"""開館時間・休館日の判定。

含まれるもの:
- ScheduleGuard — 9:00-22:00 と休館ルールの判定
- ScheduleDecision / SkipReason — 判定結果

処理の流れ:
1. 時刻を JST に揃える
2. 9:00 より前 or 22:00 以降なら取得しない
3. 年末年始（12/28〜1/4）・第3月曜・振替火曜を順に判定
4. いずれも該当しなければ should_run=True
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from enum import StrEnum
from zoneinfo import ZoneInfo

import jpholiday


class SkipReason(StrEnum):
    OUTSIDE_HOURS = "outside_hours"
    THIRD_MONDAY = "third_monday"
    SUBSTITUTED_TUESDAY = "substituted_tuesday"
    NEW_YEAR = "new_year"


@dataclass(frozen=True)
class ScheduleDecision:
    """開館判定の結果。

    should_run: True なら混雑取得を実行する
    reason: スキップ時の理由コード（should_run=False のとき）
    """

    should_run: bool
    reason: SkipReason | None = None


class ScheduleGuard:
    """9:00-22:00 と MVP 休館日を判定する。

    バリデーション: なし（日付ライブラリ jpholiday に委譲）
    """

    OPEN_TIME = time(9, 0)
    CLOSE_TIME = time(22, 0)

    def __init__(self, timezone: str = "Asia/Tokyo") -> None:
        self._tz = ZoneInfo(timezone)

    def evaluate(self, moment: datetime | None = None) -> ScheduleDecision:
        """指定時刻が取得対象かどうかを判定する。

        受け取る: 判定時刻（省略時は現在時刻）
        返す: ScheduleDecision（should_run と reason）

        処理の流れ:
        1. JST に揃える
        2. 開館時間外 → outside_hours
        3. 年末年始 → new_year
        4. 第3月曜 → third_monday
        5. 振替火曜 → substituted_tuesday
        6. いずれも該当しなければ should_run=True
        """
        now = moment or datetime.now(tz=self._tz)
        # 引数が naive なら JST を付与、aware なら JST に揃える
        if now.tzinfo is None:
            now = now.replace(tzinfo=self._tz)
        else:
            now = now.astimezone(self._tz)

        current_time = now.time()
        # 9:00 より前、または 22:00 以降は取得しない
        if current_time < self.OPEN_TIME or current_time >= self.CLOSE_TIME:
            return ScheduleDecision(False, SkipReason.OUTSIDE_HOURS)

        today = now.date()
        # 年末年始（12/28〜1/4）は休館
        if self._is_new_year_closure(today):
            return ScheduleDecision(False, SkipReason.NEW_YEAR)

        third_monday = self._third_monday(today.year, today.month)
        # 毎月第3月曜は休館
        if today == third_monday:
            return ScheduleDecision(False, SkipReason.THIRD_MONDAY)

        # 第3月曜の振替休館（祝日だった月曜の翌火曜）
        # ・条件を満たす → 取得しない（substituted_tuesday）
        # ・満たさない → 開館として続行
        yesterday = today - timedelta(days=1)
        third_monday_of_yesterday = self._third_monday(yesterday.year, yesterday.month)
        if (
            today.weekday() == 1
            and yesterday == third_monday_of_yesterday
            and jpholiday.is_holiday(third_monday_of_yesterday)
        ):
            return ScheduleDecision(False, SkipReason.SUBSTITUTED_TUESDAY)

        return ScheduleDecision(True)

    @staticmethod
    def _is_new_year_closure(day: date) -> bool:
        """12/28 以降または 1/4 以前なら年末年始休館。"""
        # 12/28 以降は年末休館
        if day.month == 12 and day.day >= 28:
            return True
        # 1/4 までは年始休館
        return day.month == 1 and day.day <= 4

    @staticmethod
    def _third_monday(year: int, month: int) -> date:
        """指定月の第3月曜日を返す。見つからなければ ValueError。"""
        day = date(year, month, 1)
        mondays = 0
        # 月初から月末まで1日ずつ進め、3番目の月曜を探す
        while day.month == month:
            if day.weekday() == 0:
                mondays += 1
                if mondays == 3:
                    return day
            day = day.fromordinal(day.toordinal() + 1)
        msg = f"第3月曜が見つかりません: {year}-{month:02d}"
        raise ValueError(msg)
