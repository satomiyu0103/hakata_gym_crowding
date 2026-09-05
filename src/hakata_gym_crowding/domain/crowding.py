"""人数から混雑4段階ラベルを算出する。"""

from __future__ import annotations

from hakata_gym_crowding.domain.models import Thresholds

LEVEL_EMPTY = "空いています"
LEVEL_SLIGHT = "やや混雑しています"
LEVEL_BUSY = "混雑しています"
LEVEL_VERY_BUSY = "大混雑しています"


def crowding_level(count: int, thresholds: Thresholds) -> str:
    """サイトJSと同じ rank 判定で混雑ラベルを返す。"""
    # 人数が rank4 以上なら大混雑（サイト表示と同じ閾値）
    if count >= thresholds.rank4:
        return LEVEL_VERY_BUSY
    # rank3 以上なら混雑
    if count >= thresholds.rank3:
        return LEVEL_BUSY
    # rank2 以上ならやや混雑
    if count >= thresholds.rank2:
        return LEVEL_SLIGHT
    # それ以外は空いている
    return LEVEL_EMPTY
