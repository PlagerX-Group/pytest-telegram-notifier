import configparser
import enum
import os
import typing as t

from telebot import TeleBot
from telebot.apihelper import ApiTelegramException


@enum.unique
class CallModeEnum(enum.Enum):
    ALWAYS: str = 'always'
    ON_FAIL: str = 'on_fail'


class TelegramBot:
    def __init__(self, configuration_path: str, /) -> None:
        self._parser = configparser.ConfigParser()
        self._parser.read(configuration_path)

        self._chat_id = self._parser.get('Telegram', 'chat-id')
        self._telegram_bot = TeleBot(os.getenv('TELEGRAM_ACCESS_TOKEN'))

    @property
    def mode(self) -> CallModeEnum:
        if value := self._parser.get('Telegram:CallOnFail', 'mode', fallback=None):
            try:
                return CallModeEnum(value)
            except ValueError:
                pass
        return CallModeEnum.ON_FAIL

    @property
    def parse_mode(self) -> str:
        return self._parser.get('Telegram', 'parse_mode', fallback='markdown')

    @property
    def users_call_on_fail(self) -> list[str]:
        if self._parser.get('Telegram:CallOnFail', 'enabled', fallback='false').lower() == 'true':
            return self._parser.get('Telegram:CallOnFail', 'usernames', fallback=[]).split(' ')
        return []

    def format_template(self, template: str, **kwargs) -> str:
        return template.format(**kwargs).encode(encoding='utf-8')

    def _send_single_message(self, template: str, **kwargs) -> None:
        self._telegram_bot.send_message(
            self._chat_id,
            self.format_template(template, **kwargs),
            parse_mode=self.parse_mode,
        )

    def _send_message(self, sticker_code: t.Optional[str], template: str, **kwargs) -> None:
        if sticker_code:
            try:
                sticker_message = self._telegram_bot.send_sticker(self._chat_id, sticker_code)
                self._telegram_bot.reply_to(
                    sticker_message,
                    self.format_template(template, **kwargs),
                    parse_mode=self.parse_mode,
                )
            except ApiTelegramException:
                self._send_single_message(template, **kwargs)
        else:
            self._send_single_message(template, **kwargs)

    def send_passed_message(self, template: str, **kwargs) -> None:
        self._send_message(
            self._parser.get('Telegram:Stickers', 'on-passed', fallback=None),
            template,
            **kwargs,
        )

    def send_failed_message(self, template: str, **kwargs) -> None:
        self._send_message(
            self._parser.get('Telegram:Stickers', 'on-failed', fallback=None),
            template,
            **kwargs,
        )
