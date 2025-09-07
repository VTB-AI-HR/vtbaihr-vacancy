from abc import abstractmethod
from typing import Protocol

from fastapi import UploadFile, Form
from fastapi.responses import JSONResponse

from internal import model


class IInterviewController(Protocol):
    pass


class IInterviewService(Protocol):
    pass


class IInterviewRepo(Protocol):
    pass

class IInterviewPromptGenerator(Protocol):
    pass