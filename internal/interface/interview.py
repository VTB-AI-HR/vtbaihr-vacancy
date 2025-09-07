from abc import abstractmethod
from typing import Protocol

from fastapi import UploadFile, Form
from fastapi.responses import JSONResponse

from internal import model


class IInterviewController(Protocol):
    @abstractmethod
    async def start_interview(self, interview_id: int) -> JSONResponse:
        pass

    @abstractmethod
    async def send_answer(
            self,
            vacancy_id: int,
            question_id: int,
            interview_id: int,
            audio_file: UploadFile
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def get_all_interview(self, vacancy_id: int) -> list[model.Interview]: pass

    async def get_interview_by_id(
            self,
            interview_id: int
    ) -> tuple[list[model.CandidateAnswer], list[model.InterviewMessage]]: pass


class IInterviewService(Protocol):
    pass


class IInterviewRepo(Protocol):
    pass

class IInterviewPromptGenerator(Protocol):
    pass