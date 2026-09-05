"""ScheduleGuard のテスト。"""

from datetime import datetime
from zoneinfo import ZoneInfo

import jpholiday

from hakata_gym_crowding.schedule.guard import ScheduleGuard, SkipReason

JST = ZoneInfo("Asia/Tokyo")


def _dt(year: int, month: int, day: int, hour: int, minute: int = 0) -> datetime:
    return datetime(year, month, day, hour, minute, tzinfo=JST)


def test_outside_hours_before_open() -> None:
    guard = ScheduleGuard()
    decision = guard.evaluate(_dt(2026, 9, 5, 8, 59))
    assert decision.should_run is False
    assert decision.reason == SkipReason.OUTSIDE_HOURS


def test_outside_hours_after_close() -> None:
    guard = ScheduleGuard()
    decision = guard.evaluate(_dt(2026, 9, 5, 22, 0))
    assert decision.should_run is False
    assert decision.reason == SkipReason.OUTSIDE_HOURS


def test_open_hours_weekday() -> None:
    guard = ScheduleGuard()
    decision = guard.evaluate(_dt(2026, 9, 5, 10, 0))
    assert decision.should_run is True


def test_new_year_closure() -> None:
    guard = ScheduleGuard()
    decision = guard.evaluate(_dt(2026, 12, 28, 10, 0))
    assert decision.should_run is False
    assert decision.reason == SkipReason.NEW_YEAR


def test_third_monday_closure() -> None:
    guard = ScheduleGuard()
    decision = guard.evaluate(_dt(2026, 1, 19, 10, 0))
    assert decision.should_run is False
    assert decision.reason == SkipReason.THIRD_MONDAY


def test_substituted_tuesday_when_third_monday_is_holiday() -> None:
    third_monday = datetime(2026, 9, 21, 10, 0, tzinfo=JST).date()
    assert third_monday.weekday() == 0
    assert jpholiday.is_holiday(third_monday)

    guard = ScheduleGuard()
    tuesday = guard.evaluate(_dt(2026, 9, 22, 10, 0))
    assert tuesday.should_run is False
    assert tuesday.reason == SkipReason.SUBSTITUTED_TUESDAY


def test_first_tuesday_of_month_is_not_substituted_closure() -> None:
    guard = ScheduleGuard()
    decision = guard.evaluate(_dt(2022, 3, 1, 10, 0))
    assert decision.should_run is True


def test_third_monday_stays_in_requested_month() -> None:
    for year in range(2020, 2031):
        for month in range(1, 13):
            third_monday = ScheduleGuard._third_monday(year, month)
            assert third_monday.month == month
