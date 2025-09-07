from opentelemetry.trace import SpanKind, Status, StatusCode

from .sql_query import *
from internal import interface, model


class VacancyRepo(interface.IVacancyRepo):
    def __init__(self, tel: interface.ITelemetry, db: interface.IDB):
        self.db = db
        self.tracer = tel.tracer()