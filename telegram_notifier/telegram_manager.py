import copy
import os
from datetime import datetime

import pytest
from _pytest.config import Config
from _pytest.main import Session
from _pytest.nodes import Item

from telegram_notifier.bot import TelegramBot


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

    @pytest.hookimpl
    def pytest_telegram_notifier_message_template(self, additional_fields: dict) -> str:
        template = (
            "---------- Test report ----------\n"
            "\U0001F55B *Datetime start testing:* {datetimestart}\n"
            "\U0001F567 *Datetime end testing:* {datetimeend}\n\n"
            "\U0001F3AE *Count tests:* {teststotal}\n"
            "\U0001F534 *Tests failed:* {testsfailed}\n"
            "\U0001F7E2 *Tests passed:* {testspassed}\n"
            "\U000026AA *Tests skipped:* {testsskipped}"
        )
        if isinstance(additional_fields, dict) and additional_fields:
            template += "\n\n------- Additional fields -------\n"
            for key, value in additional_fields.items():
                template += f"\U000025AA *{key}:* {value}\n"
        template = template.replace('_', r'\_')
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
                for markers in [item.own_markers for item in items]
                if 'skip' in [marker.name for marker in markers]
            ]
        )

    @pytest.hookimpl
    def pytest_sessionfinish(self, session: Session):
        self._additional_fields_worker.register_additional_fields(
            self._config.hook.pytest_telegram_notifier_message_additional_fields(config=self._config)[0]
        )

        template = self._config.hook.pytest_telegram_notifier_message_template(
            additional_fields=self.additional_fields_worker.fields,
        )[0]

        self._bot._send_message(
            template,
            datetimestart=self.datetime_start_tests.strftime('%H:%M:%S %d.%m.%Y'),
            datetimeend=datetime.now().strftime('%H:%M:%S %d.%m.%Y'),
            teststotal=self.teststotal,
            testspassed=self.teststotal - session.testsfailed - self.testsskipped,
            testsfailed=session.testsfailed,
            testsskipped=self.testsskipped,
        )
