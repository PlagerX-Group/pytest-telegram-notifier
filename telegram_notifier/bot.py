import configparser
import os
import typing as t

from telebot import TeleBot
from telebot.apihelper import ApiTelegramException


class TelegramBot:
    def __init__(self, configuration_path: str, /) -> None:
        self._parser = configparser.ConfigParser()
        self._parser.read(configuration_path)

        self._chat_id = self._parser.get('Telegram', 'chat-id')
        self._telegram_bot = TeleBot(os.getenv('TELEGRAM_ACCESS_TOKEN'))

    def _send_message(self, sticker_code: t.Optional[str], template: str, **kwargs):
        if sticker_code:
            try:
                sticker_message = self._telegram_bot.send_sticker(self._chat_id, sticker_code)
                self._telegram_bot.reply_to(
                    sticker_message,
                    template.format(**kwargs).encode(encoding='utf-8'),
                    parse_mode='markdown',
                )
            except ApiTelegramException:
                self._telegram_bot.send_message(
                    self._chat_id,
                    template.format(**kwargs).encode(encoding='utf-8'),
                    parse_mode='markdown',
                )
        else:
            self._telegram_bot.send_message(
                self._chat_id,
                template.format(**kwargs).encode(encoding='utf-8'),
                parse_mode='markdown',
            )

    def send_passed_message(self, template: str, **kwargs):
        self._send_message(
            self._parser.get('Telegram:Stickers', 'on-passed', fallback=None),
            template,
            **kwargs,
        )

    def send_failed_message(self, template: str, **kwargs):
        self._send_message(
            self._parser.get('Telegram:Stickers', 'on-failed', fallback=None),
            template,
            **kwargs,
        )
