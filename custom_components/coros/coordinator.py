"""DataUpdateCoordinator for COROS."""
import asyncio
from datetime import timedelta, datetime
import logging
import hashlib
import json
import re
import requests

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_EMAIL,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    API_BASE_URL,
)

_LOGGER = logging.getLogger(__name__)

def md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()

class CorosDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching COROS data from API."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.entry = entry
        self.email = entry.data[CONF_EMAIL]
        self.password = entry.data[CONF_PASSWORD]
        scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=scan_interval),
        )

    def _sync_fetch_all(self):
        """Fetch all data synchronously in an executor thread."""
        data = {
            "health": {},
            "monthly_stats": {},
            "predictions": {},
            "schedule": []
        }

        # 1. Login to COROS Consumer API
        login_res = requests.post(
            f"{API_BASE_URL}/account/login",
            json={"account": self.email, "accountType": 2, "pwd": md5(self.password)},
            timeout=10
        )
        if login_res.status_code != 200 or login_res.json().get("result") != "0000":
            _LOGGER.error("Failed to authenticate with COROS API: %s", login_res.text)
            return data

        login_data = login_res.json().get("data", {})
        token_coros = login_data.get("accessToken")
        user_id = login_data.get("userId")
        headers = {
            "accesstoken": token_coros,
            "content-type": "application/json",
            "yfheader": json.dumps({"userId": user_id})
        }

        # 2. Fetch current month activities
        now = datetime.now()
        start_day = now.strftime("%Y%m01")
        end_day = (now.replace(day=28) + timedelta(days=4)).strftime("%Y%m%d")

        acts_res = requests.get(
            f"{API_BASE_URL}/activity/query",
            headers=headers,
            params={"size": 100, "pageNumber": 1, "startDay": start_day, "endDay": end_day, "modeList": ""},
            timeout=15
        )

        running_km = 0.0
        running_sec = 0
        running_cnt = 0
        bike_km = 0.0
        bike_sec = 0
        bike_cnt = 0
        ppg_sec = 0
        ppg_cnt = 0
        total_tl = 0

        if acts_res.status_code == 200:
            acts = acts_res.json().get("data", {}).get("dataList", [])
            for a in acts:
                st = a.get("sportType") or a.get("mode")
                dist = (a.get("distance") or 0) / 1000.0
                sec = a.get("totalTime") or 0
                tl = a.get("trainingLoad") or 0
                name = (a.get("name") or "").lower()

                if st in [100, 101, 102, 103] or any(k in name for k in ["course", "cap", "trail"]):
                    running_km += dist
                    running_sec += sec
                    running_cnt += 1
                elif st in [200, 201, 202, 203, 204] or any(k in name for k in ["gravel", "vélo", "vtt"]):
                    bike_km += dist
                    bike_sec += sec
                    bike_cnt += 1
                elif st in [300, 301, 302, 303, 304, 305] or any(k in name for k in ["ppg", "renfo", "musculation"]):
                    ppg_sec += sec
                    ppg_cnt += 1
                total_tl += tl

        def format_dur(seconds):
            h = seconds // 3600
            m = (seconds % 3600) // 60
            return f"{h}h {m:02d} min" if h > 0 else f"{m} min"

        total_sec = running_sec + bike_sec + ppg_sec
        total_cnt = running_cnt + bike_cnt + ppg_cnt

        data["monthly_stats"] = {
            "running_km": round(running_km, 1),
            "running_count": running_cnt,
            "running_time_str": format_dur(running_sec),
            "velo_km": round(bike_km, 1),
            "velo_count": bike_cnt,
            "velo_time_str": format_dur(bike_sec),
            "ppg_count": ppg_cnt,
            "ppg_time_str": format_dur(ppg_sec),
            "total_count": total_cnt,
            "total_time_str": f"{total_sec // 3600}h {(total_sec % 3600) // 60:02d}",
            "training_load": total_tl
        }

        # 3. Fetch scheduled workouts & map entities to programs
        sched_start = now.strftime("%Y%m01")
        sched_end = (now + timedelta(days=45)).strftime("%Y%m%d")
        sched_res = requests.get(
            f"{API_BASE_URL}/training/schedule/query?startDate={sched_start}&endDate={sched_end}&supportRestExercise=1",
            headers=headers,
            timeout=15
        )
        if sched_res.status_code == 200:
            s_data = sched_res.json().get("data", {})
            entities = s_data.get("entities", [])
            programs_by_id = {str(p.get("idInPlan") or p.get("id")): p for p in s_data.get("programs", [])}
            
            schedule_list = []
            for e in entities:
                happen_day = str(e.get("happenDay") or "")
                plan_prog_id = str(e.get("idInPlan") or e.get("planProgramId") or e.get("programId") or "")
                prog = programs_by_id.get(plan_prog_id, {})
                
                name = prog.get("name") or e.get("name") or "Entraînement COROS"
                overview = prog.get("overview") or prog.get("description") or ""
                sport_type = prog.get("sportType", 1)
                
                is_ppg = "ppg" in name.lower() or "renfo" in name.lower() or sport_type in [300, 301, 302, 303, 304, 305]
                color = "#ab47bc" if is_ppg else "#00b0ff"
                icon = "mdi:weight-lifter" if is_ppg else "mdi:run-fast"

                schedule_list.append({
                    "date": happen_day,
                    "name": name,
                    "overview": overview,
                    "sport_type": sport_type,
                    "color": color,
                    "icon": icon,
                    "training_load": prog.get("trainingLoad") or 0
                })
            
            schedule_list.sort(key=lambda x: x["date"])
            data["schedule"] = schedule_list

        return data

    async def _async_update_data(self):
        """Fetch data from COROS."""
        try:
            return await self.hass.async_add_executor_job(self._sync_fetch_all)
        except Exception as err:
            raise UpdateFailed(f"Error communicating with COROS API: {err}") from err
