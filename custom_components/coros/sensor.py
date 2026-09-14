"""Sensor platform for COROS Training Hub & Health metrics."""
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import CorosDataUpdateCoordinator

@dataclass(frozen=True, kw_only=True)
class CorosSensorEntityDescription(SensorEntityDescription):
    """Describes COROS sensor entity."""

    value_fn: Callable[[dict[str, Any]], Any]
    attrs_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None
    entity_id_override: str | None = None

def _get_upcoming_workouts_value(data: dict[str, Any]) -> str:
    schedule = data.get("schedule", [])
    today_str = datetime.now().strftime("%Y%m%d")
    upcoming = [s for s in schedule if str(s.get("date", "")) >= today_str]
    if upcoming:
        return upcoming[0].get("name", "Séance programmée")
    return "Aucune séance programmée"

def _get_upcoming_workouts_attrs(data: dict[str, Any]) -> dict[str, Any]:
    schedule = data.get("schedule", [])
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
                    date_label = f"Aujourd'hui ({day_name} {day_num:02d}/{month_num:02d})"
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

SENSOR_DESCRIPTIONS: tuple[CorosSensorEntityDescription, ...] = (
    # --- Performance & Prédictions de Course (EvoLab) ---
    CorosSensorEntityDescription(
        key="vo2max",
        name="COROS VO2max",
        native_unit_of_measurement="ml/kg/min",
        icon="mdi:lungs",
        state_class=SensorStateClass.MEASUREMENT,
        entity_id_override="sensor.coros_vo2max",
        value_fn=lambda d: d.get("fitness", {}).get("vo2max"),
    ),
    CorosSensorEntityDescription(
        key="running_level",
        name="COROS Niveau de Course",
        native_unit_of_measurement="/100",
        icon="mdi:medal",
        state_class=SensorStateClass.MEASUREMENT,
        entity_id_override="sensor.coros_running_level",
        value_fn=lambda d: d.get("fitness", {}).get("running_level"),
    ),
    CorosSensorEntityDescription(
        key="threshold_pace",
        name="COROS Allure Seuil",
        icon="mdi:speedometer",
        entity_id_override="sensor.coros_threshold_pace",
        value_fn=lambda d: d.get("fitness", {}).get("threshold_pace"),
    ),
    CorosSensorEntityDescription(
        key="prediction_5k",
        name="COROS Prédiction 5 km",
        icon="mdi:timer-sand-complete",
        entity_id_override="sensor.coros_prediction_5k",
        value_fn=lambda d: d.get("fitness", {}).get("prediction_5k"),
        attrs_fn=lambda d: {
            "pace": d.get("fitness", {}).get("pace_5k", "0:00 /km"),
            "distance": "5 km"
        },
    ),
    CorosSensorEntityDescription(
        key="prediction_10k",
        name="COROS Prédiction 10 km",
        icon="mdi:timer-sand-complete",
        entity_id_override="sensor.coros_prediction_10k",
        value_fn=lambda d: d.get("fitness", {}).get("prediction_10k"),
        attrs_fn=lambda d: {
            "pace": d.get("fitness", {}).get("pace_10k", "0:00 /km"),
            "distance": "10 km"
        },
    ),
    CorosSensorEntityDescription(
        key="prediction_semi",
        name="COROS Prédiction Semi-Marathon",
        icon="mdi:timer-sand-complete",
        entity_id_override="sensor.coros_prediction_semi",
        value_fn=lambda d: d.get("fitness", {}).get("prediction_semi"),
        attrs_fn=lambda d: {
            "pace": d.get("fitness", {}).get("pace_semi", "0:00 /km"),
            "distance": "21.1 km"
        },
    ),
    CorosSensorEntityDescription(
        key="prediction_marathon",
        name="COROS Prédiction Marathon",
        icon="mdi:timer-sand-complete",
        entity_id_override="sensor.coros_prediction_marathon",
        value_fn=lambda d: d.get("fitness", {}).get("prediction_marathon"),
        attrs_fn=lambda d: {
            "pace": d.get("fitness", {}).get("pace_marathon", "0:00 /km"),
            "distance": "42.2 km"
        },
    ),

    # --- Charge d'entraînement & Fatigue ---
    CorosSensorEntityDescription(
        key="training_load_status",
        name="COROS Évaluation Charge d'entraînement",
        icon="mdi:gauge",
        entity_id_override="sensor.coros_training_load_status",
        value_fn=lambda d: d.get("training_status", {}).get("status"),
        attrs_fn=lambda d: {
            "load_ratio": d.get("training_status", {}).get("load_ratio"),
            "short_term_load": d.get("training_status", {}).get("short_term_load"),
            "long_term_load": d.get("training_status", {}).get("long_term_load"),
            "month_total_load": d.get("monthly_stats", {}).get("training_load", 0),
        },
    ),
    CorosSensorEntityDescription(
        key="short_term_load",
        name="COROS Charge Court Terme (Fatigue)",
        icon="mdi:chart-timeline-variant",
        state_class=SensorStateClass.MEASUREMENT,
        entity_id_override="sensor.coros_short_term_load",
        value_fn=lambda d: d.get("training_status", {}).get("short_term_load"),
    ),
    CorosSensorEntityDescription(
        key="long_term_load",
        name="COROS Charge Long Terme (Fitness)",
        icon="mdi:trending-up",
        state_class=SensorStateClass.MEASUREMENT,
        entity_id_override="sensor.coros_long_term_load",
        value_fn=lambda d: d.get("training_status", {}).get("long_term_load"),
    ),
    CorosSensorEntityDescription(
        key="load_ratio",
        name="COROS Ratio de Charge",
        icon="mdi:scale-balance",
        state_class=SensorStateClass.MEASUREMENT,
        entity_id_override="sensor.coros_load_ratio",
        value_fn=lambda d: d.get("training_status", {}).get("load_ratio"),
    ),

    # --- Récupération & Sommeil & Santé ---
    CorosSensorEntityDescription(
        key="recovery",
        name="COROS Niveau de Récupération",
        native_unit_of_measurement="%",
        icon="mdi:battery-charging-90",
        state_class=SensorStateClass.MEASUREMENT,
        entity_id_override="sensor.coros_recovery",
        value_fn=lambda d: d.get("recovery", {}).get("recovery_percent"),
        attrs_fn=lambda d: {
            "level": d.get("recovery", {}).get("recovery_level"),
            "estimated_full_recovery": d.get("recovery", {}).get("recovery_time"),
        },
    ),
    CorosSensorEntityDescription(
        key="recovery_time",
        name="COROS Temps Récupération Complète",
        icon="mdi:clock-check-outline",
        entity_id_override="sensor.coros_recovery_time",
        value_fn=lambda d: d.get("recovery", {}).get("recovery_time"),
    ),
    CorosSensorEntityDescription(
        key="fc_repos",
        name="COROS Fréquence Cardiaque au Repos",
        native_unit_of_measurement="bpm",
        icon="mdi:heart-pulse",
        state_class=SensorStateClass.MEASUREMENT,
        entity_id_override="sensor.coros_fc_repos",
        value_fn=lambda d: d.get("health", {}).get("resting_heart_rate"),
    ),
    CorosSensorEntityDescription(
        key="vfc",
        name="COROS Variabilité Fréquence Cardiaque (VFC)",
        native_unit_of_measurement="ms",
        icon="mdi:heart-flash",
        state_class=SensorStateClass.MEASUREMENT,
        entity_id_override="sensor.coros_vfc",
        value_fn=lambda d: d.get("health", {}).get("hrv_avg"),
        attrs_fn=lambda d: {
            "status": d.get("health", {}).get("hrv_status"),
            "baseline": d.get("health", {}).get("hrv_baseline"),
            "range": d.get("health", {}).get("hrv_range"),
        },
    ),
    CorosSensorEntityDescription(
        key="sommeil_duree",
        name="COROS Sommeil (Dernière nuit)",
        icon="mdi:bed-clock",
        entity_id_override="sensor.coros_sommeil_duree",
        value_fn=lambda d: d.get("sleep", {}).get("duration"),
        attrs_fn=lambda d: {
            "score": d.get("sleep", {}).get("score"),
            "deep_ratio": f"{d.get('sleep', {}).get('deep_ratio', 0)}%",
            "light_ratio": f"{d.get('sleep', {}).get('light_ratio', 0)}%",
            "rem_ratio": f"{d.get('sleep', {}).get('rem_ratio', 0)}%",
            "awake_ratio": f"{d.get('sleep', {}).get('awake_ratio', 0)}%",
            "awake_time": d.get("sleep", {}).get("awake_time"),
            "window": d.get("sleep", {}).get("window"),
        },
    ),
    CorosSensorEntityDescription(
        key="sommeil_score",
        name="COROS Score de Sommeil",
        native_unit_of_measurement="/100",
        icon="mdi:star",
        state_class=SensorStateClass.MEASUREMENT,
        entity_id_override="sensor.coros_sommeil_score",
        value_fn=lambda d: d.get("sleep", {}).get("score"),
    ),
    CorosSensorEntityDescription(
        key="sommeil_profond",
        name="COROS Sommeil Profond",
        native_unit_of_measurement="%",
        icon="mdi:power-sleep",
        state_class=SensorStateClass.MEASUREMENT,
        entity_id_override="sensor.coros_sommeil_profond",
        value_fn=lambda d: d.get("sleep", {}).get("deep_ratio"),
    ),
    CorosSensorEntityDescription(
        key="sommeil_leger",
        name="COROS Sommeil Léger",
        native_unit_of_measurement="%",
        icon="mdi:weather-night",
        state_class=SensorStateClass.MEASUREMENT,
        entity_id_override="sensor.coros_sommeil_leger",
        value_fn=lambda d: d.get("sleep", {}).get("light_ratio"),
    ),
    CorosSensorEntityDescription(
        key="sommeil_rem",
        name="COROS Sommeil Paradoxal (REM)",
        native_unit_of_measurement="%",
        icon="mdi:brain",
        state_class=SensorStateClass.MEASUREMENT,
        entity_id_override="sensor.coros_sommeil_rem",
        value_fn=lambda d: d.get("sleep", {}).get("rem_ratio"),
    ),

    # --- Activités & Bilan du Mois ---
    CorosSensorEntityDescription(
        key="running_month_km",
        name="COROS Course (Mois)",
        native_unit_of_measurement="km",
        icon="mdi:run-fast",
        state_class=SensorStateClass.TOTAL,
        entity_id_override="sensor.coros_course_mois",
        value_fn=lambda d: d.get("monthly_stats", {}).get("running_km", 0),
        attrs_fn=lambda d: {
            "count": d.get("monthly_stats", {}).get("running_count", 0),
            "time_str": d.get("monthly_stats", {}).get("running_time_str", "0 min"),
            "time_seconds": d.get("monthly_stats", {}).get("running_time_seconds", 0),
        },
    ),
    CorosSensorEntityDescription(
        key="velo_month_km",
        name="COROS Vélo & Gravel (Mois)",
        native_unit_of_measurement="km",
        icon="mdi:bicycle",
        state_class=SensorStateClass.TOTAL,
        entity_id_override="sensor.coros_velo_gravel_mois",
        value_fn=lambda d: d.get("monthly_stats", {}).get("velo_km", 0),
        attrs_fn=lambda d: {
            "count": d.get("monthly_stats", {}).get("velo_count", 0),
            "time_str": d.get("monthly_stats", {}).get("velo_time_str", "0 min"),
            "time_seconds": d.get("monthly_stats", {}).get("velo_time_seconds", 0),
        },
    ),
    CorosSensorEntityDescription(
        key="ppg_month_count",
        name="COROS PPG & Renfo (Mois)",
        native_unit_of_measurement="séances",
        icon="mdi:weight-lifter",
        state_class=SensorStateClass.TOTAL,
        entity_id_override="sensor.coros_ppg_renfo_mois",
        value_fn=lambda d: d.get("monthly_stats", {}).get("ppg_count", 0),
        attrs_fn=lambda d: {
            "count": d.get("monthly_stats", {}).get("ppg_count", 0),
            "time_str": d.get("monthly_stats", {}).get("ppg_time_str", "0 min"),
            "time_seconds": d.get("monthly_stats", {}).get("ppg_time_seconds", 0),
        },
    ),
    CorosSensorEntityDescription(
        key="month_total_time",
        name="COROS Temps Total (Mois)",
        icon="mdi:timer-outline",
        entity_id_override="sensor.coros_temps_total_mois",
        value_fn=lambda d: d.get("monthly_stats", {}).get("total_time_str", "0h 00"),
        attrs_fn=lambda d: {
            "total_activities": d.get("monthly_stats", {}).get("total_count", 0),
            "total_seconds": d.get("monthly_stats", {}).get("total_seconds", 0),
        },
    ),
    CorosSensorEntityDescription(
        key="month_total_count",
        name="COROS Séances Réalisées (Mois)",
        native_unit_of_measurement="séances",
        icon="mdi:fire",
        state_class=SensorStateClass.TOTAL,
        entity_id_override="sensor.coros_seances_realisees_mois",
        value_fn=lambda d: d.get("monthly_stats", {}).get("total_count", 0),
    ),
    CorosSensorEntityDescription(
        key="month_training_load",
        name="COROS Charge Entraînement (Mois)",
        native_unit_of_measurement="TL",
        icon="mdi:lightning-bolt",
        state_class=SensorStateClass.TOTAL,
        entity_id_override="sensor.coros_charge_entrainement_mois",
        value_fn=lambda d: d.get("monthly_stats", {}).get("training_load", 0),
        attrs_fn=lambda d: {
            "weekly_history": d.get("weekly_stats", {}).get("weekly_history", []),
        },
    ),

    # --- Statistiques Hebdomadaires ---
    CorosSensorEntityDescription(
        key="temps_activite_semaine",
        name="COROS Temps d'Activité (Semaine)",
        native_unit_of_measurement="h",
        icon="mdi:timer-outline",
        state_class=SensorStateClass.MEASUREMENT,
        entity_id_override="sensor.coros_temps_activite_semaine",
        value_fn=lambda d: d.get("weekly_stats", {}).get("current_week", {}).get("hours", 0.0),
        attrs_fn=lambda d: {
            "time_str": d.get("weekly_stats", {}).get("current_week", {}).get("time_str", "0 min"),
            "seconds": d.get("weekly_stats", {}).get("current_week", {}).get("seconds", 0),
            "training_load": d.get("weekly_stats", {}).get("current_week", {}).get("training_load", 0),
            "distance_km": d.get("weekly_stats", {}).get("current_week", {}).get("distance_km", 0.0),
            "count": d.get("weekly_stats", {}).get("current_week", {}).get("count", 0),
            "week_label": d.get("weekly_stats", {}).get("current_week", {}).get("week_label", ""),
            "date_range": d.get("weekly_stats", {}).get("current_week", {}).get("date_range", ""),
            "last_week_hours": d.get("weekly_stats", {}).get("last_week", {}).get("hours", 0.0),
            "last_week_load": d.get("weekly_stats", {}).get("last_week", {}).get("training_load", 0),
            "weekly_history": d.get("weekly_stats", {}).get("weekly_history", []),
        },
    ),
    CorosSensorEntityDescription(
        key="charge_entrainement_semaine",
        name="COROS Charge d'Entraînement (Semaine)",
        native_unit_of_measurement="TL",
        icon="mdi:chart-bell-curve-cumulative",
        state_class=SensorStateClass.MEASUREMENT,
        entity_id_override="sensor.coros_charge_entrainement_semaine",
        value_fn=lambda d: d.get("weekly_stats", {}).get("current_week", {}).get("training_load", 0),
        attrs_fn=lambda d: {
            "hours": d.get("weekly_stats", {}).get("current_week", {}).get("hours", 0.0),
            "time_str": d.get("weekly_stats", {}).get("current_week", {}).get("time_str", "0 min"),
            "distance_km": d.get("weekly_stats", {}).get("current_week", {}).get("distance_km", 0.0),
            "count": d.get("weekly_stats", {}).get("current_week", {}).get("count", 0),
            "week_label": d.get("weekly_stats", {}).get("current_week", {}).get("week_label", ""),
            "date_range": d.get("weekly_stats", {}).get("current_week", {}).get("date_range", ""),
            "last_week_load": d.get("weekly_stats", {}).get("last_week", {}).get("training_load", 0),
            "weekly_history": d.get("weekly_stats", {}).get("weekly_history", []),
        },
    ),

    # --- Planning & Prochaine Séance ---
    CorosSensorEntityDescription(
        key="upcoming_workouts",
        name="COROS Planning Entraînements",
        icon="mdi:calendar-check",
        entity_id_override="sensor.coros_planning_entrainements",
        value_fn=_get_upcoming_workouts_value,
        attrs_fn=_get_upcoming_workouts_attrs,
    ),
)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up COROS sensors."""
    coordinator: CorosDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        CorosSensor(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
    ]
    async_add_entities(entities)

class CorosSensor(CoordinatorEntity, SensorEntity):
    """Representation of a COROS sensor."""

    entity_description: CorosSensorEntityDescription

    def __init__(
        self,
        coordinator: CorosDataUpdateCoordinator,
        entry: ConfigEntry,
        description: CorosSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        if description.entity_id_override:
            self.entity_id = description.entity_id_override

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
    def native_value(self) -> Any:
        """Return native value of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes if configured."""
        if self.entity_description.attrs_fn:
            return self.entity_description.attrs_fn(self.coordinator.data)
        return None
