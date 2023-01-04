import configparser

from telebot import TeleBot


class TelegramBot:
    def __init__(self, configuration_path: str, /) -> None:
        parser = configparser.ConfigParser()
        parser.read(configuration_path)

        self._chat_id = parser['Telegram']['chat-id']
        self._telegram_bot = TeleBot(parser['Telegram']['access-token'])

    def _send_message(self, template: str, **kwargs) -> None:
        self._telegram_bot.send_message(
            self._chat_id,
            template.format(**kwargs).encode(encoding='utf-8'),
            parse_mode='markdown',
        )
