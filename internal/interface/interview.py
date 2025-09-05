from abc import abstractmethod
from typing import Protocol

from fastapi import UploadFile, Form
from fastapi.responses import JSONResponse

from internal import model


class IInterviewController(Protocol):
    @abstractmethod
    async def start_interview(
            self,
            vacancy_id: int = Form(...),
            candidate_email: str = Form(...),
            candidate_resume_file: UploadFile = Form(...)
    ) -> JSONResponse: pass

    @abstractmethod
    async def send_answer(
            self,
            vacancy_id: int = Form(...),
            question_id: int = Form(...),
            interview_id: int = Form(...),
            audio_file: UploadFile = Form(...)
    ) -> JSONResponse: pass

    @abstractmethod
    async def get_all_interview(self, vacancy_id: int) -> JSONResponse: pass

    @abstractmethod
    async def get_candidate_answers(self, interview_id: int) -> JSONResponse: pass


class IInterviewService(Protocol):
    @abstractmethod
    async def start_interview(
            self,
            vacancy_id: int,
            candidate_email: str,
            candidate_resume_file: UploadFile
    ) -> tuple[bool, int, str, int, int, int]:
        pass

    @abstractmethod
    async def send_answer(
            self,
            vacancy_id: int,
            question_id: int,
            interview_id: int,
            audio_file: UploadFile
    ) -> tuple[int, str, dict]:
        pass

    @abstractmethod
    async def get_all_interview(self, vacancy_id: int) -> list[model.Interview]: pass

    async def get_interview_by_id(
            self,
            interview_id: int
    ) -> tuple[list[model.CandidateAnswer], list[model.InterviewMessage]]: pass


class IInterviewRepo(Protocol):
    @abstractmethod
    async def create_interview(
            self,
            vacancy_id: int,
            candidate_email: str,
            candidate_resume_fid: str,
    ) -> int:
        pass

    @abstractmethod
    async def fill_interview_criterion(
            self,
            interview_id: int,
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
            general_recommendation: str,
            general_score: float,
            general_result: model.GeneralResult,
    ) -> int:
        pass

    @abstractmethod
    async def create_interview_message(
            self,
            interview_id: int,
            question_id: int,
            audio_fid: str,
            role: str,
            text: str,
    ) -> int:
        pass

    @abstractmethod
    async def create_candidate_answer(
            self,
            question_id: int,
            interview_id: int,
    ) -> int: pass

    @abstractmethod
    async def add_message_to_candidate_answer(
            self,
            message_id: int,
            candidate_answer_id: int
    ) -> None: pass

    @abstractmethod
    async def evaluation_candidate_answer(
            self,
            candidate_answer_id: int,
            score: int,
            llm_comment: str,
            response_time: int
    ) -> None: pass

    @abstractmethod
    async def get_candidate_answer(
            self,
            question_id: int,
            interview_id: int,
    ) -> list[model.CandidateAnswer]: pass

    @abstractmethod
    async def get_interview_by_id(self, interview_id: int) -> list[model.Interview]:
        pass

    @abstractmethod
    async def get_all_interview(self, vacancy_id: int) -> list[model.Interview]:
        pass

    @abstractmethod
    async def get_all_candidate_answer(self, interview_id: int) -> list[model.CandidateAnswer]:
        pass

    @abstractmethod
    async def get_interview_messages(self, interview_id: int) -> list[model.InterviewMessage]:
        pass


class IInterviewPromptGenerator(Protocol):
    @abstractmethod
    def get_resume_evaluation_system_prompt(
            self,
            vacancy_description: str,
            vacancy_red_flags: str,
            vacancy_name: str,
            vacancy_tags: list[str]
    ) -> str:
        pass

    @abstractmethod
    def get_interview_management_system_prompt(
            self,
            vacancy: model.Vacancy,
            questions: list[model.VacancyQuestion],
    ) -> str: pass

    @abstractmethod
    def get_answer_evaluation_system_prompt(
            self,
            question: model.VacancyQuestion,
            vacancy: model.Vacancy
    ) -> str: pass

    @abstractmethod
    def get_interview_summary_system_prompt(
            self,
            vacancy: model.Vacancy
    ) -> str: pass

    @abstractmethod
    def get_question_generation_prompt(
            self,
            vacancy: model.Vacancy,
            count_questions: int,
            questions_type: model.QuestionsType,
    ) -> str: pass
