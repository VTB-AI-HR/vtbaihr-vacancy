from opentelemetry.trace import Status, StatusCode, SpanKind
from fastapi.responses import JSONResponse
from .model import *
from internal import interface

class TelegramHTTPController(interface.ITelegramHTTPController):
    def __init__(
            self,
            tel: interface.ITelemetry,
            telegram_client: interface.ITelegramClient,
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.telegram_client = telegram_client