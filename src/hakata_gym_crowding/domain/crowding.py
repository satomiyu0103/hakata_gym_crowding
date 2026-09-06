"""人数から混雑4段階ラベルを算出する。

含まれるもの:
- crowding_level — 人数と閾値から日本語ラベルを返す

処理の流れ:
1. rank4 以上 → 大混雑
2. rank3 以上 → 混雑
3. rank2 以上 → やや混雑
4. それ以外 → 空いている
"""

from __future__ import annotations

from hakata_gym_crowding.domain.models import Thresholds

LEVEL_EMPTY = "空いています"
LEVEL_SLIGHT = "やや混雑しています"
LEVEL_BUSY = "混雑しています"
LEVEL_VERY_BUSY = "大混雑しています"


def crowding_level(occupant_count: int, thresholds: Thresholds) -> str:
    """サイトJSと同じ rank 判定で混雑ラベルを返す。

    受け取る: 人数、閾値4段階
    返す: 日本語の混雑ラベル文字列
    """
    # 人数が rank4 以上なら大混雑（サイト表示と同じ閾値）
    if occupant_count >= thresholds.rank4:
        return LEVEL_VERY_BUSY
    # rank3 以上なら混雑
    if occupant_count >= thresholds.rank3:
        return LEVEL_BUSY
    # rank2 以上ならやや混雑
    if occupant_count >= thresholds.rank2:
        return LEVEL_SLIGHT
    # それ以外は空いている
    return LEVEL_EMPTY
