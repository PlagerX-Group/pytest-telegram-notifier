import os

import pytest
import requests
from _pytest.config import Config, ExitCode
from _pytest.main import Session
from _pytest.nodes import Item

from telegram_notify.bot import TelegramBot


class TelegramManager:
    def __init__(self, config: Config):
        self._config = config
        self._bot = TelegramBot(
            os.path.join(os.path.abspath(os.pardir), config.option.telegram_notify_config_file),
        )

    def send_message(self):
        requests.get()

    @pytest.hookimpl
    def pytest_telegram_notify_message_template(self) -> str:
        template = "Total tests: {teststotal}\n" \
                   "Tests failed: {testsfailed}\n" \
                   "Tests passed: {testspassed}\n" \
                   "Tests skipped: {testsskipped}\n"
        return template

    @pytest.hookimpl(trylast=True)
    def pytest_collection_modifyitems(self, items: list[Item]):
        self.teststotal = len(items)
        self.testsskipped = len(
            [
                markers
                for markers in [item.own_markers
                                for item in items]
                if 'skip' in [marker.name for marker in markers]
            ]
        )

    @pytest.hookimpl
    def pytest_sessionfinish(self, session: Session):
        message_template = self._config.hook.pytest_telegram_notify_message_template()[0]
        self._bot.send_message(
            self.teststotal,
            self.teststotal - session.testsfailed - self.testsskipped,
            session.testsfailed,
            self.testsskipped,
            template=message_template
        )
