"""Config flow for Google Cloud STT integration."""

from __future__ import annotations

import json
import os
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.file_upload import process_uploaded_file
from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_MODEL
from homeassistant.core import callback
from homeassistant.helpers.selector import FileSelector, FileSelectorConfig

from .const import (
    _LOGGER,
    DEFAULT_MODEL,
    DOMAIN,
    SERVICE_ACCOUNT_INFO,
    SUPPORTED_MODELS,
)

UPLOADED_FILE = "uploaded_file"

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(UPLOADED_FILE): FileSelector(
                        FileSelectorConfig(accept=".json,application/json")
                    )
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


    def _parse_uploaded_file(
        self, uploaded_file_id: str
    ) -> dict:
        """Read and parse an uploaded JSON file."""
        with process_uploaded_file(self.hass, uploaded_file_id) as file_path:
            contents = file_path.read_text()

        return json.loads(contents)


    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        service_account_info = await self.hass.async_add_executor_job(
            self._parse_uploaded_file, user_input[UPLOADED_FILE]
        )

        return self.async_create_entry(title="Google Cloud STT", data={SERVICE_ACCOUNT_INFO: service_account_info})

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return GoogleCloudOptionsFlowHandler(config_entry)

    async def async_step_import(self, import_data: dict[str, Any]) -> ConfigFlowResult:
        """Import Google Cloud STT configuration from YAML."""

        if not os.path.isfile(self.hass.config.path(import_data["key_file"])):
            _LOGGER.error("File %s doesn't exist", import_data["key_file"])
            return self.async_abort(reason="file_not_found")

        service_account_info = await self.hass.async_add_executor_job(
            self._parse_uploaded_file, import_data["key_file"]
        )

        return self.async_create_entry(
            title="Google Cloud STT",
            data={SERVICE_ACCOUNT_INFO: service_account_info},
            options={
                CONF_MODEL: import_data.get(CONF_MODEL, DEFAULT_MODEL),
            },
        )


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
