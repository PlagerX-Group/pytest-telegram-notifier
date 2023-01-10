import pytest
from _pytest.config.argparsing import Parser
from _pytest.fixtures import Config, FixtureRequest
from pluggy import PluginManager

from . import hooks
from .telegram_manager import TelegramManager, TelegramManagerAdditionalFieldsWorker


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


def pytest_configure(config: Config):
    if not config.option.telegram_notifier:
        return

    if not hasattr(config, 'workerinput'):
        manager = TelegramManager(config)
        config.pluginmanager.register(manager, 'pytest_telegram_notifier')


def pytest_unconfigure(config: Config):
    if not hasattr(config, 'workerinput'):
        config.pluginmanager.unregister(name='pytest_telegram_notifier')


@pytest.fixture(scope='session')
def telegram_notifier_bot(request: FixtureRequest) -> TelegramManagerAdditionalFieldsWorker:
    return request.config.pluginmanager.get_plugin('pytest_telegram_notifier').additional_fields_worker
