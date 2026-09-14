"""Constants for the COROS integration."""
from datetime import timedelta

DOMAIN = "coros"
NAME = "COROS Training Hub & Health"

CONF_EMAIL = "email"
CONF_PASSWORD = "password"
CONF_MCP_TOKEN = "mcp_token"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_SCAN_INTERVAL = 15  # minutes

API_BASE_URL = "https://teameuapi.coros.com"
MCP_BASE_URL = "https://mcpeu.coros.com"

DEFAULT_MCP_CLIENT_ID = "6be9cd9d-4027-4d95-a559-7888bc302497"
DEFAULT_MCP_REFRESH_TOKEN = "REDACTED_MCP_REFRESH_TOKEN"

# Attributes
ATTR_PACE = "pace"
ATTR_DISTANCE = "distance"
ATTR_SCORE = "score"
ATTR_DEEP_RATIO = "deep_ratio"
ATTR_LIGHT_RATIO = "light_ratio"
ATTR_REM_RATIO = "rem_ratio"
ATTR_AWAKE_RATIO = "awake_ratio"
ATTR_AWAKE_TIME = "awake_time"
ATTR_AWAKE_COUNT = "awake_count"
ATTR_SLEEP_WINDOW = "window"
ATTR_STATUS = "status"
ATTR_BASELINE = "baseline"
ATTR_RANGE = "range"
ATTR_COUNT = "count"
ATTR_TIME_STR = "time_str"
ATTR_TIME_SECONDS = "time_seconds"
ATTR_WORKOUTS = "workouts"
ATTR_TOTAL_UPCOMING = "total_upcoming"
ATTR_LOAD_RATIO = "load_ratio"
ATTR_SHORT_TERM_LOAD = "short_term_load"
ATTR_LONG_TERM_LOAD = "long_term_load"
ATTR_MONTH_TOTAL_LOAD = "month_total_load"
ATTR_LEVEL = "level"
ATTR_ESTIMATED_FULL_RECOVERY = "estimated_full_recovery"
