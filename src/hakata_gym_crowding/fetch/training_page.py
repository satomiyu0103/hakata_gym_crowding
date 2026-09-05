"""博多体育館トレーニング室ページから天気情報を取得する。

含まれるもの:
- TrainingPageFetcher — HTML を GET して天気をパース
- parse_weather_html — テスト用の純関数パーサ

処理の流れ:
1. トレーニング室ページを HTTP GET — 失敗時は最大3回リトライ後 RuntimeError
2. HTML から天気アイコン・気温・風・降水確率を抽出
3. 取得失敗時は cli 側で混雑のみ継続（ここでは例外を投げる）
"""

from __future__ import annotations

import re
import time

import httpx

from hakata_gym_crowding.domain.models import WeatherSnapshot

TRAINING_PAGE_URL = "https://ssk-hakata-gym.com/training/"
USER_AGENT = "hakata-gym-crowding/0.1 (+local RPA; polite polling)"
DEFAULT_TIMEOUT = 30.0
MAX_RETRIES = 3

# OpenWeatherMap 系アイコンコード → 日本語ラベル（サイトの weather_icon/*.png 名）
WEATHER_ICON_LABELS: dict[str, str] = {
    "01d": "晴れ",
    "01n": "晴れ",
    "02d": "薄曇り",
    "02n": "薄曇り",
    "03d": "曇り",
    "03n": "曇り",
    "04d": "曇り",
    "04n": "曇り",
    "09d": "にわか雨",
    "09n": "にわか雨",
    "10d": "雨",
    "10n": "雨",
    "11d": "雷雨",
    "11n": "雷雨",
    "13d": "雪",
    "13n": "雪",
    "50d": "霧",
    "50n": "霧",
}


class TrainingPageFetcher:
    """トレーニング室ページ HTML から当日天気を取得する。

    集まっているもの:
    - データ: HTTP クライアント
    - 処理: fetch_weather

    バリデーション: HTML 構造変更時は各フィールドが None になる
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
        # テストで注入した Client は呼び出し側が閉じる
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> TrainingPageFetcher:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def fetch_weather(self) -> WeatherSnapshot:
        """ページ HTML を取得し、当日天気ブロックをパースする。

        受け取る: なし
        返す: WeatherSnapshot
        例外: HTML 取得失敗時 RuntimeError
        """
        html = self._get_html(TRAINING_PAGE_URL)
        return parse_weather_html(html)

    def _get_html(self, url: str) -> str:
        """HTTP GET で HTML を取得する。失敗時は指数バックオフでリトライ。

        受け取る: 取得先 URL
        返す: HTML 文字列
        例外: 3 回失敗で RuntimeError
        """
        last_error: Exception | None = None
        # 最大3回まで GET を試す
        for attempt in range(MAX_RETRIES):
            # ・成功 → HTML 文字列を返す
            # ・HTTPError → 指数バックオフ後に再試行
            # ・3回目も失敗 → RuntimeError
            try:
                response = self._client.get(url)
                response.raise_for_status()
                return response.text
            except httpx.HTTPError as exc:
                last_error = exc
                # 最終試行でなければ 1秒→2秒→4秒 待って再試行
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2**attempt)
        msg = f"HTML 取得に失敗しました: {url}"
        raise RuntimeError(msg) from last_error


def parse_weather_html(html: str) -> WeatherSnapshot:
    """HTML 文字列から当日天気を抽出する（テスト・再利用用の純関数）。

    受け取る: ページ HTML 全文
    返す: パース結果（欠損フィールドは None）
    """
    return WeatherSnapshot(
        weather_label=_parse_weather_label(html),
        temp_high_c=_parse_span_int(html, "max"),
        temp_low_c=_parse_span_int(html, "min"),
        wind_speed_mps=_parse_span_int(html, "wind"),
        wind_direction=_parse_wind_direction(html),
        precipitation_pct=_parse_span_int(html, "desc"),
    )


def _parse_weather_label(html: str) -> str | None:
    """今日のアイコン画像ファイル名から天候ラベルを返す。"""
    match = re.search(
        r"todayIcon.*?weather_icon/([0-9a-z]+)\.png",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return None
    icon_code = match.group(1).lower()
    # 未知のアイコンコードは空欄のまま（ラベル変換表に無い場合）
    return WEATHER_ICON_LABELS.get(icon_code)


def _parse_span_int(html: str, class_name: str) -> int | None:
    """todayInfo 内の <span class="bold {class_name}"> から整数を取り出す。"""
    pattern = rf'<span class="bold {class_name}">(\d+)</span>'
    match = re.search(pattern, html)
    # HTML 構造変更や欠損時は None（空セルになる）
    if not match:
        return None
    return int(match.group(1))


def _parse_wind_direction(html: str) -> str | None:
    """風向ラベル（東など）を返す。"""
    match = re.search(
        r'<div class="infT bold floatL dig">風向</div>\s*'
        r'<div class="infD floatL"><span class="bold dig">([^<]+)</span>',
        html,
    )
    if not match:
        return None
    return match.group(1).strip()
