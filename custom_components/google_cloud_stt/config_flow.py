"""Config flow for Google Cloud STT integration."""

from __future__ import annotations

import os
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_FILE_PATH, CONF_MODEL
from homeassistant.core import callback

from .const import DEFAULT_MODEL, DOMAIN, SUPPORTED_MODELS

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_FILE_PATH): str,
    }
)

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_MODEL, default=DEFAULT_MODEL): vol.In(SUPPORTED_MODELS),
    }
)


class GoogleCloudConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Google Cloud STT integration."""

    VERSION = 1

    _name: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        if not os.path.isfile(self.hass.config.path(user_input[CONF_FILE_PATH])):
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
                errors={CONF_FILE_PATH: "file_not_found"},
            )

        return self.async_create_entry(title="Google Cloud STT", data=user_input)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return GoogleCloudOptionsFlowHandler(config_entry)


class GoogleCloudOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle a options flow for Google Cloud STT integration."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize Google Cloud STT options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        return self.async_show_form(step_id="init", data_schema=OPTIONS_SCHEMA)
