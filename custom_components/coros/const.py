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

ATTR_PACE = "pace"
ATTR_DISTANCE = "distance"
ATTR_SCORE = "score"
ATTR_DEEP_RATIO = "deep_ratio"
ATTR_LIGHT_RATIO = "light_ratio"
ATTR_REM_RATIO = "rem_ratio"
ATTR_STATUS = "status"
ATTR_BASELINE = "baseline"
ATTR_RANGE = "range"
ATTR_COUNT = "count"
ATTR_TIME_STR = "time_str"
ATTR_TIME_SECONDS = "time_seconds"
ATTR_WORKOUTS = "workouts"
