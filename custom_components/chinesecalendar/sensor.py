"""Platform for sensor integration."""

from datetime import timedelta, datetime
from homeassistant.core import callback
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_point_in_time
import homeassistant.util.dt as dt_util


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    sensor = ChineseCalendarSensor(hass)
    async_track_point_in_time(
        hass, sensor.point_in_time_listener, sensor.get_next_interval()
    )
    async_add_entities([sensor], True)


class ChineseCalendarSensor(Entity):
    def __init__(self, hass):
        self._data = {}
        self.hass = hass
        self.update_internal_state()

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def name(self):
        return "chinese_calendar"

    @property
    def state(self):
        return self._data.get("is_workday") == True and "Workday" or "Holiday"

    @property
    def icon(self):
        return "mdi:calendar"

    @property
    def device_state_attributes(self):
        return self._data

    def update_internal_state(self):
        from chinese_calendar import is_workday, get_holiday_detail, is_in_lieu

        now = dt_util.now()
        on_holiday, holiday_name = get_holiday_detail(now)
        self._data = {
            "is_workday": is_workday(now),
            "is_holiday": on_holiday,
            "holiday_name": holiday_name,
            "is_in_lieu": is_in_lieu(now),
        }

    def get_next_interval(self):
        return dt_util.start_of_local_day(dt_util.now() + timedelta(days=1))

    @callback
    def point_in_time_listener(self, *args, **kwargs):
        self.update_internal_state()
        self.async_schedule_update_ha_state()

        async_track_point_in_time(
            self.hass, self.point_in_time_listener, self.get_next_interval()
        )
