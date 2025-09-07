import io
import json
from datetime import datetime

from fastapi import UploadFile

from internal import model, interface


class InterviewService(interface.IInterviewService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            vacancy_repo: interface.IVacancyRepo,
            interview_repo: interface.IInterviewRepo,
            interview_prompt_generator: interface.IInterviewPromptGenerator,
            llm_client: interface.ILLMClient,
            storage: interface.IStorage
    ):
        self.logger = tel.logger()

        self.vacancy_repo = vacancy_repo
        self.interview_repo = interview_repo
        self.interview_prompt_generator = interview_prompt_generator
        self.llm_client = llm_client
        self.storage = storage

