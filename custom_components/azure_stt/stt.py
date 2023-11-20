"""Support for the cloud for speech to text service."""
from __future__ import annotations

import logging
import os
from collections.abc import AsyncIterable
import requests
import json

import async_timeout
import voluptuous as vol

from homeassistant.components.stt import (
    AudioBitRates,
    AudioChannels,
    AudioCodecs,
    AudioFormats,
    AudioSampleRates,
    Provider,
    SpeechMetadata,
    SpeechResult,
    SpeechResultState,
)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

CONF_API_KEY = "api_key"
CONF_REGION = "region"



SUPPORTED_LANGUAGES = [
    "af-ZA",
    "am-ET",
    "ar-AE",
    "ar-BH",
    "ar-DZ",
    "ar-EG",
    "ar-IL",
    "ar-IQ",
    "ar-JO",
    "ar-KW",
    "ar-LB",
    "ar-LY",
    "ar-MA",
    "ar-OM",
    "ar-PS",
    "ar-QA",
    "ar-SA",
    "ar-SY",
    "ar-TN",
    "ar-YE",
    "az-AZ",
    "bg-BG",
    "bn-IN",
    "bs-BA",
    "ca-ES",
    "cs-CZ",
    "cy-GB",
    "da-DK",
    "de-AT",
    "de-CH",
    "de-DE",
    "el-GR",
    "en-AU",
    "en-CA",
    "en-GB",
    "en-GH",
    "en-HK",
    "en-IE",
    "en-IN",
    "en-KE",
    "en-NG",
    "en-NZ",
    "en-PH",
    "en-SG",
    "en-TZ",
    "en-US",
    "en-ZA",
    "es-AR",
    "es-BO",
    "es-CL",
    "es-CO",
    "es-CR",
    "es-CU",
    "es-DO",
    "es-EC",
    "es-ES",
    "es-GQ",
    "es-GT",
    "es-HN",
    "es-MX",
    "es-NI",
    "es-PA",
    "es-PE",
    "es-PR",
    "es-PY",
    "es-SV",
    "es-US",
    "es-UY",
    "es-VE",
    "et-EE",
    "eu-ES",
    "fa-IR",
    "fi-FI",
    "fil-PH",
    "fr-BE",
    "fr-CA",
    "fr-CH",
    "fr-FR",
    "ga-IE",
    "gl-ES",
    "gu-IN",
    "he-IL",
    "hi-IN",
    "hr-HR",
    "hu-HU",
    "hy-AM",
    "id-ID",
    "is-IS",
    "it-CH",
    "it-IT",
    "ja-JP",
    "jv-ID",
    "ka-GE",
    "kk-KZ",
    "km-KH",
    "kn-IN",
    "ko-KR",
    "lo-LA",
    "lt-LT",
    "lv-LV",
    "mk-MK",
    "ml-IN",
    "mn-MN",
    "mr-IN",
    "ms-MY",
    "mt-MT",
    "my-MM",
    "nb-NO",
    "ne-NP",
    "nl-BE",
    "nl-NL",
    "pa-IN",
    "pl-PL",
    "ps-AF",
    "pt-BR",
    "pt-PT",
    "ro-RO",
    "ru-RU",
    "si-LK",
    "sk-SK",
    "sl-SI",
    "so-SO",
    "sq-AL",
    "sr-RS",
    "sv-SE",
    "sw-KE",
    "sw-TZ",
    "ta-IN",
    "te-IN",
    "th-TH",
    "tr-TR",
    "uk-UA",
    "ur-IN",
    "uz-UZ",
    "vi-VN",
    "wuu-CN",
    "yue-CN",
    "zh-CN",
    "zh-CN-shandong",
    "zh-CN-sichuan",
    "zh-HK",
    "zh-TW",
    "zu-ZA",
]


PLATFORM_SCHEMA = cv.PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_API_KEY): cv.string,
        vol.Required(CONF_REGION): cv.string,
    }
)


async def async_get_engine(hass, config, discovery_info=None):
    """Set up Azure STT component."""
    api_key = config.get(CONF_API_KEY)
    region = config.get(CONF_REGION)

    return AzureSTTProvider(hass, api_key, region)


class AzureSTTProvider(Provider):
    """The Azure STT API provider."""

    def __init__(self, hass, api_key, region) -> None:
        """Init Azure STT service."""
        self.hass = hass
        self.name = "Azure STT"


        self._api_key = api_key
        self._region = region
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
        # Collect data
        async def audio_data_generator():
            async for chunk in stream:
                yield chunk
        
        headers = {
            'Content-Type': 'audio/wav',
            'Ocp-Apim-Subscription-Key': self._api_key,
            'Transfer-Encoding': 'chunked'
        }

        def job():
            return requests.post(self._region, headers=headers, data=audio_data_generator(), stream=True)

        async with async_timeout.timeout(15):
            assert self.hass
            response = await self.hass.async_add_executor_job(job)
            

            for line in response.iter_lines():
                if line:
                    response_json = json.loads(line)
                    return SpeechResult(
                        response_json['DisplayText'],
                        SpeechResultState.SUCCESS,
                    )
                else:
                    return SpeechResult("",SpeechResultState.ERROR)
            