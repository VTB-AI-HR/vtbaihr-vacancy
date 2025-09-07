from abc import abstractmethod
from typing import Protocol

from fastapi import FastAPI, UploadFile, Form, File
from fastapi.responses import JSONResponse
from opentelemetry.metrics import Meter
from opentelemetry.trace import Tracer

from internal.controller.http.handler.vacancy.model import *


class IVacancyController(Protocol):
    @abstractmethod
    async def create_vacancy(self, body: CreateVacancyBody) -> JSONResponse: pass

    @abstractmethod
    async def delete_vacancy(self, vacancy_id: int) -> JSONResponse: pass

    @abstractmethod
    async def edit_vacancy(self, body: EditVacancyBody) -> JSONResponse: pass

    @abstractmethod
    async def add_question(self, body: AddQuestionBody) -> JSONResponse: pass

    @abstractmethod
    async def edit_question(self, body: EditQuestionBody) -> JSONResponse: pass

    @abstractmethod
    async def create_vacancy_criterion_weight(self, body: CreateVacancyCriterionWeightBody) -> JSONResponse: pass

    @abstractmethod
    async def edit_vacancy_criterion_weight(self, body: EditVacancyCriterionWeightBody) -> JSONResponse: pass

    @abstractmethod
    async def create_resume_weight(self, body: CreateResumeWeightBody) -> JSONResponse: pass

    @abstractmethod
    async def edit_resume_weight(self, body: CreateResumeWeightBody) -> JSONResponse: pass

    @abstractmethod
    async def generate_tags(self, body: GenerateTagsBody) -> JSONResponse: pass

    @abstractmethod
    async def generate_question(self, body: GenerateQuestionBody) -> JSONResponse: pass

    @abstractmethod
    async def evaluate_resume(self, candidate_resume_files: list[UploadFile] = File(...)) -> JSONResponse: pass

    @abstractmethod
    async def respond(
            self,
            vacancy_id: int,
            candidate_email: str,
            candidate_resume_file: UploadFile
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def get_all_vacancy(self) -> JSONResponse: pass

    @abstractmethod
    async def get_all_question(self, vacancy_id: int) -> JSONResponse: pass


class IVacancyService(Protocol):
    @abstractmethod
    async def create_vacancy(
            self,
            name: str,
            tags: list[str],
            description: str,
            red_flags: str,
            skill_lvl: model.SkillLevel,
    ) -> int: pass

    @abstractmethod
    async def delete_vacancy(self, vacancy_id: int) -> None: pass

    @abstractmethod
    async def edit_vacancy(
            self,
            vacancy_id: int,
            name: str | None,
            tags: list[str] | None,
            description: str | None,
            red_flags: str | None,
            skill_lvl: model.SkillLevel | None,
    ) -> None: pass

    @abstractmethod
    async def add_question(
            self,
            vacancy_id: int,
            question: str,
            hint_for_evaluation: str,
            weight: int,
            question_type: model.QuestionsType,
            response_time: int,
    ) -> int: pass

    @abstractmethod
    async def edit_question(
            self,
            vacancy_id: int,
            question: str | None,
            hint_for_evaluation: str | None,
            weight: int | None,
            question_type: model.QuestionsType | None,
            response_time: int | None,
    ) -> int: pass

    @abstractmethod
    async def create_vacancy_criterion_weight(
            self,
            vacancy_id: int,
            logic_structure_score_weight: int,
            pause_detection_score_weight: int,
            soft_skill_score_weight: int,
            hard_skill_score_weight: int,
            accordance_xp_vacancy_score_weight: int,
            accordance_skill_vacancy_score_weight: int,
            accordance_xp_resume_score_weight: int,
            accordance_skill_resume_score_weight: int,
            red_flag_score_weight: int,
    ) -> None: pass

    @abstractmethod
    async def edit_vacancy_criterion_weight(
            self,
            vacancy_id: int,
            logic_structure_score_weight: int | None,
            pause_detection_score_weight: int | None,
            soft_skill_score_weight: int | None,
            hard_skill_score_weight: int | None,
            accordance_xp_vacancy_score_weight: int | None,
            accordance_skill_vacancy_score_weight: int | None,
            accordance_xp_resume_score_weight: int | None,
            accordance_skill_resume_score_weight: int | None,
            red_flag_score_weight: int | None,
    ) -> None: pass

    @abstractmethod
    async def create_resume_weight(
            self,
            vacancy_id: int,
            hard_skill_weight: int,
            work_xp_weight: int,
            recommendation_weight: int,
            portfolio_weight: int,
    ) -> None: pass

    @abstractmethod
    async def edit_resume_weight(
            self,
            vacancy_id: int,
            hard_skill_weight: int | None,
            work_xp_weight: int | None,
            recommendation_weight: int | None,
            portfolio_weight: int | None,
    ) -> None: pass

    @abstractmethod
    async def generate_tags(self, vacancy_description: str) -> list[str]: pass

    @abstractmethod
    async def generate_question(
            self,
            vacancy_id: int,
            questions_type: model.QuestionsType,
            count_questions: int,
    ) -> list[model.VacancyQuestion]: pass

    @abstractmethod
    async def evaluate_resume(self, candidate_resume_files: list[UploadFile]) -> list[model.Interview]: pass

    @abstractmethod
    async def respond(
            self,
            vacancy_id: int,
            candidate_email: str,
            candidate_resume_file: UploadFile
    ) -> tuple[str, int, int]:
        pass

    @abstractmethod
    async def get_all_vacancy(self) -> list[model.Vacancy]: pass

    @abstractmethod
    async def get_all_question(self, vacancy_id: int) -> list[model.VacancyQuestion]: pass


class IVacancyRepo(Protocol):
    @abstractmethod
    async def create_vacancy(
            self,
            name: str,
            tags: list[str],
            description: str,
            red_flags: str,
            skill_lvl: model.SkillLevel,
    ) -> int: pass

    @abstractmethod
    async def delete_vacancy(self, vacancy_id: int) -> None: pass

    @abstractmethod
    async def edit_vacancy(
            self,
            vacancy_id: int,
            name: str | None,
            tags: list[str] | None,
            description: str | None,
            red_flags: str | None,
            skill_lvl: model.SkillLevel | None,
    ) -> None: pass

    @abstractmethod
    async def add_question(
            self,
            vacancy_id: int,
            question: str,
            hint_for_evaluation: str,
            weight: int,
            question_type: model.QuestionsType,
            response_time: int,
    ) -> int: pass

    @abstractmethod
    async def create_vacancy_criterion_weight(
            self,
            vacancy_id: int,
            logic_structure_score_weight: int,
            pause_detection_score_weight: int,
            soft_skill_score_weight: int,
            hard_skill_score_weight: int,
            accordance_xp_vacancy_score_weight: int,
            accordance_skill_vacancy_score_weight: int,
            accordance_xp_resume_score_weight: int,
            accordance_skill_resume_score_weight: int,
            red_flag_score_weight: int,
    ) -> None: pass

    @abstractmethod
    async def edit_vacancy_criterion_weight(
            self,
            vacancy_id: int,
            logic_structure_score_weight: int | None,
            pause_detection_score_weight: int | None,
            soft_skill_score_weight: int | None,
            hard_skill_score_weight: int | None,
            accordance_xp_vacancy_score_weight: int | None,
            accordance_skill_vacancy_score_weight: int | None,
            accordance_xp_resume_score_weight: int | None,
            accordance_skill_resume_score_weight: int | None,
            red_flag_score_weight: int | None,
    ) -> None: pass

    @abstractmethod
    async def create_resume_weight(
            self,
            vacancy_id: int,
            hard_skill_weight: int,
            work_xp_weight: int,
            recommendation_weight: int,
            portfolio_weight: int,
    ) -> None: pass

    @abstractmethod
    async def edit_resume_weight(
            self,
            vacancy_id: int,
            hard_skill_weight: int | None,
            work_xp_weight: int | None,
            recommendation_weight: int | None,
            portfolio_weight: int | None,
    ) -> None: pass

    @abstractmethod
    async def get_all_vacancy(self) -> list[model.Vacancy]: pass

    @abstractmethod
    async def get_all_question(self, vacancy_id: int) -> list[model.VacancyQuestion]: pass



class IVacancyPromptGenerator(Protocol):
    @abstractmethod
    def get_question_generation_prompt(
            self,
            vacancy: model.Vacancy,
            count_questions: int,
            questions_type: model.QuestionsType,
    ) -> str: pass

    @abstractmethod
    def get_resume_evaluation_system_prompt(
            self,
            vacancy_description: str,
            vacancy_red_flags: str,
            vacancy_name: str,
            vacancy_tags: list[str]
    ) -> str: pass
