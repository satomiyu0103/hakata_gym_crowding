"""混雑4段階マッピングのテスト。"""

from hakata_gym_crowding.domain.crowding import (
    LEVEL_BUSY,
    LEVEL_EMPTY,
    LEVEL_SLIGHT,
    LEVEL_VERY_BUSY,
    crowding_level,
)
from hakata_gym_crowding.domain.models import Thresholds

THRESHOLDS = Thresholds(rank1=0, rank2=15, rank3=25, rank4=30)


def test_crowding_level_empty() -> None:
    assert crowding_level(0, THRESHOLDS) == LEVEL_EMPTY
    assert crowding_level(14, THRESHOLDS) == LEVEL_EMPTY


def test_crowding_level_slight() -> None:
    assert crowding_level(15, THRESHOLDS) == LEVEL_SLIGHT
    assert crowding_level(24, THRESHOLDS) == LEVEL_SLIGHT


def test_crowding_level_busy() -> None:
    assert crowding_level(25, THRESHOLDS) == LEVEL_BUSY
    assert crowding_level(29, THRESHOLDS) == LEVEL_BUSY


def test_crowding_level_very_busy() -> None:
    assert crowding_level(30, THRESHOLDS) == LEVEL_VERY_BUSY
    assert crowding_level(100, THRESHOLDS) == LEVEL_VERY_BUSY
