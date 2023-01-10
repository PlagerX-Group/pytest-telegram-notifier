# pylint: disable=W0212

import copy
import os
import uuid
from datetime import datetime

import pytest
from _pytest.config import Config
from _pytest.main import Session
from _pytest.reports import TestReport

from telegram_notifier.bot import CallModeEnum, TelegramBot
from telegram_notifier.exceptions import (
    TelegramNotifierError,
    TelegramNotifierTelegraphError,
)


class TelegramManagerAdditionalFieldsWorker:
    def __init__(self):
        self.__fields = {}

    @property
    def fields(self) -> dict:
        return copy.deepcopy(self.__fields)

    def register_additional_field(self, key, value) -> None:
        self.__fields.update({str(key): str(value)})

    def register_additional_fields(self, fields: dict) -> None:
        for key, value in fields.items():
            self.register_additional_field(key, value)


class TelegramManager:
    def __init__(self, config: Config):
        self.datetime_start_tests = None
        self.testsskipped = 0

        self.itemslongrepr = []

        self._config = config
        self._additional_fields_worker = TelegramManagerAdditionalFieldsWorker()
        self._bot = TelegramBot(
            os.path.join(os.path.abspath(os.pardir), config.option.telegram_notifier_config_file),
        )

    @property
    def additional_fields_worker(self) -> TelegramManagerAdditionalFieldsWorker:
        return self._additional_fields_worker

    @pytest.hookimpl(trylast=True)
    def pytest_telegram_notifier_message_additional_fields(self) -> dict:
        return {}

    @pytest.hookimpl(trylast=True)
    def pytest_telegram_telegraph_title(self):
        return f'Automation-{uuid.uuid4()} ({datetime.now()})'

    @pytest.hookimpl(trylast=True)
    def pytest_telegram_notifier_message_template(self, additional_fields: dict) -> str:
        template = (
            '---------- Test report ----------\n'
            '\U0001F558 *Datetime start testing:* {datetimestart}\n'
            '\U0001F559 *Datetime end testing:* {datetimeend}\n\n'
            '\U0001F3AE *Count tests:* {teststotal}\n'
            '\U0001F534 *Tests failed:* {testsfailed}\n'
            '\U0001F7E2 *Tests passed:* {testspassed}\n'
            '\U0001F7E2 *Tests skipped:* {testsskipped}\n\n'
            '\U00000023 *Percentage of tests passed:* {percentpassedtests:.2f}%\n'
            '\U00000023 *Percentage of tests failed:* {percentfailedtests:.2f}%\n'
            '\U00000023 *Percentage of tests skipped:* {percentskippedtests:.2f}%\n\n'
        )
        if isinstance(additional_fields, dict) and additional_fields:
            template += '\n\n------- Additional fields -------\n'
            for key, value in additional_fields.items():
                template += f'\U000025AA *{key}:* {value}\n'
        template = template.replace('_', r'\_')
        template += '\nI CALL: {mentioned}\n'
        return template

    @pytest.hookimpl(tryfirst=True)
    def pytest_configure(self, config: Config):
        config.stash['telegram-notifier-addfields'] = {}

    @pytest.hookimpl(trylast=True)
    def pytest_sessionstart(self):
        self.datetime_start_tests = datetime.now()

    @pytest.hookimpl(tryfirst=True)
    def pytest_runtest_logreport(self, report: TestReport):
        if report.when == 'setup':
            if report.skipped:
                self.testsskipped += 1
        if report.when == 'call':
            if report.failed:
                self.itemslongrepr.append((report.fspath, str(report.longrepr)))

    @pytest.hookimpl(trylast=True)
    def pytest_sessionfinish(self, session: Session):
        self._config.hook.pytest_telegram_notifier_message_additional_fields(config=self._config)
        self._additional_fields_worker.register_additional_fields(
            dict(self._config.stash.get('telegram-notifier-addfields', {})),
        )

        template = self._config.hook.pytest_telegram_notifier_message_template(
            additional_fields=self.additional_fields_worker.fields
        )

        if not isinstance(template, str):
            raise TelegramNotifierError('The template type must be "str"')

        if len(template) == 0:
            raise TelegramNotifierError('Text for "template" cannot be empty')

        teststotal = session.testscollected

        if teststotal > 0:
            testspassed = teststotal - session.testsfailed - self.testsskipped
            kwargs = {
                'datetimestart': self.datetime_start_tests.strftime('%H:%M:%S %d.%m.%Y'),
                'datetimeend': datetime.now().strftime('%H:%M:%S %d.%m.%Y'),
                'teststotal': teststotal,
                'testspassed': teststotal - session.testsfailed - self.testsskipped,
                'testsfailed': session.testsfailed,
                'testsskipped': self.testsskipped,
                'percentpassedtests': round(testspassed / teststotal * 100, 2),
                'percentfailedtests': round(session.testsfailed / teststotal * 100, 2),
                'percentskippedtests': round(self.testsskipped / teststotal * 100, 2),
            }

            if (
                self._bot.mode == CallModeEnum.ALWAYS
                or self._bot.mode == CallModeEnum.ON_FAIL
                and session.testsfailed > 0
            ):
                kwargs.update({'mentioned': ', '.join(self._bot.users_call_on_fail)})
            else:
                kwargs.update({'mentioned': '<empty>'})

            if self._bot.telegraph.is_enabled:
                telegraph_title = self._config.hook.pytest_telegram_telegraph_title()

                if not isinstance(telegraph_title, str):
                    raise TelegramNotifierTelegraphError('The "telegraph_title" type must be "str"')

                if len(telegraph_title) == 0:
                    raise TelegramNotifierTelegraphError('Text for "telegraph_title" cannot be empty')

                telegraph_page_url = self._bot.telegraph.create_page(
                    telegraph_title,
                    stacktrace=self.itemslongrepr,
                )
                template += f'\n[Telegraph]({telegraph_page_url})'

            if session.testsfailed == 0:
                self._bot.send_passed_message(template, **kwargs)
            else:
                self._bot.send_failed_message(template, **kwargs)
