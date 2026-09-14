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
DEFAULT_MCP_REFRESH_TOKEN = "ohA2IawitTAgHbJ_zvHP9O9snjNtCyOXXhggKxeQKFkWEVdbeOco3XNbBbouMaGKkVY2BQ7YXnlTjzATER9HMKirFuX16N2uQ3PwkANCEKnAivEAUkBx4au2xiMHVJ2p"
DEFAULT_MCP_ACCESS_TOKEN = "eyJraWQiOiIxMWZjMTE0MS03YWFmLTQ0MzgtYTgxMC1mMjlmOWQzNGI1NWYiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJhMDljMThlMDA0NDc0YWVlOTAzOTg0N2I4NGIxNTJjNCIsImF1ZCI6IjZiZTljZDlkLTQwMjctNGQ5NS1hNTU5LTc4ODhiYzMwMjQ5NyIsIm5iZiI6MTc4NzgzMDk5Niwic2NvcGUiOlsibWNwLnRvb2xzIiwib3BlbmlkIiwib2ZmbGluZV9hY2Nlc3MiXSwiaXNzIjoiaHR0cHM6Ly9tY3BldS5jb3Jvcy5jb20iLCJtY3BfYXV0aG9yaXphdGlvbl92ZXJzaW9uIjowLCJleHAiOjE3OTA0MjI5OTYsImlhdCI6MTc4NzgzMDk5NiwianRpIjoiYjEyMzY2YzEtY2I3MC00YWVmLTkzMjgtNzM0MzA3NWJlY2NkIn0.VPJuxIL3ZoU-1DoX3Bp_5lPROoQiWzVL5B6hS0RFlIEPB_t621w-kYoBhjdnx1V38IQZI2xhCzIIMqdCCis6NeeDJIPdMKjK1Txn4jo9JLNBBKR4Z3VmBC8NgELU2y_0JN9PpRIb_N97FtHvJygYOwTVaHlYidT3qUoMYARcFANX2SMpstwZO33PSliXTpCvdAs7Jce88KpzPX0IScRWHotTQ_cuR4iAi4p2SNLqATh42LBDzKMxiqcYr-W4QIhXfCMMKZws273aTZTkWFvJ5F3EXFJPgYSw4jKj87g55Rahezx8y3GsFn4M8Hi2UHUT-CIYAzzBK94zCOaeumGC8g"

DEFAULT_MCP_TOKENS = {
    "client_id": DEFAULT_MCP_CLIENT_ID,
    "access_token": DEFAULT_MCP_ACCESS_TOKEN,
    "refresh_token": DEFAULT_MCP_REFRESH_TOKEN,
}

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
