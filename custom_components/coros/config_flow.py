"""Config flow for COROS integration."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_EMAIL,
    CONF_PASSWORD,
    CONF_MCP_TOKEN,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

class CorosConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for COROS."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_EMAIL], data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_EMAIL): str,
            vol.Required(CONF_PASSWORD): str,
            vol.Optional(CONF_MCP_TOKEN): str,
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return CorosOptionsFlowHandler()

class CorosOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options."""

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
        current_mcp = self.config_entry.options.get(
            CONF_MCP_TOKEN,
            self.config_entry.data.get(CONF_MCP_TOKEN, ""),
        )
        schema = vol.Schema({
            vol.Optional(CONF_SCAN_INTERVAL, default=current_interval): cv.positive_int,
            vol.Optional(CONF_MCP_TOKEN, default=current_mcp): str,
        })
        return self.async_show_form(step_id="init", data_schema=schema)

