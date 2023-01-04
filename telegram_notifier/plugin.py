import pytest
from _pytest.config.argparsing import Parser
from _pytest.fixtures import Config, FixtureRequest
from pluggy import PluginManager

from .telegram_manager import TelegramManager, TelegramManagerAdditionalFieldsWorker


@pytest.hookimpl
def pytest_addoption(parser: Parser):
    group = parser.getgroup("telegram_notifier")
    group.addoption(
        "--telegram-notifier",
        action="store_true",
        dest="telegram_notifier",
    )
    group.addoption(
        "--telegram-notifier-config-file",
        action="store",
        dest="telegram_notifier_config_file",
        default="pytest-telegram-notifier.ini",
    )


@pytest.hookimpl
def pytest_addhooks(pluginmanager: PluginManager):
    from . import hooks

    pluginmanager.add_hookspecs(hooks)


@pytest.hookimpl(trylast=True)
def pytest_configure(config: Config):
    if not config.option.telegram_notifier:
        return

    manager = TelegramManager(config)
    config.pluginmanager.register(manager, "telegram_notifier_2")


@pytest.fixture(scope="session")
def telegram_notifier_bot(request: FixtureRequest) -> TelegramManagerAdditionalFieldsWorker:
    return request.config.pluginmanager.get_plugin('telegram_notifier_2').additional_fields_worker
