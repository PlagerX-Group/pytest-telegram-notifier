import pytest


@pytest.hookspec
def pytest_telegram_notify_init_settings():
    pass


@pytest.hookspec
def pytest_telegram_notify_message_template():
    pass
