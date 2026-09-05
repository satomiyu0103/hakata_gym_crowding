"""ピープルカウンター JSON の取得とパース。

処理の流れ:
1. トレーニング室・体育館の JSON をそれぞれ GET する
2. 人数・計測時刻・メンテナンスフラグを取り出す
3. 計測が古い場合は stale_data、メンテ中は maintenance と判定する
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
    """p-counter 公開 JSON を取得する。"""

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
        """2 JSON を取得し、1 行分のスナップショットを組み立てる。"""
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
        data = self._get_json(url)
        node = data["hakata"][section]
        thresholds = node["threshold"]
        maintenance_raw = node.get("maintenance")
        maintenance = str(maintenance_raw) == "1" if maintenance_raw is not None else False
        return PCounterPayload(
            count=int(node["sum"]["area1"]),
            time_calc=str(node["time_calc"]),
            maintenance=maintenance,
            thresholds=Thresholds(
                rank1=int(thresholds["rank1"]),
                rank2=int(thresholds["rank2"]),
                rank3=int(thresholds["rank3"]),
                rank4=int(thresholds["rank4"]),
            ),
        )

    def _get_json(self, url: str) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                response = self._client.get(url)
                response.raise_for_status()
                payload = response.json()
                if not isinstance(payload, dict):
                    msg = f"JSON ルートが dict ではありません: {url}"
                    raise TypeError(msg)
                return payload
            except (httpx.HTTPError, ValueError, TypeError) as exc:
                last_error = exc
                # 指数バックオフ: 1秒 → 2秒 → 4秒
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2**attempt)
        msg = f"JSON 取得に失敗しました: {url}"
        raise RuntimeError(msg) from last_error

    @staticmethod
    def _is_stale(now: datetime, time_calc: str) -> bool:
        """サイトJSと同じく、計測時刻が5分以上古い場合は stale とする。"""
        try:
            hour, minute, second = (int(part) for part in time_calc.split(":"))
        except ValueError:
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
