import pytest
from _pytest.config.argparsing import Parser
from _pytest.fixtures import Config
from pluggy import PluginManager


@pytest.hookimpl
def pytest_addoption(parser: Parser):
    group = parser.getgroup("telegram_notify")
    group.addoption(
        "--telegram-notify",
        action="store_true",
        dest="telegram_notify",
    )
    group.addoption(
        "--telegram-notify-config-file",
        action="store",
        dest="telegram_notify_config_file",
        default="pytest-telegram-notify.ini",
    )


@pytest.hookimpl
def pytest_addhooks(pluginmanager: PluginManager):
    from . import hooks

    pluginmanager.add_hookspecs(hooks)


@pytest.hookimpl(trylast=True)
def pytest_configure(config: Config):
    if not config.option.telegram_notify:
        return

    from .telegram_manager import TelegramManager

    manager = TelegramManager(config)
    config.pluginmanager.register(manager, "telegram_notifier")
