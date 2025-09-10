import base64
import io
import segno
import asyncio

from opentelemetry.trace import Status, StatusCode, SpanKind

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.auth import ExportLoginTokenRequest
from telethon.tl.types.auth import LoginTokenSuccess
from telethon.errors import (
    AuthTokenExpiredError,
    AuthTokenAlreadyAcceptedError,
    AuthTokenInvalidError,
    AuthKeyUnregisteredError,
    SessionPasswordNeededError
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
        self._auth_lock = asyncio.Lock()

    async def generate_qr_code(self) -> io.BytesIO:
        with self.tracer.start_as_current_span(
                "LTelegramClient.generate_qr_code",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                # Закрываем предыдущую сессию если есть
                if self.qr_session and self.qr_session.client:
                    try:
                        self.qr_session.client.disconnect()
                    except:
                        pass

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

                span.set_status(Status(StatusCode.OK))
                return img_buffer

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def qr_code_status(self) -> tuple[str, str]:
        with self.tracer.start_as_current_span(
                "LTelegramClient.qr_code_status",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                if not self.qr_session or not self.qr_session.client:
                    return model.QRCodeStatus.ERROR, ""

                # Проверяем подключение
                if not self.qr_session.client.is_connected():
                    await self.qr_session.client.connect()

                auth_result = await self.qr_session.client(ExportLoginTokenRequest(
                    api_id=self.api_id,
                    api_hash=self.api_hash,
                    except_ids=[]
                ))

                if isinstance(auth_result, LoginTokenSuccess):
                    self.logger.info("QR код успешно подтвержден")

                    # Сохраняем сессию и ждем полной инициализации
                    self.session_string = self.qr_session.string_session.save()

                    # Небольшая задержка для полной инициализации сессии
                    await asyncio.sleep(2)

                    # Обновляем основной клиент
                    if self.userbot:
                        try:
                            self.userbot.disconnect()
                        except:
                            pass

                    self.userbot = self.qr_session.client
                    self.qr_session.status = model.QRCodeStatus.CONFIRMED

                    # Проверяем что клиент авторизован
                    try:
                        await self.userbot.get_me()
                        self.logger.info("Клиент успешно авторизован")
                    except Exception as err:
                        raise err

                    span.set_status(Status(StatusCode.OK))
                    return model.QRCodeStatus.CONFIRMED, self.session_string
                else:
                    return model.QRCodeStatus.PENDING, ""

            except AuthTokenExpiredError:
                self.logger.warning("QR токен истек")
                return model.QRCodeStatus.EXPIRED, ""
            except AuthTokenAlreadyAcceptedError:
                self.logger.warning("QR токен уже использован")
                return model.QRCodeStatus.ERROR, ""
            except AuthTokenInvalidError:
                self.logger.warning("QR токен недействителен")
                return model.QRCodeStatus.ERROR, ""
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise err

    async def start(self):
        with self.tracer.start_as_current_span(
                "LTelegramClient.start",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                async with self._auth_lock:
                    if not self.session_string:
                        raise ValueError("Session string не найден")

                    # Закрываем предыдущий клиент если есть
                    if self.userbot:
                        try:
                            self.userbot.disconnect()
                        except:
                            pass

                    session = StringSession(self.session_string)
                    client = TelegramClient(session, self.api_id, self.api_hash)

                    await client.connect()

                    # Проверяем авторизацию
                    try:
                        me = await client.get_me()
                        self.logger.info("Клиент успешно запущен", {
                            "user_id": me.id,
                            "username": me.username
                        })
                        self.userbot = client
                    except AuthKeyUnregisteredError:
                        client.disconnect()
                        raise ValueError("Сессия недействительна, требуется повторная авторизация")
                    except SessionPasswordNeededError:
                        client.disconnect()
                        raise ValueError("Требуется двухфакторная аутентификация")

                span.set_status(Status(StatusCode.OK))

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def send_message_to_telegram(
            self,
            tg_user_data: str,
            text: str
    ):
        with self.tracer.start_as_current_span(
                "LTelegramClient.send_message_to_telegram",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_user_data": tg_user_data,
                }
        ) as span:
            try:
                async with self._auth_lock:
                    # Проверяем подключение
                    if not self.userbot.is_connected():
                        await self.userbot.connect()

                    await self.userbot.send_message(tg_user_data, text)


                span.set_status(Status(StatusCode.OK))

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def disconnect(self):
        """Метод для корректного отключения клиента"""
        try:
            if self.userbot:
                self.userbot.disconnect()
                self.userbot = None

            if self.qr_session and self.qr_session.client:
                self.qr_session.client.disconnect()
                self.qr_session = None

            self.logger.info("Telegram клиент отключен")
        except Exception as err:
            raise err