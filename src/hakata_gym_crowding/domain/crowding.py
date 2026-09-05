"""人数から混雑4段階ラベルを算出する。"""

from __future__ import annotations

from hakata_gym_crowding.domain.models import Thresholds

LEVEL_EMPTY = "空いています"
LEVEL_SLIGHT = "やや混雑しています"
LEVEL_BUSY = "混雑しています"
LEVEL_VERY_BUSY = "大混雑しています"


def crowding_level(count: int, thresholds: Thresholds) -> str:
    """サイトJSと同じ rank 判定で混雑ラベルを返す。"""
    if count >= thresholds.rank4:
        return LEVEL_VERY_BUSY
    if count >= thresholds.rank3:
        return LEVEL_BUSY
    if count >= thresholds.rank2:
        return LEVEL_SLIGHT
    return LEVEL_EMPTY
