"""TrainingPageFetcher / parse_weather_html のテスト。"""

from pathlib import Path

import httpx

from hakata_gym_crowding.fetch.training_page import (
    TrainingPageFetcher,
    parse_weather_html,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_weather_html_from_fixture() -> None:
    html = (FIXTURES / "training_page.html").read_text(encoding="utf-8")
    weather = parse_weather_html(html)

    assert weather.weather_label == "曇り"
    assert weather.temp_high_c == 29
    assert weather.temp_low_c == 28
    assert weather.wind_speed_mps == 5
    assert weather.wind_direction == "東"
    assert weather.precipitation_pct == 20


def test_fetch_weather_with_mock_transport() -> None:
    html = (FIXTURES / "training_page.html").read_text(encoding="utf-8")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=html)

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)

    with TrainingPageFetcher(client=client) as fetcher:
        weather = fetcher.fetch_weather()

    assert weather.precipitation_pct == 20
