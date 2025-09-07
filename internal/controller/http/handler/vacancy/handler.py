from opentelemetry.trace import Status, StatusCode, SpanKind
from fastapi.responses import JSONResponse

from .model import *
from internal import interface


class VacancyController(interface.IVacancyController):
    def __init__(
            self,
            tel: interface.ITelemetry,
            vacancy_service: interface.IVacancyService,
    ):
        self.tracer = tel.tracer()
        self.vacancy_service = vacancy_service