from abc import abstractmethod
from typing import Protocol

from fastapi import FastAPI, UploadFile
from opentelemetry.metrics import Meter
from opentelemetry.trace import Tracer
from weed.util import WeedOperationResponse

from internal import model
from internal.controller.http.handler.vacancy.model import *

class IInterviewController(Protocol):
    @abstractmethod
    def start_interview(self, body: StartInterviewBody) -> StartInterviewResponse:
        pass

    @abstractmethod
    def send_answer(self, vacancy_id: int, question_id: int, audio_file: UploadFile) -> int:
        pass


class IInterviewService(Protocol):
    @abstractmethod
    def create_interview(
            self,
            vacancy_id: int,
            candidate_email: str,
            candidate_resume_fid: str,
    ) -> int:
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
            role: str,
            text: str,
    ) -> int:
        pass

    @abstractmethod
    def create_candidate_answer(
            self,
            question_id: int,
            interview_id: int,
            duration: int,
            text: str,
            audio_fid: str,
            llm_comment: str,
            score: int
    ) -> int: pass
