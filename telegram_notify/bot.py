import configparser

from telebot import TeleBot


class TelegramBot:

    def __init__(self, configuration_path: str, /):
        parser = configparser.ConfigParser()
        parser.read(configuration_path)

        self._chat_id = parser['Telegram']['chat-id']
        self._telegram_bot = TeleBot(parser['Telegram']['access-token'])

    def __del__(self):
        self._telegram_bot.stop_bot()

    def send_message(
        self,
        teststotal: int,
        testspassed: int,
        testsfailed: int,
        testsskipped: int,
        /,
        template: str,
    ) -> None:
        self._telegram_bot.send_message(
            self._chat_id,
            template.format(
                teststotal=teststotal,
                testsfailed=testsfailed,
                testspassed=testspassed,
                testsskipped=testsskipped,
            ),
        )