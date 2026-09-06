"""ピープルカウンター JSON の取得とパース。

含まれるもの:
- PCounterFetcher — 2 つの JSON を取得してスナップショットを組み立てる

処理の流れ:
1. トレーニング室・体育館の JSON をそれぞれ GET する — 失敗時は最大3回リトライ後 RuntimeError
2. 人数・計測時刻・メンテナンスフラグを取り出す
3. メンテ中なら maintenance、計測が5分以上古いなら stale_data と判定する
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import httpx

from hakata_gym_crowding.domain.crowding import crowding_level
from hakata_gym_crowding.domain.models import (
    CrowdingSnapshot,
    PCounterPayload,
    RecordStatus,
    Thresholds,
)

TRAIN_JSON_URL = (
    "https://svc01.p-counter.jp/v4shr3svr/shinko-sports/data/hakata_train.json"
)
GYM_JSON_URL = (
    "https://svc01.p-counter.jp/v4shr3svr/shinko-sports/data/hakata_gym.json"
)
USER_AGENT = "hakata-gym-crowding/0.1 (+local RPA; polite polling)"
DEFAULT_TIMEOUT = 30.0
MAX_RETRIES = 3
STALE_SECONDS = 60 * 5


class PCounterFetcher:
    """p-counter 公開 JSON（外部サービス）を取得する。

    集まっているもの:
    - データ: HTTP クライアント（自前生成 or テスト注入）
    - 処理: fetch_snapshot（2 JSON → 1 スナップショット）

    バリデーション: JSON ルートが dict でない場合は TypeError → リトライ対象
    """

    def __init__(
        self,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        client: httpx.Client | None = None,
    ) -> None:
        self._owns_client = client is None
        self._client = client or httpx.Client(
            timeout=timeout,
            headers={"User-Agent": USER_AGENT},
        )

    def close(self) -> None:
        # 自前で作った Client だけ閉じる（テスト用の注入 Client は触らない）
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> PCounterFetcher:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def fetch_snapshot(self, now: datetime) -> CrowdingSnapshot:
        """2 JSON を取得し、1 行分のスナップショットを組み立てる。

        受け取る: 取得時刻（タイムゾーン付き推奨）
        返す: 混雑人数・ステータスを含む CrowdingSnapshot
        例外: JSON 取得失敗時 RuntimeError
        """
        train = self._fetch_payload(TRAIN_JSON_URL, section="train")
        gym = self._fetch_payload(GYM_JSON_URL, section="gym")

        status = RecordStatus.OK
        # メンテナンス中はサイト表示が止まっているため最優先で判定
        if train.maintenance or gym.maintenance:
            status = RecordStatus.MAINTENANCE
        # 計測時刻が5分以上古い場合は stale（記録は行う）
        elif self._is_stale(now, train.time_calc) or self._is_stale(now, gym.time_calc):
            status = RecordStatus.STALE_DATA

        return CrowdingSnapshot(
            recorded_at=now,
            train_count=train.count,
            train_level=crowding_level(train.count, train.thresholds),
            gym_count=gym.count,
            source_time=train.time_calc,
            status=status,
        )

    def _fetch_payload(self, url: str, *, section: str) -> PCounterPayload:
        """1 つの JSON から人数・閾値・メンテフラグを取り出す。"""
        parsed_json = self._get_json(url)
        hakata_section_json = parsed_json["hakata"][section]
        thresholds = hakata_section_json["threshold"]
        maintenance_raw = hakata_section_json.get("maintenance")
        # maintenance は "1" 文字列で来ることがある
        maintenance = str(maintenance_raw) == "1" if maintenance_raw is not None else False
        section_occupant_count = int(hakata_section_json["sum"]["area1"])
        return PCounterPayload(
            section_occupant_count,
            str(hakata_section_json["time_calc"]),
            maintenance,
            Thresholds(
                rank1=int(thresholds["rank1"]),
                rank2=int(thresholds["rank2"]),
                rank3=int(thresholds["rank3"]),
                rank4=int(thresholds["rank4"]),
            ),
        )

    def _get_json(self, url: str) -> dict[str, Any]:
        """URL から JSON を GET する。最大3回リトライ。

        受け取る: 取得先 URL
        返す: パース済み dict
        例外: 3 回失敗で RuntimeError
        """
        last_error: Exception | None = None
        # 最大3回まで JSON GET を試す
        for attempt in range(MAX_RETRIES):
            # ・成功 → dict を返す
            # ・HTTPError / ValueError / TypeError → 指数バックオフ後に再試行
            # ・3回目も失敗 → RuntimeError を投げる
            try:
                response = self._client.get(url)
                response.raise_for_status()
                parsed_response_json = response.json()
                # ルートが dict でない JSON はパースエラーとして扱う
                if not isinstance(parsed_response_json, dict):
                    msg = f"JSON ルートが dict ではありません: {url}"
                    raise TypeError(msg)
                return parsed_response_json
            except (httpx.HTTPError, ValueError, TypeError) as exc:
                last_error = exc
                # 指数バックオフ: 1秒 → 2秒 → 4秒
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2**attempt)
        msg = f"JSON 取得に失敗しました: {url}"
        raise RuntimeError(msg) from last_error

    @staticmethod
    def _is_stale(now: datetime, time_calc: str) -> bool:
        """サイトJSと同じく、計測時刻が5分以上古い場合は stale とする。

        受け取る: 現在時刻、計測時刻文字列（HH:MM:SS）
        返す: True なら古いデータ
        """
        try:
            hour, minute, second = (int(part) for part in time_calc.split(":"))
        except ValueError:
            # time_calc が壊れていれば安全側で stale とみなす
            return True

        local_now = now
        if now.tzinfo is None:
            # naive datetime は JST として扱う（Windows ローカル実行向け）
            local_now = now.replace(tzinfo=ZoneInfo("Asia/Tokyo"))
        local_now = local_now.astimezone(ZoneInfo("Asia/Tokyo")).replace(tzinfo=None)

        source_dt = local_now.replace(
            hour=hour,
            minute=minute,
            second=second,
            microsecond=0,
        )
        delta = abs((local_now - source_dt).total_seconds())
        # 日付跨ぎで誤判定しないよう ±12時間超なら日付を補正
        if delta > 12 * 3600:
            if source_dt > local_now:
                source_dt -= timedelta(days=1)
            else:
                source_dt += timedelta(days=1)
            delta = abs((local_now - source_dt).total_seconds())
        return delta >= STALE_SECONDS
