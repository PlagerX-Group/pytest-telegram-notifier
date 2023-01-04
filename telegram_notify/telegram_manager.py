import os
from datetime import datetime

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
        template = "Datetime start testing: {datetimestart}\n" \
                   "Datetime end testing: {datetimeend}\n" \
                   "Total tests: {teststotal}\n" \
                   "Tests failed: {testsfailed}\n" \
                   "Tests passed: {testspassed}\n" \
                   "Tests skipped: {testsskipped}\n"
        return template

    @pytest.hookimpl(trylast=True)
    def pytest_sessionstart(self):
        self.datetime_start_tests = datetime.now()

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
            message_template,
            datetimestart=self.datetime_start_tests.strftime('%H:%M:%S %d.%m.%Y'),
            datetimeend=datetime.now().strftime('%H:%M:%S %d.%m.%Y'),
            teststotal=self.teststotal,
            testspassed=self.teststotal - session.testsfailed - self.testsskipped,
            testsfailed=session.testsfailed,
            testsskipped=self.testsskipped,
        )
