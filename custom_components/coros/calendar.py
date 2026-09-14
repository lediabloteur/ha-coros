"""Calendar platform for COROS Training Schedule."""
import re
from datetime import datetime, date, timedelta
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
        super().__init__(coordinator)
        self._attr_name = "Planning Entraînements COROS"
        self._attr_unique_id = f"{entry.entry_id}_calendar"
        self._attr_icon = "mdi:calendar-clock"

    def _get_events(self) -> list[CalendarEvent]:
        events = []
        programs = self.coordinator.data.get("schedule", [])

        for p in programs:
            name = p.get("name") or "Entraînement COROS"
            overview = p.get("overview") or p.get("description") or ""

            # Extract date (YYYYMMDD)
            date_str = str(p.get("startDay") or p.get("date") or "")
            if not date_str or len(date_str) != 8:
                m = re.search(r'(\d{8})', name)
                if m:
                    date_str = m.group(1)

            if len(date_str) == 8:
                try:
                    d = datetime.strptime(date_str, "%Y%m%d").date()
                    events.append(CalendarEvent(
                        start=d,
                        end=d + timedelta(days=1),
                        summary=name,
                        description=overview,
                        location="Poitiers"
                    ))
                except Exception:
                    pass

        return sorted(events, key=lambda x: x.start)

    @property
    def event(self) -> CalendarEvent | None:
        today = dt_util.now().date()
        for e in self._get_events():
            if e.end >= today:
                return e
        return None

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        events = self._get_events()
        start_d = start_date.date()
        end_d = end_date.date()
        return [e for e in events if start_d <= e.end and e.start <= end_d]
