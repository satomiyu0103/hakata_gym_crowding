"""PCounterFetcher のパーステスト。"""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx

from hakata_gym_crowding.domain.models import RecordStatus
from hakata_gym_crowding.fetch.pcounter import PCounterFetcher

FIXTURES = Path(__file__).parent / "fixtures"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_fetch_snapshot_with_mock_transport() -> None:
    train = _load_fixture("hakata_train.json")
    gym = _load_fixture("hakata_gym.json")

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("hakata_train.json"):
            return httpx.Response(200, json=train)
        if request.url.path.endswith("hakata_gym.json"):
            return httpx.Response(200, json=gym)
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    now = datetime(2026, 9, 5, 17, 0, 0, tzinfo=ZoneInfo("Asia/Tokyo"))

    with PCounterFetcher(client=client) as fetcher:
        snapshot = fetcher.fetch_snapshot(now)

    assert snapshot.train_count == 25
    assert snapshot.train_level == "混雑しています"
    assert snapshot.gym_count == 58
    assert snapshot.source_time == "16:59:04"
    assert snapshot.status == RecordStatus.OK
