from opentelemetry.trace import Status, StatusCode, SpanKind
from fastapi import UploadFile, Form, Path, File
from fastapi.responses import JSONResponse

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

                message_to_candidate, total_questions, question_id = await self.interview_service.start_interview(
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
                        "question_id": question_id
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

                next_question_id, message_to_candidate, interview_result = await self.interview_service.send_answer(
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
                        "interview_result": interview_result
                    }
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_all_interview(self, vacancy_id: int = Path(...)) -> JSONResponse:
        """Получает все интервью для указанной вакансии"""
        with self.tracer.start_as_current_span(
                "InterviewController.get_all_interview",
                kind=SpanKind.INTERNAL,
                attributes={"vacancy_id": vacancy_id}
        ) as span:
            try:
                self.logger.info("Getting all interviews request", {"vacancy_id": vacancy_id})

                interviews = await self.interview_service.get_all_interview(vacancy_id)

                # Конвертируем в словари для JSON ответа
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

    async def get_interview_details(self, interview_id: int = Path(...)) -> JSONResponse:
        """Получает детали интервью включая ответы кандидата и сообщения"""
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

                # Конвертируем в словари для JSON ответа
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

            except ValueError as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                self.logger.warning("Interview not found", {
                    "interview_id": interview_id,
                    "error": str(err)
                })
                return JSONResponse(
                    status_code=404,
                    content={"error": "Interview not found"}
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err