from abc import abstractmethod
from typing import Protocol

from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse
from opentelemetry.metrics import Meter
from opentelemetry.trace import Tracer
from weed.util import WeedOperationResponse

from internal import model
from internal.controller.http.handler.interview.model import *


class IInterviewController(Protocol):
    @abstractmethod
    def start_interview(
            self,
            vacancy_id: int,
            candidate_email: str,
            candidate_resume_file: UploadFile
    ) -> JSONResponse:
        pass

    @abstractmethod
    def send_answer(
            self,
            vacancy_id: int,
            question_id: int,
            audio_file: UploadFile
    ) -> JSONResponse:
        pass

    @abstractmethod
    def get_all_interview(self, vacancy_id: int) -> JSONResponse:
        pass


class IInterviewService(Protocol):
    @abstractmethod
    def start_interview(
            self,
            vacancy_id: int,
            candidate_email: str,
            candidate_resume_file: UploadFile
    ) -> tuple[bool, str]:
        pass

    @abstractmethod
    def send_answer(
            self,
            vacancy_id: int,
            question_id: int,
            audio_file: UploadFile
    ) -> SendAnswerResponse:
        pass


class IInterviewRepo(Protocol):
    @abstractmethod
    def create_interview(
            self,
            vacancy_id: int,
            candidate_email: str,
            candidate_resume_fid: str,
    ) -> int:
        pass

    @abstractmethod
    def fill_interview_criterion(
            self,
            interview_id: str,
            red_flag_score: float,
            hard_skill_score: float,
            soft_skill_score: float,
            logic_structure_score: float,
            accordance_xp_vacancy_score: float,
            accordance_skill_vacancy_score: float,
            accordance_xp_resume_score: float,
            accordance_skill_resume_score: float,
            strong_areas: str,
            weak_areas: str,
            pause_detection_score: float,
            emotional_coloring: str
    ) -> int:
        pass

    @abstractmethod
    def add_general_result(
            self,
            vacancy_id: int,
            general_score: float,
            general_result: model.GeneralResult,
            general_recommendation: str
    ) -> int:
        pass

    @abstractmethod
    def create_interview_message(
            self,
            interview_id: str,
            question_id: int,
            audio_fid: str,
            role: str,
            text: str,
    ) -> int:
        pass

    @abstractmethod
    def create_candidate_answer(
            self,
            question_id: int,
            interview_id: int,
            message_id: int
    ) -> int: pass

    @abstractmethod
    def add_message_to_candidate_answer(
            self,
            message_id: int,
            candidate_answer_id: int
    ) -> None: pass

    @abstractmethod
    def evaluation_candidate_answer(
            self,
            candidate_answer_id: int,
            score: int,
            llm_comment: str,
            response_time: int
    ) -> None: pass

    @abstractmethod
    def get_interview_by_id(self, interview_id: int) -> list[model.Interview]:
        pass

    @abstractmethod
    def get_candidate_answers(self, interview_id: int) -> list[model.CandidateAnswer]:
        pass

    @abstractmethod
    def get_interview_messages(self, interview_id: int) -> list[model.InterviewMessage]:
        pass
