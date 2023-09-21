# Google Cloud Speech-To-Text for Home Assistant

[![](https://img.shields.io/github/release/chatziko/ha-google-cloud-stt/all.svg?style=for-the-badge)](https://github.com/chatziko/ha-google-cloud-stt/releases)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![](https://img.shields.io/badge/MAINTAINER-%40chatziko-red?style=for-the-badge)](https://github.com/chatziko)
[![](https://img.shields.io/badge/COMMUNITY-FORUM-success?style=for-the-badge)](https://community.home-assistant.io)


This integration allows to use [Google Cloud Speech-to-Text](https://cloud.google.com/speech-to-text) in Home Assistant.

## Install

You can install this integration via [HACS](https://hacs.xyz/). Go to HACS / Integrations / Three-dots menu / Custom repositories
and add:
- Repository: `https://github.com/chatziko/ha-google-cloud-stt`
- Category: Integration

Then install the "Google Cloud Speech-To-Text" integration.


## Configure

To use it you need to configure a Google Cloud project, following the same instructions as the
[Google Cloud Text-to-Speach](https://www.home-assistant.io/integrations/google_cloud) integration.
Then place the JSON file with the API key you downloaded in the `config` folder, and add the following to your `configuration.yaml`:

```yaml
stt:
  - platform: google_cloud_stt
    key_file: googlecloud.json
    model: command_and_search
```

After enabling the integration, you can configure a [Voice Assistant](https://www.home-assistant.io/blog/2023/04/27/year-of-the-voice-chapter-2/#composing-voice-assistants)
to use it by selecting `google_cloud_stt` in the "Speech-to-text" option.

The supported languages are listed [here](https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages).
Note that V1 of Google Cloud Speech-to-Text is used (V2 is still in preview and available in much fewer languages).
The list of available models is avaiable [here](https://cloud.google.com/speech-to-text/docs/speech-to-text-requests#select-model). The default model
is `command_and_search`, since it is available in most languages and should perform well in home automation tasks.


## FAQ

#### I get the following error in the Home Assistant system log

  ```
  The stt integration does not support any configuration parameters, got [{'platform': 'google_cloud_stt', 'key_file': 'google-cloud-service-googlecloud.json', 'model': 'command_and_search'}]. Please remove the configuration parameters from your configuration.
  ```

This is a known issue due to a [bug](https://github.com/home-assistant/core/issues/97161) in Home Assistant >= 2023.7. However, the reported message
does __not__ affect the functionality of this integration, it should still work as expected (if properly configured).