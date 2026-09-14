"""Sensor platform for COROS."""
from homeassistant.components.sensor import SensorEntity
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
    """Set up COROS sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        CorosRunningMonthSensor(coordinator, entry),
        CorosVeloMonthSensor(coordinator, entry),
        CorosPpgMonthSensor(coordinator, entry),
        CorosMonthTimeSensor(coordinator, entry),
        CorosMonthCountSensor(coordinator, entry),
        CorosTrainingLoadSensor(coordinator, entry),
    ]
    async_add_entities(entities)

class CorosBaseSensor(CoordinatorEntity, SensorEntity):
    """Base sensor for COROS."""

    def __init__(self, coordinator, entry, key, name, icon=None, unit=None):
        super().__init__(coordinator)
        self._key = key
        self._attr_name = f"COROS {name}"
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = unit

class CorosRunningMonthSensor(CorosBaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "running_month_km", "Course (Mois)", "mdi:run-fast", "km")

    @property
    def native_value(self):
        return self.coordinator.data.get("monthly_stats", {}).get("running_km", 0)

    @property
    def extra_state_attributes(self):
        st = self.coordinator.data.get("monthly_stats", {})
        return {
            "count": st.get("running_count", 0),
            "time_str": st.get("running_time_str", "0 min")
        }

class CorosVeloMonthSensor(CorosBaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "velo_month_km", "Vélo & Gravel (Mois)", "mdi:bicycle", "km")

    @property
    def native_value(self):
        return self.coordinator.data.get("monthly_stats", {}).get("velo_km", 0)

    @property
    def extra_state_attributes(self):
        st = self.coordinator.data.get("monthly_stats", {})
        return {
            "count": st.get("velo_count", 0),
            "time_str": st.get("velo_time_str", "0 min")
        }

class CorosPpgMonthSensor(CorosBaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "ppg_month_count", "PPG & Renfo (Mois)", "mdi:weight-lifter", "séances")

    @property
    def native_value(self):
        return self.coordinator.data.get("monthly_stats", {}).get("ppg_count", 0)

    @property
    def extra_state_attributes(self):
        st = self.coordinator.data.get("monthly_stats", {})
        return {"time_str": st.get("ppg_time_str", "0 min")}

class CorosMonthTimeSensor(CorosBaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "month_total_time", "Temps Total (Mois)", "mdi:timer-outline")

    @property
    def native_value(self):
        return self.coordinator.data.get("monthly_stats", {}).get("total_time_str", "0h 00")

class CorosMonthCountSensor(CorosBaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "month_total_count", "Séances Réalisées (Mois)", "mdi:fire", "séances")

    @property
    def native_value(self):
        return self.coordinator.data.get("monthly_stats", {}).get("total_count", 0)

class CorosTrainingLoadSensor(CorosBaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "month_training_load", "Charge Entraînement (Mois)", "mdi:lightning-bolt", "TL")

    @property
    def native_value(self):
        return self.coordinator.data.get("monthly_stats", {}).get("training_load", 0)
