"""Calendar platform for COROS Training Schedule."""
from datetime import datetime, timedelta, time
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
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

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for COROS Training Hub."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.user_id or self.coordinator.email)},
            name="COROS Training Hub",
            manufacturer="COROS",
            model="Training Hub & Health",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://training.coros.com",
        )

    def _get_events(self) -> list[CalendarEvent]:
        events = []
        schedule = self.coordinator.data.get("schedule", [])
        tz = dt_util.DEFAULT_TIME_ZONE

        for s in schedule:
            date_str = str(s.get("date") or "")
            name = s.get("name") or "Entraînement COROS"
            overview = s.get("overview") or ""

            if len(date_str) == 8:
                try:
                    d = datetime.strptime(date_str, "%Y%m%d").date()
                    start_dt = datetime.combine(d, time.min, tzinfo=tz)
                    end_dt = datetime.combine(d + timedelta(days=1), time.min, tzinfo=tz)
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

    @property
    def event(self) -> CalendarEvent | None:
        now = dt_util.now()
        for e in self._get_events():
            if e.end >= now:
                return e
        return None

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        events = self._get_events()
        return [e for e in events if start_date <= e.end and e.start <= end_date]
