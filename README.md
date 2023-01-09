# pytest-telegram-notifier

[![PyPI version](https://badge.fury.io/py/pytest-telegram-notifier.svg)](https://badge.fury.io/py/pytest-telegram-notifier)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/PlagerX-Group/pytest-telegram-notifier/main.svg)](https://results.pre-commit.ci/latest/github/PlagerX-Group/pytest-telegram-notifier/main)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Open Source Helpers](https://www.codetriage.com/plagerx-group/pytest-telegram-notifier/badges/users.svg)](https://www.codetriage.com/plagerx-group/pytest-telegram-notifier)


#### To activate the plugin, you must use the parameter
```text
--telegram-notifier
```

#### Custom path or configuration file name
```text
--telegram-notifier-config-file <custom-path>
```

#### An example of plugin configuration:
```ini
[Telegram]
chat-id: -99999999

```

#### Environment variables
```text
TELEGRAM_ACCESS_TOKEN=<access-token>
```

#### An example of Telegram message
![name](docs/telegram-message.png)
