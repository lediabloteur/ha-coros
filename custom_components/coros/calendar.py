"""Calendar platform for COROS Training Schedule."""
from datetime import datetime, date, timedelta
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

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
        now = datetime.now()
        upcoming = [e for e in events if e.end >= now]
        if upcoming:
            return upcoming[0]
        return None

    def _get_events(self) -> list[CalendarEvent]:
        """Convert schedule data into CalendarEvent list."""
        events = []
        programs = self.coordinator.data.get("schedule", [])
        for p in programs:
            raw_date = str(p.get("date") or "")
            if len(raw_date) == 8:
                try:
                    dt = datetime.strptime(raw_date, "%Y%m%d")
                    start_dt = dt.replace(hour=18, minute=30)
                    end_dt = dt.replace(hour=20, minute=0)
                    summary = p.get("name") or "Entraînement COROS"
                    description = p.get("overview") or p.get("description") or ""

                    events.append(CalendarEvent(
                        start=start_dt,
                        end=end_dt,
                        summary=summary,
                        description=description,
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
        return [e for e in events if start_date <= e.end and e.start <= end_date]
