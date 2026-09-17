"""DataUpdateCoordinator for COROS."""
import asyncio
from datetime import timedelta, datetime
import logging
import hashlib
import json
import os
import re
import time
import requests

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_EMAIL,
    CONF_PASSWORD,
    CONF_MCP_TOKEN,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    API_BASE_URL,
    MCP_BASE_URL,
    DEFAULT_MCP_CLIENT_ID,
    DEFAULT_MCP_REFRESH_TOKEN,
    DEFAULT_MCP_TOKENS,
)

_LOGGER = logging.getLogger(__name__)

def md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()

def clean_text(txt: str) -> str:
    """Strip bounding quotes and unescape newline/tab sequences."""
    if not txt:
        return ""
    txt = txt.strip()
    if txt.startswith('"') and txt.endswith('"'):
        txt = txt[1:-1]
    return txt.replace("\\n", "\n").replace("\\t", "\t")

def compute_pace(time_str: str | None, dist_km: float) -> str:
    """Calculate average pace min/km from time string."""
    if not time_str or not dist_km:
        return ""
    parts = [int(p) for p in time_str.split(":") if p.isdigit()]
    if len(parts) == 2:
        sec = parts[0] * 60 + parts[1]
    elif len(parts) == 3:
        sec = parts[0] * 3600 + parts[1] * 60 + parts[2]
    else:
        return ""
    pace_sec = int(round(sec / dist_km))
SPORT_MAP = {
    100: ("Course à pied", "run", "mdi:run"),
    101: ("Tapis de course", "run", "mdi:run-fast"),
    102: ("Trail", "run", "mdi:hiking"),
    103: ("Piste", "run", "mdi:run"),
    200: ("Vélo de route", "bike", "mdi:bike"),
    201: ("Home-trainer", "bike", "mdi:bike-fast"),
    202: ("VTT", "bike", "mdi:bicycle"),
    203: ("Gravel", "bike", "mdi:bike"),
    204: ("Vélo électrique", "bike", "mdi:moped"),
    300: ("Renforcement", "strength", "mdi:dumbbell"),
    301: ("Musculation", "strength", "mdi:dumbbell"),
    400: ("Natation", "swim", "mdi:swim"),
    401: ("Natation eau libre", "swim", "mdi:swim"),
    402: ("Musculation", "strength", "mdi:dumbbell"),
    500: ("Marche", "walk", "mdi:walk"),
    501: ("Randonnée", "walk", "mdi:hiking"),
    900: ("Marche", "walk", "mdi:walk"),
    901: ("Corde à sauter", "other", "mdi:jump-rope"),
}

def format_duration(seconds: int) -> str:
    """Format seconds into readable duration string."""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h}h {m:02d}m {s:02d}s" if s > 0 else f"{h}h {m:02d}m"
    if m > 0:
        return f"{m}m {s:02d}s" if s > 0 else f"{m}m"
    return f"{s}s"

def parse_coros_activity(a: dict) -> dict:
    """Parse raw COROS activity dict into structured activity data."""
    st = a.get("sportType") or a.get("mode") or 0
    name = a.get("name") or "Activité"
    name_l = name.lower()

    if st in SPORT_MAP:
        sport_name, category, icon = SPORT_MAP[st]
    elif any(k in name_l for k in ["course", "cap", "footing", "fractionné", "seuil"]):
        sport_name, category, icon = "Course à pied", "run", "mdi:run"
    elif any(k in name_l for k in ["trail", "dénivelé"]):
        sport_name, category, icon = "Trail", "run", "mdi:hiking"
    elif any(k in name_l for k in ["vélo", "gravel", "vtt", "cyclisme", "sortie"]):
        sport_name, category, icon = "Vélo", "bike", "mdi:bike"
    elif any(k in name_l for k in ["muscu", "renfo", "ppg", "gainage"]):
        sport_name, category, icon = "Renforcement", "strength", "mdi:dumbbell"
    else:
        sport_name, category, icon = "Activité", "other", "mdi:shoe-print"

    dist_m = float(a.get("distance") or 0)
    dist_km = round(dist_m / 1000.0, 2)
    tot_sec = int(a.get("totalTime") or 0)
    work_sec = int(a.get("workoutTime") or tot_sec)

    pace_str = None
    speed_kmh = None
    if dist_km > 0 and work_sec > 0:
        speed_kmh = round((dist_km / (work_sec / 3600.0)), 2)
        pace_sec = int(round(work_sec / dist_km))
        pace_str = f"{pace_sec // 60}:{pace_sec % 60:02d} /km"

    start_ts = a.get("startTime")
    start_iso = None
    date_fr = None
    if start_ts:
        try:
            dt = datetime.fromtimestamp(start_ts)
            start_iso = dt.isoformat()
            date_fr = dt.strftime("%d/%m/%Y %H:%M")
        except Exception:
            pass

    cal = a.get("calorie") or 0
    kcal = int(round(cal / 1000.0)) if cal > 1000 else int(cal)

    # Detect actual GPS route map (COROS uses imageUrlType == 1 and /img/ for GPS maps)
    img_type = a.get("imageUrlType")
    img_url = a.get("imageUrl")
    has_gps = bool(img_type == 1 and img_url and "/img/" in img_url)
    map_url = img_url if has_gps else None

    return {
        "label_id": str(a.get("labelId") or ""),
        "name": name,
        "sport": sport_name,
        "category": category,
        "icon": icon,
        "sport_type": st,
        "date": str(a.get("date") or ""),
        "date_formatted": date_fr,
        "start_time": start_iso,
        "distance_km": dist_km,
        "distance_m": int(round(dist_m)),
        "duration": format_duration(tot_sec),
        "duration_seconds": tot_sec,
        "moving_time": format_duration(work_sec),
        "moving_time_seconds": work_sec,
        "pace": pace_str,
        "speed_kmh": speed_kmh,
        "avg_hr": a.get("avgHr") or None,
        "max_hr": a.get("maxHeartRate") or a.get("maxHr") or a.get("avgHr") or None,
        "elevation_gain": int(a.get("ascent") or 0),
        "elevation_loss": int(a.get("descent") or 0),
        "calories": kcal,
        "cadence": a.get("cadence") or None,
        "training_load": a.get("trainingLoad") or 0,
        "device": a.get("device") or None,
        "has_gps": has_gps,
        "map_url": map_url,
    }

class CorosDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching COROS data from API and MCP gateway."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.entry = entry
        self.email = entry.data[CONF_EMAIL]
        self.password = entry.data[CONF_PASSWORD]
        self.user_id: str | None = None
        self._mcp_tokens: dict | None = None
        scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=scan_interval),
        )

    def _get_token_file_path(self) -> str:
        """Get path to persistent token cache file."""
        return self.hass.config.path(".coros_tokens.json")

    def _load_mcp_tokens(self) -> dict:
        """Load MCP tokens from memory, config entry, cache file, or defaults."""
        if self._mcp_tokens:
            return self._mcp_tokens

        # 1. Config entry options or data
        configured_token = self.entry.options.get(CONF_MCP_TOKEN) or self.entry.data.get(CONF_MCP_TOKEN)
        if configured_token:
            if isinstance(configured_token, dict):
                self._mcp_tokens = configured_token
                return self._mcp_tokens
            if isinstance(configured_token, str):
                try:
                    self._mcp_tokens = json.loads(configured_token)
                    return self._mcp_tokens
                except Exception:
                    self._mcp_tokens = {
                        "refresh_token": configured_token,
                        "client_id": DEFAULT_MCP_CLIENT_ID
                    }
                    return self._mcp_tokens

        # 2. Local token file in HA config directory
        token_path = self._get_token_file_path()
        if os.path.exists(token_path):
            try:
                with open(token_path, "r", encoding="utf-8") as f:
                    tok = json.load(f)
                    if tok and isinstance(tok, dict):
                        if not tok.get("access_token") and DEFAULT_MCP_TOKENS.get("access_token"):
                            tok["access_token"] = DEFAULT_MCP_TOKENS["access_token"]
                        self._mcp_tokens = tok
                        return self._mcp_tokens
            except Exception as err:
                _LOGGER.debug("Could not read token file %s: %s", token_path, err)

        # 3. Fallback default tokens
        self._mcp_tokens = dict(DEFAULT_MCP_TOKENS)
        return self._mcp_tokens

    def _save_mcp_tokens(self, tokens: dict) -> None:
        """Persist tokens to cache file."""
        self._mcp_tokens = tokens
        token_path = self._get_token_file_path()
        try:
            with open(token_path, "w", encoding="utf-8") as f:
                json.dump(tokens, f, indent=2)
        except Exception as err:
            _LOGGER.debug("Could not save tokens to %s: %s", token_path, err)

    def _refresh_mcp_token(self, tokens: dict) -> dict:
        """Refresh MCP OAuth token."""
        client_id = tokens.get("client_id", DEFAULT_MCP_CLIENT_ID)
        refresh_tok = tokens.get("refresh_token")
        if not refresh_tok:
            return tokens

        try:
            res = requests.post(
                f"{MCP_BASE_URL}/oauth2/token",
                data={
                    "grant_type": "refresh_token",
                    "client_id": client_id,
                    "refresh_token": refresh_tok,
                },
                timeout=10
            )
            if res.status_code == 200:
                new_tokens = res.json()
                new_tokens["client_id"] = client_id
                self._save_mcp_tokens(new_tokens)
                return new_tokens
            _LOGGER.warning("COROS MCP token refresh failed (%s): %s", res.status_code, res.text)
        except Exception as err:
            _LOGGER.warning("Error refreshing COROS MCP token: %s", err)
        return tokens

    def _get_mcp_session_headers(self, tokens: dict) -> dict | None:
        """Initialize MCP session and return authenticated headers."""
        access_token = tokens.get("access_token")
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        init_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "HomeAssistant", "version": "1.2.0"}
            }
        }
        try:
            res = requests.post(f"{MCP_BASE_URL}/mcp", headers=headers, json=init_payload, timeout=10)
            if res.status_code == 401 or not access_token:
                tokens = self._refresh_mcp_token(tokens)
                access_token = tokens.get("access_token")
                if not access_token and DEFAULT_MCP_TOKENS.get("access_token"):
                    access_token = DEFAULT_MCP_TOKENS["access_token"]
                    tokens["access_token"] = access_token
                headers["Authorization"] = f"Bearer {access_token}"
                res = requests.post(f"{MCP_BASE_URL}/mcp", headers=headers, json=init_payload, timeout=10)

            if res.status_code != 200:
                _LOGGER.warning("COROS MCP initialize failed (%s): %s", res.status_code, res.text)
                return None

            session_id = res.headers.get("Mcp-Session-Id") or res.headers.get("mcp-session-id")
            if session_id:
                headers["Mcp-Session-Id"] = session_id
                requests.post(
                    f"{MCP_BASE_URL}/mcp",
                    headers=headers,
                    json={"jsonrpc": "2.0", "method": "notifications/initialized"},
                    timeout=10
                )
            return headers
        except Exception as err:
            _LOGGER.warning("Could not establish COROS MCP session: %s", err)
            return None

    def _call_mcp_tool(self, headers: dict, tool_name: str, args: dict = None) -> dict | None:
        """Call an MCP tool on the COROS gateway."""
        if args is None:
            args = {}
        payload = {
            "jsonrpc": "2.0",
            "id": int(time.time()),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": args
            }
        }
        try:
            res = requests.post(f"{MCP_BASE_URL}/mcp", headers=headers, json=payload, timeout=15)
            if res.status_code == 200:
                return res.json().get("result")
            _LOGGER.debug("MCP call %s returned %s: %s", tool_name, res.status_code, res.text)
        except Exception as err:
            _LOGGER.debug("Error calling MCP tool %s: %s", tool_name, err)
        return None

    def _sync_fetch_mcp_metrics(self) -> dict:
        """Fetch all health, fitness, and recovery metrics via MCP."""
        mcp_data = {
            "fitness": {},
            "training_status": {},
            "recovery": {},
            "health": {},
            "sleep": {}
        }
        try:
            tokens = self._load_mcp_tokens()
            headers = self._get_mcp_session_headers(tokens)
            if not headers:
                return mcp_data

            # 1. Fitness Assessment Overview (EvoLab Race Predictor)
            fit_res = self._call_mcp_tool(headers, "queryFitnessAssessmentOverview", {})
            if fit_res and fit_res.get("content"):
                txt = clean_text(fit_res["content"][0].get("text", ""))
                m_vo2 = re.search(r'VO2max:\s*(\d+)', txt)
                m_rl = re.search(r'Running Level:\s*(\d+)', txt)
                m_tp = re.search(r'Threshold Pace:\s*([\d:]+)', txt)
                m_5k = re.search(r'5 km Prediction:\s*([\d:]+)', txt)
                m_10k = re.search(r'10 km Prediction:\s*([\d:]+)', txt)
                m_semi = re.search(r'Half Marathon Prediction:\s*([\d:]+)', txt)
                m_mar = re.search(r'(?<!Half )Marathon Prediction:\s*([\d:]+)', txt)

                t_5k = m_5k.group(1) if m_5k else None
                t_10k = m_10k.group(1) if m_10k else None
                t_semi = m_semi.group(1) if m_semi else None
                t_mar = m_mar.group(1) if m_mar else None

                mcp_data["fitness"] = {
                    "vo2max": int(m_vo2.group(1)) if m_vo2 else None,
                    "running_level": int(m_rl.group(1)) if m_rl else None,
                    "threshold_pace": f"{m_tp.group(1)} /km" if m_tp else None,
                    "prediction_5k": t_5k,
                    "pace_5k": compute_pace(t_5k, 5.0),
                    "prediction_10k": t_10k,
                    "pace_10k": compute_pace(t_10k, 10.0),
                    "prediction_semi": t_semi,
                    "pace_semi": compute_pace(t_semi, 21.0975),
                    "prediction_marathon": t_mar,
                    "pace_marathon": compute_pace(t_mar, 42.195),
                }

            # 2. Training Load Assessment (Fitness, Fatigue, Load Ratio)
            tl_res = self._call_mcp_tool(headers, "queryTrainingLoadAssessment", {"days": 7})
            if tl_res and tl_res.get("content"):
                txt = clean_text(tl_res["content"][0].get("text", ""))
                blocks = re.findall(
                    r'(\d{4}-\d{2}-\d{2})\s*\nComment:\s*([^\n]+)\s*\nShort-Term Load:\s*(\d+)\s*\nLong-Term Load:\s*(\d+)\s*\nLoad Ratio:\s*([\d\.]+)',
                    txt
                )
                if blocks:
                    latest = blocks[0]
                    mcp_data["training_status"] = {
                        "date": latest[0],
                        "status": latest[1].strip(),
                        "short_term_load": int(latest[2]),
                        "long_term_load": int(latest[3]),
                        "load_ratio": float(latest[4]),
                    }

            # 3. Recovery Status
            rec_res = self._call_mcp_tool(headers, "queryRecoveryStatus", {})
            if rec_res and rec_res.get("content"):
                txt = clean_text(rec_res["content"][0].get("text", ""))
                m_rec = re.search(r'Recovery:\s*(\d+)%', txt)
                m_lvl = re.search(r'Level:\s*([^\n\r]+)', txt)
                m_time = re.search(r'Estimated Full Recovery:\s*([^\n\r]+)', txt)
                mcp_data["recovery"] = {
                    "recovery_percent": int(m_rec.group(1)) if m_rec else None,
                    "recovery_level": m_lvl.group(1).strip() if m_lvl else None,
                    "recovery_time": m_time.group(1).strip() if m_time else None,
                }

            # 4. Resting Heart Rate
            rhr_res = self._call_mcp_tool(headers, "queryRestingHeartRate", {"days": 7})
            if rhr_res and rhr_res.get("content"):
                txt = clean_text(rhr_res["content"][0].get("text", ""))
                m_rhr = re.findall(r'(\d{4}-\d{2}-\d{2}):\s*(\d+)\s*bpm', txt)
                if m_rhr:
                    mcp_data["health"]["resting_heart_rate"] = int(m_rhr[0][1])

            # 5. Sleep HRV
            hrv_res = self._call_mcp_tool(headers, "querySleepHrv", {"days": 7})
            if hrv_res and hrv_res.get("content"):
                txt = clean_text(hrv_res["content"][0].get("text", ""))
                m_hrv = re.findall(
                    r'(\d{4}-\d{2}-\d{2}):\s*\n\s*HRV Avg:\s*(\d+)\s*ms\s*—\s*([^\n]+)\s*\n\s*Normal Range:\s*([^\n]+)\s*\n\s*Baseline:\s*([^\n]+)',
                    txt
                )
                if m_hrv:
                    latest = m_hrv[0]
                    mcp_data["health"]["hrv_avg"] = int(latest[1])
                    mcp_data["health"]["hrv_status"] = latest[2].strip()
                    mcp_data["health"]["hrv_range"] = latest[3].strip()
                    mcp_data["health"]["hrv_baseline"] = latest[4].strip()

            # 6. Sleep Data
            sleep_res = self._call_mcp_tool(headers, "querySleepData", {"days": 7})
            if sleep_res and sleep_res.get("content"):
                txt = clean_text(sleep_res["content"][0].get("text", ""))
                sleep_blocks = re.findall(
                    r'(\d{4}-\d{2}-\d{2})\s*\nSleep Score:\s*(\d+)\s*\nMain Sleep:\s*([^\n]+)\s*\nDeep Sleep Ratio:\s*(\d+)%\s*\nLight Sleep Ratio:\s*(\d+)%\s*\nREM Ratio:\s*(\d+)%\s*\nAwake Ratio:\s*(\d+)%\s*\nAwake Time:\s*([^\n]+)\s*\nAwake Count[^:]*:\s*(\d+)\s*\nMain Sleep Window:\s*([^\n]+)',
                    txt
                )
                if sleep_blocks:
                    latest = sleep_blocks[-1]
                    mcp_data["sleep"] = {
                        "date": latest[0],
                        "score": int(latest[1]),
                        "duration": latest[2].replace("min", "").strip(),
                        "deep_ratio": int(latest[3]),
                        "light_ratio": int(latest[4]),
                        "rem_ratio": int(latest[5]),
                        "awake_ratio": int(latest[6]),
                        "awake_time": latest[7].strip(),
                        "awake_count": int(latest[8]),
                        "window": latest[9].strip(),
                    }
        except Exception as err:
            _LOGGER.warning("Error fetching COROS MCP metrics: %s", err)

        return mcp_data

    def _sync_fetch_all(self):
        """Fetch all data synchronously in an executor thread."""
        data = {
            "monthly_stats": {},
            "weekly_stats": {},
            "schedule": [],
            "fitness": {},
            "training_status": {},
            "recovery": {},
            "health": {},
            "sleep": {},
            "latest_activity": None,
            "recent_activities": [],
            "latest_run": None,
            "latest_bike": None,
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
        self.user_id = user_id

        headers = {
            "accesstoken": token_coros,
            "content-type": "application/json",
            "yfheader": json.dumps({"userId": user_id})
        }

        # 2. Fetch activities (last 70 days for weekly and monthly stats)
        now = datetime.now()
        current_month_prefix = now.strftime("%Y%m")
        current_iso_year, current_iso_week, _ = now.isocalendar()

        start_day = (now - timedelta(days=70)).strftime("%Y%m%d")
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

        # Weekly buckets (last 8 weeks up to current week)
        months_fr = ["", "Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sept", "Oct", "Nov", "Déc"]
        weeks_dict = {}
        for i in range(7, -1, -1):
            ref_date = now - timedelta(weeks=i)
            y, w, _ = ref_date.isocalendar()
            key = f"{y}-W{w:02d}"
            mon = ref_date - timedelta(days=ref_date.weekday())
            sun = mon + timedelta(days=6)
            if mon.month == sun.month:
                label_range = f"{mon.day} - {sun.day} {months_fr[mon.month]}"
            else:
                label_range = f"{mon.day} {months_fr[mon.month]} - {sun.day} {months_fr[sun.month]}"

            weeks_dict[key] = {
                "key": key,
                "week_label": f"S{w:02d}",
                "week_num": w,
                "year": y,
                "date_range": label_range,
                "start_date": mon.strftime("%Y-%m-%d"),
                "end_date": sun.strftime("%Y-%m-%d"),
                "start_timestamp": int(mon.timestamp() * 1000),
                "total_seconds": 0,
                "total_hours": 0.0,
                "training_load": 0,
                "distance_km": 0.0,
                "count": 0,
                "is_current": (y == current_iso_year and w == current_iso_week),
            }

        parsed_activities = []
        if acts_res.status_code == 200:
            acts = acts_res.json().get("data", {}).get("dataList", [])
            for a in acts:
                parsed_act = parse_coros_activity(a)
                parsed_activities.append(parsed_act)

                d_str = str(a.get("date") or "")
                st = a.get("sportType") or a.get("mode")
                dist = (a.get("distance") or 0) / 1000.0
                sec = a.get("totalTime") or 0
                tl = a.get("trainingLoad") or 0
                name = (a.get("name") or "").lower()

                # 2.a Monthly stats (current month only)
                if d_str.startswith(current_month_prefix):
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

                # 2.b Weekly aggregation
                if len(d_str) == 8:
                    try:
                        act_dt = datetime.strptime(d_str, "%Y%m%d")
                        act_y, act_w, _ = act_dt.isocalendar()
                        w_key = f"{act_y}-W{act_w:02d}"
                        if w_key in weeks_dict:
                            weeks_dict[w_key]["total_seconds"] += sec
                            weeks_dict[w_key]["training_load"] += tl
                            weeks_dict[w_key]["distance_km"] += dist
                            weeks_dict[w_key]["count"] += 1
                    except Exception:
                        pass

        if parsed_activities:
            data["latest_activity"] = parsed_activities[0]
            data["recent_activities"] = parsed_activities[:10]
            for act in parsed_activities:
                if act["category"] == "run" and data["latest_run"] is None:
                    data["latest_run"] = act
                if act["category"] == "bike" and data["latest_bike"] is None:
                    data["latest_bike"] = act

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
            "running_time_seconds": running_sec,
            "velo_km": round(bike_km, 1),
            "velo_count": bike_cnt,
            "velo_time_str": format_dur(bike_sec),
            "velo_time_seconds": bike_sec,
            "ppg_count": ppg_cnt,
            "ppg_time_str": format_dur(ppg_sec),
            "ppg_time_seconds": ppg_sec,
            "total_count": total_cnt,
            "total_time_str": f"{total_sec // 3600}h {(total_sec % 3600) // 60:02d}",
            "total_seconds": total_sec,
            "training_load": total_tl
        }

        # Build final weekly list & current/last week stats
        weekly_history = []
        for k in sorted(weeks_dict.keys()):
            item = weeks_dict[k]
            item["total_hours"] = round(item["total_seconds"] / 3600.0, 1)
            item["total_time_str"] = format_dur(item["total_seconds"])
            item["distance_km"] = round(item["distance_km"], 1)
            weekly_history.append(item)

        cur_week_key = f"{current_iso_year}-W{current_iso_week:02d}"
        cur_w_data = weeks_dict.get(cur_week_key, {})
        last_w_data = weekly_history[-2] if len(weekly_history) >= 2 else {}

        data["weekly_stats"] = {
            "current_week": {
                "hours": cur_w_data.get("total_hours", 0.0),
                "seconds": cur_w_data.get("total_seconds", 0),
                "time_str": format_dur(cur_w_data.get("total_seconds", 0)),
                "training_load": cur_w_data.get("training_load", 0),
                "distance_km": cur_w_data.get("distance_km", 0.0),
                "count": cur_w_data.get("count", 0),
                "week_label": cur_w_data.get("week_label", ""),
                "date_range": cur_w_data.get("date_range", ""),
            },
            "last_week": {
                "hours": last_w_data.get("total_hours", 0.0),
                "seconds": last_w_data.get("total_seconds", 0),
                "time_str": last_w_data.get("total_time_str", "0 min"),
                "training_load": last_w_data.get("training_load", 0),
                "distance_km": last_w_data.get("distance_km", 0.0),
                "count": last_w_data.get("count", 0),
                "week_label": last_w_data.get("week_label", ""),
                "date_range": last_w_data.get("date_range", ""),
            },
            "weekly_history": weekly_history,
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

        # 4. Fetch MCP metrics (Health, Recovery, Fitness, Sleep, HRV)
        mcp_metrics = self._sync_fetch_mcp_metrics()
        data.update(mcp_metrics)

        return data

    async def _async_update_data(self):
        """Fetch data from COROS."""
        try:
            return await self.hass.async_add_executor_job(self._sync_fetch_all)
        except Exception as err:
            raise UpdateFailed(f"Error communicating with COROS API: {err}") from err
