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
    async def create_vacancy_criterion_weight(self, body: CreateVacancyCriterionWeightBody) -> JSONResponse: pass

    @abstractmethod
    async def create_resume_weight(self, body: CreateWeightBody) -> JSONResponse: pass

    @abstractmethod
    async def generate_tags(self, vacancy_id: int) -> JSONResponse: pass

    @abstractmethod
    async def generate_question(self, body: GenerateQuestionBody) -> JSONResponse: pass

    async def evaluate_resume(self, candidate_resume_files: list[UploadFile] = File(...)) -> JSONResponse: pass

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
    pass


class IVacancyRepo(Protocol):
    pass


class IVacancyPromptGenerator(Protocol):
    pass