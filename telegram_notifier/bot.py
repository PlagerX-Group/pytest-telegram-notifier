import configparser
from datetime import datetime

from telebot import TeleBot


class TelegramBot:
    def __init__(self, configuration_path: str, /):
        parser = configparser.ConfigParser()
        parser.read(configuration_path)

        self._chat_id = parser['Telegram']['chat-id']
        self._telegram_bot = TeleBot(parser['Telegram']['access-token'])

    def __del__(self):
        self._telegram_bot.stop_bot()

    def send_message(self, template: str, **kwargs) -> None:
        self._telegram_bot.send_message(
            self._chat_id,
            template.format(**kwargs).encode(encoding='utf-8'),
            parse_mode='markdown',
        )
