from abc import abstractmethod
from typing import Protocol

from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse
from opentelemetry.metrics import Meter
from opentelemetry.trace import Tracer

from internal.controller.http.handler.vacancy.model import *


class IVacancyController(Protocol):
    pass


class IVacancyService(Protocol):
    pass


class IVacancyRepo(Protocol):
    pass


class IVacancyPromptGenerator(Protocol):
    pass