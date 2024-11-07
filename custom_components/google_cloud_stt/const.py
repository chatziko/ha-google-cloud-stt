"""Constants for the Google Cloud Speech-to-Text integration."""

import logging

_LOGGER = logging.getLogger(__package__)


DOMAIN = "google_cloud_stt"
DEFAULT_MODEL = "command_and_search"

SERVICE_ACCOUNT_INFO = "service_account_info"

SUPPORTED_MODELS = [
    "default",
    "command_and_search",
    "latest_short",
    "latest_long",
    "phone_call",
    "video",
]
