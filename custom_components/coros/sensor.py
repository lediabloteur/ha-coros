"""Sensor platform for COROS."""
from datetime import datetime, timedelta
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
        CorosUpcomingWorkoutsSensor(coordinator, entry),
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

class CorosUpcomingWorkoutsSensor(CorosBaseSensor):
    """Sensor for upcoming COROS workouts."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "upcoming_workouts", "Planning Entraînements", "mdi:calendar-check")

    @property
    def native_value(self):
        schedule = self.coordinator.data.get("schedule", [])
        today_str = datetime.now().strftime("%Y%m%d")
        upcoming = [s for s in schedule if str(s.get("date")) >= today_str]
        if upcoming:
            return upcoming[0].get("name", "Séance programmée")
        return "Aucune séance programmée"

    @property
    def extra_state_attributes(self):
        schedule = self.coordinator.data.get("schedule", [])
        today_str = datetime.now().strftime("%Y%m%d")
        
        days_fr = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
        
        formatted_workouts = []
        for s in schedule:
            d_str = str(s.get("date") or "")
            if len(d_str) == 8:
                try:
                    dt = datetime.strptime(d_str, "%Y%m%d")
                    day_name = days_fr[dt.weekday()]
                    day_num = dt.day
                    month_num = dt.month
                    
                    if d_str == today_str:
                        date_label = f"Aujourd’hui ({day_name} {day_num:02d}/{month_num:02d})"
                    elif d_str == (datetime.now() + timedelta(days=1)).strftime("%Y%m%d"):
                        date_label = f"Demain ({day_name} {day_num:02d}/{month_num:02d})"
                    else:
                        date_label = f"{day_name} {day_num:02d}/{month_num:02d}"
                        
                    formatted_workouts.append({
                        "date": date_label,
                        "raw_date": d_str,
                        "name": s.get("name"),
                        "detail": s.get("overview"),
                        "color": s.get("color", "#00b0ff"),
                        "icon": s.get("icon", "mdi:run-fast"),
                        "sport_type": s.get("sport_type", 1)
                    })
                except Exception:
                    pass

        upcoming_list = [w for w in formatted_workouts if w["raw_date"] >= today_str]
        return {
            "workouts": upcoming_list[:10],
            "total_upcoming": len(upcoming_list)
        }
