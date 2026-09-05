"""開館時間・休館日の判定。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
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
    should_run: bool
    reason: SkipReason | None = None


class ScheduleGuard:
    """9:00-22:00 と MVP 休館日を判定する。"""

    OPEN_TIME = time(9, 0)
    CLOSE_TIME = time(22, 0)

    def __init__(self, timezone: str = "Asia/Tokyo") -> None:
        self._tz = ZoneInfo(timezone)

    def evaluate(self, moment: datetime | None = None) -> ScheduleDecision:
        now = moment or datetime.now(tz=self._tz)
        if now.tzinfo is None:
            now = now.replace(tzinfo=self._tz)
        else:
            now = now.astimezone(self._tz)

        current_time = now.time()
        if current_time < self.OPEN_TIME or current_time >= self.CLOSE_TIME:
            return ScheduleDecision(False, SkipReason.OUTSIDE_HOURS)

        today = now.date()
        if self._is_new_year_closure(today):
            return ScheduleDecision(False, SkipReason.NEW_YEAR)

        third_monday = self._third_monday(today.year, today.month)
        if today == third_monday:
            return ScheduleDecision(False, SkipReason.THIRD_MONDAY)

        if today == third_monday.fromordinal(third_monday.toordinal() + 1):
            if jpholiday.is_holiday(third_monday):
                return ScheduleDecision(False, SkipReason.SUBSTITUTED_TUESDAY)

        return ScheduleDecision(True)

    @staticmethod
    def _is_new_year_closure(day: date) -> bool:
        if day.month == 12 and day.day >= 28:
            return True
        return day.month == 1 and day.day <= 4

    @staticmethod
    def _third_monday(year: int, month: int) -> date:
        day = date(year, month, 1)
        mondays = 0
        while True:
            if day.weekday() == 0:
                mondays += 1
                if mondays == 3:
                    return day
            day = day.fromordinal(day.toordinal() + 1)
