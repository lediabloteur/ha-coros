"""Image platform for COROS activity route maps."""
from datetime import datetime
import logging

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import CorosDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up COROS image entities."""
    coordinator: CorosDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        CorosActivityMapImage(
            coordinator,
            entry,
            key="derniere_activite_carte",
            name="COROS Carte Dernière Activité",
            data_key="latest_activity",
        ),
        CorosActivityMapImage(
            coordinator,
            entry,
            key="derniere_course_carte",
            name="COROS Carte Dernière Course",
            data_key="latest_run",
        ),
        CorosActivityMapImage(
            coordinator,
            entry,
            key="derniere_sortie_velo_carte",
            name="COROS Carte Dernière Sortie Vélo",
            data_key="latest_bike",
        ),
    ]
    async_add_entities(entities)


class CorosActivityMapImage(CoordinatorEntity, ImageEntity):
    """Representation of a COROS activity map image."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: CorosDataUpdateCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
        data_key: str,
    ) -> None:
        """Initialize the image entity."""
        super().__init__(coordinator)
        ImageEntity.__init__(self, coordinator.hass)
        self._entry = entry
        self._key = key
        self._attr_name = name
        self._data_key = data_key
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self.entity_id = f"image.coros_{key}"

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

    @property
    def image_url(self) -> str | None:
        """Return the URL of the image to display."""
        act = self.coordinator.data.get(self._data_key)
        if act and isinstance(act, dict):
            return act.get("map_url")
        return None

    @property
    def image_last_updated(self) -> datetime | None:
        """Return when the image was last updated."""
        act = self.coordinator.data.get(self._data_key)
        if act and isinstance(act, dict):
            start_time = act.get("start_time")
            if start_time:
                try:
                    return datetime.fromisoformat(start_time)
                except Exception:
                    pass
        return self.coordinator.last_update_success_time
