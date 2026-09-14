"""Calendar platform for COROS Training Schedule."""
import re
from datetime import datetime, timedelta, timezone
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import homeassistant.util.dt as dt_util

from .const import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up COROS calendar entity."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([CorosCalendarEntity(coordinator, entry)])

class CorosCalendarEntity(CoordinatorEntity, CalendarEntity):
    """Representation of a COROS Training Schedule Calendar."""

    def __init__(self, coordinator, entry) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_name = "Planning Entraînements COROS"
        self._attr_unique_id = f"{entry.entry_id}_calendar"
        self._attr_icon = "mdi:calendar-clock"

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        events = self._get_events()
        now = dt_util.now()
        upcoming = [e for e in events if e.end >= now]
        if upcoming:
            return upcoming[0]
        return None

    def _get_events(self) -> list[CalendarEvent]:
        """Convert schedule data into CalendarEvent list."""
        events = []
        programs = self.coordinator.data.get("schedule", [])
        local_tz = dt_util.get_default_time_zone()

        for p in programs:
            name = p.get("name") or "Entraînement COROS"
            overview = p.get("overview") or p.get("description") or ""

            # Extract date (YYYYMMDD) from name or startDay or date
            date_str = str(p.get("startDay") or p.get("date") or "")
            if not date_str or len(date_str) != 8:
                m = re.search(r'(\d{8})', name)
                if m:
                    date_str = m.group(1)

            if len(date_str) == 8:
                try:
                    dt = datetime.strptime(date_str, "%Y%m%d").replace(tzinfo=local_tz)
                    start_dt = dt.replace(hour=18, minute=30)
                    end_dt = dt.replace(hour=20, minute=0)

                    events.append(CalendarEvent(
                        start=start_dt,
                        end=end_dt,
                        summary=name,
                        description=overview,
                        location="Poitiers"
                    ))
                except Exception:
                    pass

        return sorted(events, key=lambda x: x.start)

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        events = self._get_events()
        start_tz = start_date if start_date.tzinfo else start_date.replace(tzinfo=dt_util.get_default_time_zone())
        end_tz = end_date if end_date.tzinfo else end_date.replace(tzinfo=dt_util.get_default_time_zone())
        return [e for e in events if start_tz <= e.end and e.start <= end_tz]
