# pylint: disable=W0212

import copy
from datetime import datetime

import pytest
from _pytest.config import Config
from _pytest.main import Session
from _pytest.reports import TestReport

from telegram_notifier.bot import CallModeEnum, TelegramBot
from telegram_notifier.exceptions import TelegramNotifierError


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

        self._config = config
        self._additional_fields_worker = TelegramManagerAdditionalFieldsWorker()
        self._bot = TelegramBot(config.option.telegram_notifier_config_file)

    @property
    def additional_fields_worker(self) -> TelegramManagerAdditionalFieldsWorker:
        return self._additional_fields_worker

    @pytest.hookimpl(trylast=True)
    def pytest_telegram_notifier_message_additional_fields(self) -> dict:
        return {}

    @pytest.hookimpl(trylast=True)
    def pytest_telegram_notifier_message_template(self, additional_fields: dict) -> str:
        template = (
            '---------- Test report ----------\n'
            '\U0001F558 *Datetime start testing:*\n{datetimestart}\n'
            '\U0001F559 *Datetime end testing:*\n{datetimeend}\n'
            '\U0001F559 *Test duration:*\n{testsduration}\n\n'
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

    @pytest.hookimpl(tryfirst=True)
    def pytest_runtest_logreport(self, report: TestReport):
        if report.when == 'setup':
            if report.skipped:
                self.testsskipped += 1

    @pytest.hookimpl(trylast=True)
    def pytest_sessionstart(self):
        self.datetime_start_tests = datetime.now()

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

            datetimestart = self.datetime_start_tests
            datetimeend = datetime.now()
            datetimetotal = datetimeend - datetimestart

            kwargs = {
                'datetimestart': datetimestart.strftime('%H:%M:%S %d.%m.%Y'),
                'datetimeend': datetimeend.strftime('%H:%M:%S %d.%m.%Y'),
                'testsduration': str(datetimetotal).rsplit('.', maxsplit=1)[0],
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
                users_call_on_fail = self._bot.users_call_on_fail
                if len(users_call_on_fail) > 0:
                    kwargs.update({'mentioned': ', '.join(self._bot.users_call_on_fail)})
                else:
                    kwargs.update({'mentioned': '-'})
            else:
                kwargs.update({'mentioned': '-'})

            if session.testsfailed == 0:
                self._bot.send_passed_message(template, **kwargs)
            else:
                self._bot.send_failed_message(template, **kwargs)
