import base64
import io

import httpx
import pypdf
from pdf2image import convert_from_bytes

import openai
from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface
from internal import model


class GPTClient(interface.ILLMClient):
    def __init__(
            self,
            tel: interface.ITelemetry,
            api_key: str
    ):
        self.tracer = tel.tracer()
        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            http_client=httpx.AsyncClient()
        )

    async def generate(
            self,
            history: list[model.InterviewMessage],
            system_prompt: str = "",
            temperature: float = 0.5,
            llm_model: str = "gpt-5",
            pdf_file: bytes = None,
    ) -> str:
        with self.tracer.start_as_current_span(
                "GPTClient.generate",
                kind=SpanKind.CLIENT,
        ) as span:
            try:
                if system_prompt != "":
                    system_prompt = [{"role": "system", "content": system_prompt}]

                history = [
                    *system_prompt,
                    *[
                        {"role": message.role, "content": message.text}
                        for message in history
                    ]
                ]

                if pdf_file is not None:
                    if llm_model in ["gpt-5", "gpt-4o", "gpt-4o-mini"]:
                        # Подход 1: Конвертируем PDF в изображения (для vision моделей)
                        images = self._pdf_to_images(pdf_file)

                        content = [
                            {"type": "text", "text": history[-1]["content"]}
                        ]

                        # Добавляем каждую страницу как изображение
                        for i, img_base64 in enumerate(images):
                            content.append({
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_base64}",
                                    "detail": "high"
                                }
                            })

                        history[-1]["content"] = content
                    else:
                        # Подход 2: Извлекаем текст из PDF
                        pdf_text = self._extract_text_from_pdf(pdf_file)
                        original_text = history[-1]["content"]
                        history[-1]["content"] = f"{original_text}\n\nСодержимое PDF:\n{pdf_text}"

                response = await self.client.chat.completions.create(
                    model=llm_model,
                    messages=history,
                    temperature=temperature,
                )
                llm_response = response.choices[0].message.content

                span.set_status(Status(StatusCode.OK))
                return llm_response

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    async def transcribe_audio(
            self,
            audio_file: bytes,
            filename: str = "audio.wav"
    ) -> str:
        with self.tracer.start_as_current_span(
                "GPTClient.transcribe_audio",
                kind=SpanKind.CLIENT,
        ) as span:
            try:
                audio_buffer = io.BytesIO(audio_file)
                audio_buffer.name = filename

                transcript = await self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_buffer,
                    response_format="text"
                )

                span.set_status(Status(StatusCode.OK))
                return transcript

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    async def text_to_speech(
            self,
            text: str,
            voice: str = "alloy",
            tts_model: str = "tts-1-hd"
    ) -> bytes:
        with self.tracer.start_as_current_span(
                "GPTClient.text_to_speech",
                kind=SpanKind.CLIENT,
        ) as span:
            try:
                response = await self.client.audio.speech.create(
                    model=tts_model,
                    voice=voice,
                    input=text,
                    response_format="mp3",
                    speed=0.85,
                )

                audio_content = response.content

                span.set_status(Status(StatusCode.OK))
                return audio_content

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    def _extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        with self.tracer.start_as_current_span(
                "GPTClient._extract_text_from_pdf",
                kind=SpanKind.CLIENT,
        ) as span:
            try:
                """Извлекает текст из PDF файла"""
                reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return text
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    def _pdf_to_images(self, pdf_bytes: bytes) -> list[str]:
        with self.tracer.start_as_current_span(
                "GPTClient._pdf_to_images",
                kind=SpanKind.CLIENT,
        ) as span:
            try:
                images = convert_from_bytes(pdf_bytes, dpi=200)

                base64_images = []
                for img in images:
                    # Конвертируем PIL Image в base64
                    buffer = io.BytesIO()
                    img.save(buffer, format='PNG')
                    img_data = buffer.getvalue()
                    base64_image = base64.b64encode(img_data).decode('utf-8')
                    base64_images.append(base64_image)

                return base64_images
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err
