import base64
import io
import segno

from opentelemetry.trace import Status, StatusCode, SpanKind

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.auth import ExportLoginTokenRequest
from telethon.tl.types.auth import LoginTokenSuccess
from telethon.errors import (
    AuthTokenExpiredError,
    AuthTokenAlreadyAcceptedError,
    AuthTokenInvalidError,
)
from internal import interface, model

class LTelegramClient(interface.ITelegramClient):
    def __init__(
            self,
            tel: interface.ITelemetry,
            api_id: int,
            api_hash: str,
            session_string: str | None
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()

        self.api_id = api_id
        self.api_hash = api_hash
        self.session_string = session_string

        self.qr_session: model.QrSession = None
        self.userbot: TelegramClient = None

    async def generate_qr_code(self) -> io.BytesIO:
        with self.tracer.start_as_current_span(
                "UserbotClient.generate_qr_code",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                session = StringSession()
                client = TelegramClient(session, self.api_id, self.api_hash)
                await client.connect()

                self.qr_session = model.QrSession(
                    client=client,
                    string_session=session,
                    status=model.QRCodeStatus.PENDING
                )

                auth_result = await client(ExportLoginTokenRequest(
                    api_id=self.api_id,
                    api_hash=self.api_hash,
                    except_ids=[]
                ))

                token_b64url = base64.urlsafe_b64encode(auth_result.token).decode().rstrip('=')
                qr_url = f"tg://login?token={token_b64url}"

                qr = segno.make(qr_url)
                img_buffer = io.BytesIO()
                qr.save(img_buffer, kind='png', scale=8)
                img_buffer.seek(0)

                span.set_status(StatusCode.OK)
                return img_buffer

            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def qr_code_status(self) -> tuple[str, str]:
        with self.tracer.start_as_current_span(
                "UserbotClient.qr_code_status",
                kind=SpanKind.INTERNAL
        ) as span:
            try:

                auth_result = await self.qr_session.client(ExportLoginTokenRequest(
                    api_id=self.api_id,
                    api_hash=self.api_hash,
                    except_ids=[]
                ))

                if isinstance(auth_result, LoginTokenSuccess):
                    self.logger.info("QRCode успешно подтвержден")
                    self.session_string = self.qr_session.string_session.save()

                    self.userbot = self.qr_session.client

                    span.set_status(StatusCode.OK)
                    return model.QRCodeStatus.CONFIRMED, self.session_string
                else:
                    return model.QRCodeStatus.PENDING, ""

            except AuthTokenExpiredError:
                return model.QRCodeStatus.EXPIRED, ""
            except AuthTokenAlreadyAcceptedError:
                return model.QRCodeStatus.ERROR, ""
            except AuthTokenInvalidError:
                return model.QRCodeStatus.ERROR, ""
            except Exception as e:
                span.record_exception(e)
                span.set_status(StatusCode.ERROR, str(e))
                raise

    async def start(self):
        with self.tracer.start_as_current_span(
                "UserbotClient.start",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                client = TelegramClient(StringSession(self.session_string), self.api_id, self.api_hash)
                await client.connect()
                self.userbot = client

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise err

    async def send_message_to_telegram(
            self,
            tg_user_data: str,
            text: str
    ):
        with self.tracer.start_as_current_span(
                "UserbotClient.send_message_to_telegram",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_user_data": tg_user_data,
                    "text": text
                }
        ) as span:
            try:
                await self.userbot.send_message(tg_user_data, text)
                self.logger.debug("Отправили сообщение в телеграм")

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(e)
                span.set_status(StatusCode.ERROR, str(e))
                raise err