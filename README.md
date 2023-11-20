# Azure Speech-To-Text for Home Assistant

[![](https://img.shields.io/github/release/chatziko/ha-google-cloud-stt/all.svg?style=for-the-badge)](https://github.com/chatziko/ha-google-cloud-stt/releases)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![](https://img.shields.io/badge/MAINTAINER-%40chatziko-red?style=for-the-badge)](https://github.com/chatziko)
[![](https://img.shields.io/badge/COMMUNITY-FORUM-success?style=for-the-badge)](https://community.home-assistant.io)

This integration allows to use [Azure Speech-to-Text](https://azure.microsoft.com/en-us/products/ai-services/speech-to-text) in Home Assistant.

## Install

You can install this integration via [HACS](https://hacs.xyz/). Go to HACS / Integrations / Three-dots menu / Custom repositories
and add:

- Repository: `https://github.com/Robert0309/ha-azure-stt.git`
- Category: Integration

Then install the "Azure Speech-To-Text" integration.

## Configure

Azure subscription - [Create one for free](https://azure.microsoft.com/free/cognitive-services).
[Create a Speech resource](https://portal.azure.com/#create/Microsoft.CognitiveServicesSpeechServices) in the Azure portal.
Your Speech resource key and region. After your Speech resource is deployed, select Go to resource to view and manage keys. For more information about Azure AI services resources, see [Get the keys for your resource](https://learn.microsoft.com/en-us/azure/ai-services/multi-service-resource?pivots=azportal#get-the-keys-for-your-resource).
Then place the JSON file with the API key you downloaded in the `config` folder, and add the following to your `configuration.yaml`:

```yaml
stt:
  - platform: azure_stt
    api_key: api_ky
    region: region
```

After enabling the integration, you can configure a [Voice Assistant](https://www.home-assistant.io/blog/2023/04/27/year-of-the-voice-chapter-2/#composing-voice-assistants)
to use it by selecting `azure_stt` in the "Speech-to-text" option.

The supported languages are listed [here](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=stt).

## FAQ

#### I get the following error in the Home Assistant system log

```
The stt integration does not support any configuration parameters, got [{'platform': 'azure_stt', 'api_key': 'api_ky', 'region': 'region'}]. Please remove the configuration parameters from your configuration.
```

This is a known issue due to a [bug](https://github.com/home-assistant/core/issues/97161) in Home Assistant >= 2023.7. However, the reported message
does **not** affect the functionality of this integration, it should still work as expected (if properly configured).
