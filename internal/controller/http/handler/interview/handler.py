from opentelemetry.trace import Status, StatusCode, SpanKind
from fastapi import UploadFile, Form
from fastapi.responses import JSONResponse

from .model import *
from internal import interface


class InterviewController(interface.IInterviewController):
    def __init__(
            self,
            tel: interface.ITelemetry,
            interview_service: interface.IInterviewService,
    ):
        self.tracer = tel.tracer()
        self.interview_service = interview_service

    async def start_interview(
            self,
            vacancy_id: int = Form(...),
            candidate_email: str = Form(...),
            candidate_resume_file: UploadFile = Form(...)
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "InterviewController.start_interview",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": vacancy_id,
                    "candidate_email": candidate_email,
                    "resume_filename": candidate_resume_file.filename,
                }
        ) as span:
            try:
                is_suitable, resume_accordance_score, message_to_candidate, total_question, interview_id, question_id = await self.interview_service.start_interview(
                    vacancy_id=vacancy_id,
                    candidate_email=candidate_email,
                    candidate_resume_file=candidate_resume_file
                )

                response = StartInterviewResponse(
                    is_suitable=is_suitable,
                    resume_accordance_score=resume_accordance_score,
                    message_to_candidate=message_to_candidate,
                    total_question=total_question,
                    interview_id=interview_id,
                    question_id=question_id
                )

                span.set_attributes({
                    "is_suitable": is_suitable,
                    "resume_accordance_score": resume_accordance_score,
                    "message_to_candidate": message_to_candidate,
                    "total_question": total_question,
                    "interview_id": interview_id,
                    "question_id": question_id,
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content=response.model_dump()
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def send_answer(
            self,
            vacancy_id: int = Form(...),
            question_id: int = Form(...),
            interview_id: int = Form(...),
            audio_file: UploadFile = Form(...)
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "InterviewController.send_answer",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": vacancy_id,
                    "question_id": question_id,
                    "audio_filename": audio_file.filename,
                }
        ) as span:
            try:
                next_question_id, message_to_candidate, interview_result = await self.interview_service.send_answer(
                    vacancy_id=vacancy_id,
                    question_id=question_id,
                    interview_id=interview_id,
                    audio_file=audio_file
                )

                response = SendAnswerResponse(
                    question_id=next_question_id,
                    message_to_candidate=message_to_candidate,
                    interview_result=interview_result
                )

                span.set_attributes({
                    "next_question_id": next_question_id,
                    "interview_finished": bool(interview_result)
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content=response.model_dump()
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_all_interview(self, vacancy_id: int) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "InterviewController.get_all_interview",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": vacancy_id,
                }
        ) as span:
            try:
                interviews = await self.interview_service.get_all_interview(vacancy_id)

                span.set_attributes({
                    "interviews_count": len(interviews)
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content=[interview.to_dict() for interview in interviews]
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_candidate_answers(self, interview_id: int) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "InterviewController.get_candidate_answers",
                kind=SpanKind.INTERNAL,
                attributes={
                    "interview_id": interview_id,
                }
        ) as span:
            try:
                candidate_answers, interview_messages = await self.interview_service.get_interview_by_id(interview_id)

                span.set_attributes({
                    "candidate_answers_count": len(candidate_answers),
                    "interview_messages_count": len(interview_messages)
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "candidate_answers": [answer.to_dict() for answer in candidate_answers],
                        "interview_messages": [interview_message.to_dict() for interview_message in interview_messages]
                    }
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err
