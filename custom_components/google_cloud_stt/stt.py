"""Support for the Google Cloud speech to text service."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterable
import os

from google.cloud import (
    speech,  # Use speech v1. For the moment speech v2 is in preview and has fewer supported languages
)

from homeassistant.components import stt
from homeassistant.components.stt import (
    AudioBitRates,
    AudioChannels,
    AudioCodecs,
    AudioFormats,
    AudioSampleRates,
    SpeechMetadata,
    SpeechResult,
    SpeechResultState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_FILE_PATH, CONF_MODEL
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import _LOGGER, DEFAULT_MODEL

SUPPORTED_LANGUAGES = [
    "af-ZA",
    "sq-AL",
    "am-ET",
    "ar-DZ",
    "ar-BH",
    "ar-EG",
    "ar-IQ",
    "ar-IL",
    "ar-JO",
    "ar-KW",
    "ar-LB",
    "ar-MA",
    "ar-OM",
    "ar-QA",
    "ar-SA",
    "ar-PS",
    "ar-TN",
    "ar-AE",
    "ar-YE",
    "hy-AM",
    "az-AZ",
    "eu-ES",
    "bn-BD",
    "bn-IN",
    "bs-BA",
    "bg-BG",
    "my-MM",
    "ca-ES",
    "zh-CN",
    "zh-TW",
    "hr-HR",
    "cs-CZ",
    "da-DK",
    "nl-BE",
    "nl-NL",
    "en-AU",
    "en-CA",
    "en-GH",
    "en-HK",
    "en-IN",
    "en-IE",
    "en-KE",
    "en-NZ",
    "en-NG",
    "en-PK",
    "en-PH",
    "en-SG",
    "en-ZA",
    "en-TZ",
    "en-GB",
    "en-US",
    "et-EE",
    "fil-PH",
    "fi-FI",
    "fr-BE",
    "fr-CA",
    "fr-FR",
    "fr-CH",
    "gl-ES",
    "ka-GE",
    "de-AT",
    "de-DE",
    "de-CH",
    "el-GR",
    "gu-IN",
    "iw-IL",
    "hi-IN",
    "hu-HU",
    "is-IS",
    "id-ID",
    "it-IT",
    "it-CH",
    "ja-JP",
    "jv-ID",
    "kn-IN",
    "kk-KZ",
    "km-KH",
    "ko-KR",
    "lo-LA",
    "lv-LV",
    "lt-LT",
    "mk-MK",
    "ms-MY",
    "ml-IN",
    "mr-IN",
    "mn-MN",
    "ne-NP",
    "no-NO",
    "fa-IR",
    "pl-PL",
    "pt-BR",
    "pt-PT",
    "ro-RO",
    "ru-RU",
    "sr-RS",
    "si-LK",
    "sk-SK",
    "sl-SI",
    "es-AR",
    "es-BO",
    "es-CL",
    "es-CO",
    "es-CR",
    "es-DO",
    "es-EC",
    "es-SV",
    "es-GT",
    "es-HN",
    "es-MX",
    "es-NI",
    "es-PA",
    "es-PY",
    "es-PE",
    "es-PR",
    "es-ES",
    "es-US",
    "es-UY",
    "es-VE",
    "su-ID",
    "sw-KE",
    "sw-TZ",
    "sv-SE",
    "ta-IN",
    "ta-MY",
    "ta-SG",
    "ta-LK",
    "te-IN",
    "th-TH",
    "tr-TR",
    "uk-UA",
    "ur-IN",
    "ur-PK",
    "uz-UZ",
    "vi-VN",
    "zu-ZA",
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Wyoming speech-to-text."""
    key_file = hass.config.path(
        str(config_entry.data.get(CONF_FILE_PATH, "googlecloud.json"))
    )
    if not os.path.isfile(key_file):
        _LOGGER.error("File %s doesn't exist", key_file)
        return None

    async_add_entities(
        [
            GoogleCloudSTTProvider(
                hass, key_file, config_entry.options.get(CONF_MODEL, DEFAULT_MODEL)
            ),
        ]
    )


class GoogleCloudSTTProvider(stt.SpeechToTextEntity):
    """The Google Cloud STT API provider."""

    def __init__(self, hass, key_file, model) -> None:
        """Init Google Cloud STT service."""
        self.hass = hass
        self._attr_name = "Google Cloud STT"

        self._model = model
        self._key_file = key_file
        self._client = None

    @property
    def supported_languages(self) -> list[str]:
        """Return a list of supported languages."""
        return SUPPORTED_LANGUAGES

    @property
    def supported_formats(self) -> list[AudioFormats]:
        """Return a list of supported formats."""
        return [AudioFormats.WAV, AudioFormats.OGG]

    @property
    def supported_codecs(self) -> list[AudioCodecs]:
        """Return a list of supported codecs."""
        return [AudioCodecs.PCM, AudioCodecs.OPUS]

    @property
    def supported_bit_rates(self) -> list[AudioBitRates]:
        """Return a list of supported bitrates."""
        return [AudioBitRates.BITRATE_16]

    @property
    def supported_sample_rates(self) -> list[AudioSampleRates]:
        """Return a list of supported samplerates."""
        return [AudioSampleRates.SAMPLERATE_16000]

    @property
    def supported_channels(self) -> list[AudioChannels]:
        """Return a list of supported channels."""
        return [AudioChannels.CHANNEL_MONO]

    async def async_process_audio_stream(
        self, metadata: SpeechMetadata, stream: AsyncIterable[bytes]
    ) -> SpeechResult:
        """Process an audio stream to STT service."""
        # Collect data
        audio_data = b""
        async for chunk in stream:
            audio_data += chunk

        audio = speech.RecognitionAudio(content=audio_data)
        encoding = (
            speech.RecognitionConfig.AudioEncoding.OGG_OPUS
            if metadata.codec == AudioCodecs.OPUS
            else speech.RecognitionConfig.AudioEncoding.LINEAR16
        )
        config = speech.RecognitionConfig(
            language_code=metadata.language,
            encoding=encoding,
            sample_rate_hertz=metadata.sample_rate,
            model=self._model,
        )

        def job():
            # Create the client on first use, so that it is created inside the executor job
            if self._client is None:
                if self._key_file:
                    self._client = speech.SpeechClient.from_service_account_json(
                        self._key_file
                    )
                else:
                    self._client = speech.SpeechClient()

            return self._client.recognize(config=config, audio=audio)

        async with asyncio.timeout(10):
            assert self.hass
            response = await self.hass.async_add_executor_job(job)
            if response.results and response.results[0].alternatives:
                return SpeechResult(
                    response.results[0].alternatives[0].transcript,
                    SpeechResultState.SUCCESS,
                )
            return SpeechResult("", SpeechResultState.ERROR)
