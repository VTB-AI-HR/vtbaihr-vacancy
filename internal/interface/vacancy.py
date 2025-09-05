from abc import abstractmethod
from typing import Protocol

from fastapi import FastAPI, UploadFile
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
    async def generate_question(self, body: GenerateQuestionBody) -> JSONResponse: pass

    @abstractmethod
    async def add_question(self, body: AddQuestionBody) -> JSONResponse: pass

    @abstractmethod
    async def edit_question(self, body: EditQuestionBody) -> JSONResponse: pass

    @abstractmethod
    async def delete_question(self, question_id: int) -> JSONResponse: pass

    @abstractmethod
    async def edit_vacancy_criterion_weights(self, body: EditVacancyCriterionWeightsBody) -> JSONResponse: pass

    @abstractmethod
    async def get_all_vacancy(self) -> JSONResponse: pass


class IVacancyService(Protocol):
    @abstractmethod
    async def create_vacancy(
            self,
            name: str,
            tags: list[str],
            description: str,
            red_flags: str,
            skill_lvl: model.SkillLevel,
            question_response_time: int,
            questions_type: model.QuestionsType
    ) -> int: pass

    @abstractmethod
    async def delete_vacancy(self, vacancy_id: int) -> None: pass

    @abstractmethod
    async def generate_questions(
            self,
            vacancy_id: int,
            questions_type: model.QuestionsType,
            count_questions: int
    ) -> list[dict]: pass

    @abstractmethod
    async def add_question(
            self,
            vacancy_id: int,
            question: str,
            hint_for_evaluation: str,
            weight: int,
            question_type: model.QuestionsType
    ) -> int: pass

    @abstractmethod
    async def edit_question(
            self,
            question_id: int,
            vacancy_id: int,
            question: str | None,
            hint_for_evaluation: str | None,
            weight: int | None,
            question_type: model.QuestionsType | None
    ) -> None: pass

    @abstractmethod
    async def delete_question(self, question_id: int) -> None: pass

    @abstractmethod
    async def edit_vacancy_criterion_weights(
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
            red_flag_score_weight: int | None
    ) -> None: pass

    @abstractmethod
    async def get_all_vacancy(self) -> list[model.Vacancy]: pass


class IVacancyRepo(Protocol):
    @abstractmethod
    async def create_vacancy(
            self,
            name: str,
            tags: list[str],
            description: str,
            red_flags: str,
            skill_lvl: model.SkillLevel,
            question_response_time: int,
            questions_type: model.QuestionsType
    ) -> int: pass

    @abstractmethod
    async def delete_vacancy(self, vacancy_id: int) -> None: pass

    @abstractmethod
    async def add_question(
            self,
            vacancy_id: int,
            question: str,
            hint_for_evaluation: str,
            weight: int,  # [0;10]
            question_type: model.QuestionsType
    ) -> int: pass

    @abstractmethod
    async def edit_question(
            self,
            question_id: int,
            vacancy_id: int,
            question: str | None,
            hint_for_evaluation: str | None,
            weight: int | None,  # [0;10]
            question_type: model.QuestionsType | None
    ) -> None: pass

    @abstractmethod
    async def delete_question(self, question_id: int) -> None: pass

    @abstractmethod
    async def edit_vacancy_criterion_weights(
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
            red_flag_score_weight: int | None
    ) -> None: pass

    @abstractmethod
    async def get_all_vacancy(self) -> list[model.Vacancy]: pass

    @abstractmethod
    async def get_all_question(self, vacancy_id: int) -> list[model.VacancyQuestion]: pass

    @abstractmethod
    async def get_vacancy_by_id(self, vacancy_id: int) -> list[model.Vacancy]: pass
