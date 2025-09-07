from opentelemetry.trace import Status, StatusCode, SpanKind
from fastapi import UploadFile, Form
from fastapi.responses import JSONResponse

from .model import *
from internal import interface


class InterviewController(interface.IInterviewController):
    def __init__(
            self,
            tel: interface.ITelemetry,
            interview_service: interface.IInterviewService,
    ):
        self.tracer = tel.tracer()
        self.interview_service = interview_service