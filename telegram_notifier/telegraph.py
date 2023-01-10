import uuid
from configparser import ConfigParser

from telegraph import Telegraph


class TelegramTelegraph:
    def __init__(self, parser: ConfigParser, /):
        self._parser = parser
        self._telegraph = Telegraph()
        self._telegraph.create_account(str(uuid.uuid4())[:4], str(uuid.uuid4()))

    @property
    def is_enabled(self) -> bool:
        return self._parser.get('Telegram:Telegraph', 'enabled', fallback='false').lower() == 'true'

    @property
    def use_stacktrace(self) -> bool:
        return self._parser.get('Telegram:Telegraph', 'stacktrace', fallback='false').lower() == 'true'

    def create_page(self, title: str, /, stacktrace: list[tuple[str, str]] = None) -> str:
        html_content = ''

        if self.use_stacktrace and isinstance(stacktrace, list):
            html_content += '<h3>Stacktrace</h3>'
            for fspath, trace in stacktrace:
                html_content += f'<h4><b>Test path:</b> {fspath}</h4>'
                html_content += trace.replace('\n', '<br />')

        if len(html_content) > 0:
            response = self._telegraph.create_page(title, html_content=html_content)
            return response.get('url')
        return ''
