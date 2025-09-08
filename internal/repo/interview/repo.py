from opentelemetry.trace import SpanKind, Status, StatusCode

from .sql_query import *
from internal import model
from internal import interface


class InterviewRepo(interface.IInterviewRepo):
    def __init__(self, tel: interface.ITelemetry, db: interface.IDB):
        self.db = db
        self.tracer = tel.tracer()

    async def create_interview(
            self,
            vacancy_id: int,
            candidate_name: str,
            candidate_email: str,
            candidate_phone: str,
            candidate_resume_fid: str,
            accordance_xp_vacancy_score: int,
            accordance_skill_vacancy_score: int,
    ) -> int:
        with self.tracer.start_as_current_span(
                "InterviewRepo.create_interview",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": vacancy_id,
                    "candidate_email": candidate_email,
                }
        ) as span:
            try:
                args = {
                    'vacancy_id': vacancy_id,
                    'candidate_name': candidate_name,
                    'candidate_email': candidate_email,
                    'candidate_phone': candidate_phone,
                    'candidate_resume_fid': candidate_resume_fid,
                    'accordance_xp_vacancy_score': accordance_xp_vacancy_score,
                    'accordance_skill_vacancy_score': accordance_skill_vacancy_score,
                    'general_result': model.GeneralResult.IN_PROCESS.value
                }
                interview_id = await self.db.insert(create_interview, args)

                span.set_status(Status(StatusCode.OK))
                return interview_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def create_candidate_answer(
            self,
            question_id: int,
            interview_id: int,
    ) -> int:
        with self.tracer.start_as_current_span(
                "InterviewRepo.create_candidate_answer",
                kind=SpanKind.INTERNAL,
                attributes={
                    "question_id": question_id,
                    "interview_id": interview_id,
                }
        ) as span:
            try:
                args = {
                    'question_id': question_id,
                    'interview_id': interview_id,
                }
                candidate_answer_id = await self.db.insert(create_candidate_answer, args)

                span.set_status(Status(StatusCode.OK))
                return candidate_answer_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def create_interview_message(
            self,
            interview_id: int,
            question_id: int,
            audio_fid: str,
            role: str,
            text: str,
    ) -> int:
        with self.tracer.start_as_current_span(
                "InterviewRepo.create_interview_message",
                kind=SpanKind.INTERNAL,
                attributes={
                    "interview_id": interview_id,
                    "question_id": question_id,
                    "role": role,
                }
        ) as span:
            try:
                args = {
                    'interview_id': interview_id,
                    'question_id': question_id,
                    'audio_fid': audio_fid,
                    'role': role,
                    'text': text,
                }
                message_id = await self.db.insert(create_interview_message, args)

                span.set_status(Status(StatusCode.OK))
                return message_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def add_message_to_candidate_answer(
            self,
            message_id: int,
            candidate_answer_id: int
    ) -> None:
        with self.tracer.start_as_current_span(
                "InterviewRepo.add_message_to_candidate_answer",
                kind=SpanKind.INTERNAL,
                attributes={
                    "message_id": message_id,
                    "candidate_answer_id": candidate_answer_id,
                }
        ) as span:
            try:
                args = {
                    'message_id': message_id,
                    'candidate_answer_id': candidate_answer_id,
                }
                await self.db.update(add_message_to_candidate_answer, args)

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def evaluation_candidate_answer(
            self,
            candidate_answer_id: int,
            score: int,
            message_to_candidate: str,
            message_to_hr: str,
            response_time: int
    ) -> None:
        with self.tracer.start_as_current_span(
                "InterviewRepo.evaluation_candidate_answer",
                kind=SpanKind.INTERNAL,
                attributes={
                    "candidate_answer_id": candidate_answer_id,
                    "score": score,
                }
        ) as span:
            try:
                args = {
                    'candidate_answer_id': candidate_answer_id,
                    'score': score,
                    'message_to_candidate': message_to_candidate,
                    'message_to_hr': message_to_hr,
                    'response_time': response_time,
                }
                await self.db.update(evaluation_candidate_answer, args)

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def fill_interview_criterion(
            self,
            interview_id: int,
            red_flag_score: int,
            hard_skill_score: int,
            soft_skill_score: int,
            logic_structure_score: int,
            accordance_xp_resume_score: int,
            accordance_skill_resume_score: int,
            strong_areas: str,
            weak_areas: str,
            general_score: float,
            general_result: model.GeneralResult,
            message_to_candidate: str,
            message_to_hr: str,
    ) -> None:
        with self.tracer.start_as_current_span(
                "InterviewRepo.fill_interview_criterion",
                kind=SpanKind.INTERNAL,
                attributes={
                    "interview_id": interview_id,
                    "general_score": general_score,
                    "general_result": general_result.value,
                }
        ) as span:
            try:
                args = {
                    'interview_id': interview_id,
                    'red_flag_score': red_flag_score,
                    'hard_skill_score': hard_skill_score,
                    'soft_skill_score': soft_skill_score,
                    'logic_structure_score': logic_structure_score,
                    'accordance_xp_resume_score': accordance_xp_resume_score,
                    'accordance_skill_resume_score': accordance_skill_resume_score,
                    'strong_areas': strong_areas,
                    'weak_areas': weak_areas,
                    'general_score': general_score,
                    'general_result': general_result.value,
                    'message_to_candidate': message_to_candidate,
                    'message_to_hr': message_to_hr,
                }
                await self.db.update(fill_interview_criterion, args)

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_candidate_answer(
            self,
            question_id: int,
            interview_id: int,
    ) -> list[model.CandidateAnswer]:
        with self.tracer.start_as_current_span(
                "InterviewRepo.get_candidate_answer",
                kind=SpanKind.INTERNAL,
                attributes={
                    "question_id": question_id,
                    "interview_id": interview_id,
                }
        ) as span:
            try:
                args = {
                    'question_id': question_id,
                    'interview_id': interview_id,
                }
                rows = await self.db.select(get_candidate_answer, args)
                candidate_answers = model.CandidateAnswer.serialize(rows) if rows else []

                span.set_status(Status(StatusCode.OK))
                return candidate_answers
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_interview_by_id(self, interview_id: int) -> list[model.Interview]:
        with self.tracer.start_as_current_span(
                "InterviewRepo.get_interview_by_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "interview_id": interview_id,
                }
        ) as span:
            try:
                args = {'interview_id': interview_id}
                rows = await self.db.select(get_interview_by_id, args)
                interviews = model.Interview.serialize(rows) if rows else []

                span.set_status(Status(StatusCode.OK))
                return interviews
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_all_interview(self, vacancy_id: int) -> list[model.Interview]:
        with self.tracer.start_as_current_span(
                "InterviewRepo.get_all_interview",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": vacancy_id,
                }
        ) as span:
            try:
                args = {'vacancy_id': vacancy_id}
                rows = await self.db.select(get_all_interview, args)
                interviews = model.Interview.serialize(rows) if rows else []

                span.set_status(Status(StatusCode.OK))
                return interviews
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_all_candidate_answer(self, interview_id: int) -> list[model.CandidateAnswer]:
        with self.tracer.start_as_current_span(
                "InterviewRepo.get_all_candidate_answer",
                kind=SpanKind.INTERNAL,
                attributes={
                    "interview_id": interview_id,
                }
        ) as span:
            try:
                args = {'interview_id': interview_id}
                rows = await self.db.select(get_all_candidate_answer, args)
                candidate_answers = model.CandidateAnswer.serialize(rows) if rows else []

                span.set_status(Status(StatusCode.OK))
                return candidate_answers
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_interview_messages(self, interview_id: int) -> list[model.InterviewMessage]:
        with self.tracer.start_as_current_span(
                "InterviewRepo.get_interview_messages",
                kind=SpanKind.INTERNAL,
                attributes={
                    "interview_id": interview_id,
                }
        ) as span:
            try:
                args = {'interview_id': interview_id}
                rows = await self.db.select(get_interview_messages, args)
                messages = model.InterviewMessage.serialize(rows) if rows else []

                span.set_status(Status(StatusCode.OK))
                return messages
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err
