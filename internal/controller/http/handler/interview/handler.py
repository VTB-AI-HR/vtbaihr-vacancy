from opentelemetry.trace import Status, StatusCode, SpanKind
from fastapi import UploadFile, Form, Path, File
from fastapi.responses import JSONResponse
from starlette.responses import StreamingResponse

from internal import interface


class InterviewController(interface.IInterviewController):
    def __init__(
            self,
            tel: interface.ITelemetry,
            interview_service: interface.IInterviewService,
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.interview_service = interview_service

    async def start_interview(self, interview_id: int) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "InterviewController.start_interview",
                kind=SpanKind.INTERNAL,
                attributes={"interview_id": interview_id}
        ) as span:
            try:
                self.logger.info("Starting interview request", {"interview_id": interview_id})

                message_to_candidate, total_questions, question_id, llm_audio_filename, llm_audio_fid = await self.interview_service.start_interview(
                    interview_id
                )

                self.logger.info("Interview started successfully", {
                    "interview_id": interview_id,
                    "total_questions": total_questions,
                    "first_question_id": question_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "message_to_candidate": message_to_candidate,
                        "total_question": total_questions,
                        "question_id": question_id,
                        "llm_audio_filename": llm_audio_filename,
                        "llm_audio_fid": llm_audio_fid,
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def send_answer(
            self,
            interview_id: int = Form(...),
            question_id: int = Form(...),
            audio_file: UploadFile = File(...)
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "InterviewController.send_answer",
                kind=SpanKind.INTERNAL,
                attributes={
                    "question_id": question_id,
                    "interview_id": interview_id,
                }
        ) as span:
            try:
                self.logger.info("Processing answer request", {
                    "question_id": question_id,
                    "interview_id": interview_id,
                    "content_type": audio_file.content_type
                })

                next_question_id, message_to_candidate, interview_result, llm_audio_filename, llm_audio_fid = await self.interview_service.send_answer(
                    interview_id=interview_id,
                    question_id=question_id,
                    audio_file=audio_file
                )

                self.logger.info("Answer processed successfully", {
                    "question_id": question_id,
                    "interview_id": interview_id,
                    "next_question_id": next_question_id,
                    "has_interview_result": bool(interview_result)
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "question_id": next_question_id,
                        "message_to_candidate": message_to_candidate,
                        "interview_result": interview_result,
                        "llm_audio_filename": llm_audio_filename,
                        "llm_audio_fid": llm_audio_fid,
                    }
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_all_interview(self, vacancy_id: int = Path(...)) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "InterviewController.get_all_interview",
                kind=SpanKind.INTERNAL,
                attributes={"vacancy_id": vacancy_id}
        ) as span:
            try:
                self.logger.info("Getting all interviews request", {"vacancy_id": vacancy_id})

                interviews = await self.interview_service.get_all_interview(vacancy_id)
                interviews_dict = [interview.to_dict() for interview in interviews]

                self.logger.info("All interviews retrieved successfully", {
                    "vacancy_id": vacancy_id,
                    "interviews_count": len(interviews)
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content=interviews_dict
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_interview_by_id(self, interview_id: int = Path(...)) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "InterviewController.get_interview_by_id",
                kind=SpanKind.INTERNAL,
                attributes={"interview_id": interview_id}
        ) as span:
            try:
                self.logger.info("Getting interview by ID request", {"interview_id": interview_id})

                interview = await self.interview_service.get_interview_by_id(interview_id)
                interview_dict = interview.to_dict()

                self.logger.info("Interview retrieved successfully", {
                    "interview_id": interview_id,
                    "vacancy_id": interview.vacancy_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content=interview_dict
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_interview_details(self, interview_id: int = Path(...)) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "InterviewController.get_interview_details",
                kind=SpanKind.INTERNAL,
                attributes={"interview_id": interview_id}
        ) as span:
            try:
                self.logger.info("Getting interview details request", {"interview_id": interview_id})

                candidate_answers, interview_messages = await self.interview_service.get_interview_details(
                    interview_id
                )
                candidate_answers_dict = [answer.to_dict() for answer in candidate_answers]
                interview_messages_dict = [message.to_dict() for message in interview_messages]

                self.logger.info("Interview details retrieved successfully", {
                    "interview_id": interview_id,
                    "candidate_answers_count": len(candidate_answers),
                    "interview_messages_count": len(interview_messages)
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "candidate_answers": candidate_answers_dict,
                        "interview_messages": interview_messages_dict
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def download_audio(
            self,
            audio_fid: str = Path(...),
            audio_filename: str = Path(...)
    ) -> StreamingResponse:
        with self.tracer.start_as_current_span(
                "InterviewController.download_audio",
                kind=SpanKind.INTERNAL,
                attributes={
                    "audio_fid": audio_fid,
                    "audio_filename": audio_filename
                }
        ) as span:
            try:
                self.logger.info("Downloading audio file", {
                    "audio_fid": audio_fid,
                    "audio_filename": audio_filename
                })

                audio_stream, content_type = await self.interview_service.download_audio(audio_fid, audio_filename)

                # Определяем MIME тип для аудио файлов
                if not content_type or content_type == "application/octet-stream":
                    if audio_filename.lower().endswith(('.mp3', '.mpeg')):
                        content_type = "audio/mpeg"
                    elif audio_filename.lower().endswith('.wav'):
                        content_type = "audio/wav"
                    elif audio_filename.lower().endswith('.ogg'):
                        content_type = "audio/ogg"
                    elif audio_filename.lower().endswith('.m4a'):
                        content_type = "audio/mp4"
                    else:
                        content_type = "audio/mpeg"  # default

                def iterfile():
                    try:
                        while True:
                            chunk = audio_stream.read(8192)  # Читаем по 8KB
                            if not chunk:
                                break
                            yield chunk
                    finally:
                        audio_stream.close()

                self.logger.info("Audio file downloaded successfully", {
                    "audio_fid": audio_fid,
                    "audio_filename": audio_filename,
                    "content_type": content_type
                })

                span.set_status(Status(StatusCode.OK))
                return StreamingResponse(
                    iterfile(),
                    media_type=content_type,
                    headers={
                        "Content-Disposition": f"attachment; filename={audio_filename}",
                        "Cache-Control": "no-cache",
                        "Accept-Ranges": "bytes"
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def download_resume(
            self,
            resume_fid: str = Path(...),
            resume_filename: str = Path(...)
    ) -> StreamingResponse:
        with self.tracer.start_as_current_span(
                "InterviewController.download_resume",
                kind=SpanKind.INTERNAL,
                attributes={"resume_fid": resume_fid, "resume_filename": resume_filename}
        ) as span:
            try:
                # Получаем поток файла резюме из сервиса
                resume_stream, content_type = await self.interview_service.download_resume(
                    resume_fid,
                    resume_filename
                )

                # Определяем MIME тип для резюме
                if not content_type or content_type == "application/octet-stream":
                    if resume_filename.lower().endswith('.pdf'):
                        content_type = "application/pdf"
                    elif resume_filename.lower().endswith(('.doc', '.docx')):
                        content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    elif resume_filename.lower().endswith('.txt'):
                        content_type = "text/plain"
                    else:
                        content_type = "application/octet-stream"  # default

                def iterfile():
                    try:
                        while True:
                            chunk = resume_stream.read(8192)  # Читаем по 8KB
                            if not chunk:
                                break
                            yield chunk
                    finally:
                        resume_stream.close()

                span.set_status(Status(StatusCode.OK))
                return StreamingResponse(
                    iterfile(),
                    media_type=content_type,
                    headers={
                        "Content-Disposition": f"attachment; filename={resume_filename}",
                        "Cache-Control": "no-cache",
                        "Accept-Ranges": "bytes"
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err
