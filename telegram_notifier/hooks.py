import pytest
from _pytest.config import Config


@pytest.hookspec
def pytest_telegram_notifier_init_settings():
    pass


@pytest.hookspec
def pytest_telegram_notifier_message_template(additional_fields: dict):
    pass


@pytest.hookspec
def pytest_telegram_notifier_message_additional_fields(config: Config):
    pass
