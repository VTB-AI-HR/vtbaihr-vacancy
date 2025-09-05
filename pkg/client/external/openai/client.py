import base64
import io

import httpx
import fitz

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
            llm_model: str = "gpt-4o-mini",
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
                    if llm_model in ["gpt-4o", "gpt-4o-mini"]:
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

    def _extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        """Извлекает текст из PDF файла"""
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text

    def _pdf_to_images(self, pdf_bytes: bytes) -> list[str]:
        """Конвертирует PDF страницы в base64 изображения"""
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        images = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            # Конвертируем страницу в изображение
            mat = fitz.Matrix(2, 2)  # увеличиваем разрешение
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")

            # Кодируем в base64
            base64_image = base64.b64encode(img_data).decode('utf-8')
            images.append(base64_image)

        doc.close()
        return images