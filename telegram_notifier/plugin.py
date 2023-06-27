import pytest
from _pytest.config.argparsing import Parser
from _pytest.fixtures import Config
from pluggy import PluginManager

from . import hooks
from .telegram_manager import TelegramManager


def pytest_addoption(parser: Parser):
    group = parser.getgroup('telegram_notifier')
    group.addoption(
        '--telegram-notifier',
        action='store_true',
        dest='telegram_notifier',
    )
    group.addoption(
        '--telegram-notifier-config-file',
        action='store',
        dest='telegram_notifier_config_file',
        default='pytest-telegram-notifier.ini',
    )


def pytest_addhooks(pluginmanager: PluginManager):
    pluginmanager.add_hookspecs(hooks)


@pytest.mark.tryfirst
def pytest_cmdline_main(config: Config):
    if config.option.telegram_notifier:
        manager = TelegramManager(config)
        config.pluginmanager.register(manager, 'pytest_telegram_notifier')
