import json
from datetime import datetime

from opentelemetry.trace import SpanKind, Status, StatusCode

from internal import interface, model


class VacancyService(interface.IVacancyService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            vacancy_repo: interface.IVacancyRepo,
            interview_repo: interface.IInterviewRepo,
            storage: interface.IStorage,
            vacancy_prompt_generator: interface.IVacancyPromptGenerator,
            llm_client: interface.ILLMClient,
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.vacancy_repo = vacancy_repo
        self.interview_repo = interview_repo
        self.storage = storage
        self.vacancy_prompt_generator = vacancy_prompt_generator
        self.llm_client = llm_client
