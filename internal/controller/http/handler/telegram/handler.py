from opentelemetry.trace import Status, StatusCode, SpanKind
from fastapi.responses import JSONResponse
from starlette.responses import StreamingResponse

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

    async def generate_qr_code(self) -> StreamingResponse:
        with self.tracer.start_as_current_span(
                "TelegramHTTPController.generate_qr_code",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                self.logger.info("Generating QR code for Telegram authorization")

                qr_image = await self.telegram_client.generate_qr_code()

                self.logger.info("QR code generated successfully")

                def iterfile():
                    try:
                        qr_image.seek(0)
                        while True:
                            chunk = qr_image.read(8192)
                            if not chunk:
                                break
                            yield chunk
                    finally:
                        qr_image.close()

                span.set_status(Status(StatusCode.OK))
                return StreamingResponse(
                    iterfile(),
                    media_type="image/png",
                    headers={
                        "Content-Disposition": "inline; filename=telegram_qr.png",
                        "Cache-Control": "no-cache"
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def check_qr_status(self) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "TelegramHTTPController.check_qr_status",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                self.logger.info("Checking QR code status")

                status, session_string = await self.telegram_client.qr_code_status()

                self.logger.info("QR code status checked", {
                    "status": status,
                    "has_session": bool(session_string)
                })

                response_data = {
                    "status": status,
                    "session_string": session_string if status == "confirmed" else None
                }

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content=response_data
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def start_telegram_client(self) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "TelegramHTTPController.start_telegram_client",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                self.logger.info("Starting Telegram client")

                await self.telegram_client.start()

                self.logger.info("Telegram client started successfully")

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={"message": "Telegram client started successfully"}
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err