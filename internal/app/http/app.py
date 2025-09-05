from fastapi import FastAPI

from internal import model, interface
from internal.controller.http.handler.interview.model import *
from internal.controller.http.handler.vacancy.model import *


def NewHTTP(
        db: interface.IDB,
        vacancy_controller: interface.IVacancyController,
        interview_controller: interface.IInterviewController,
        http_middleware: interface.IHttpMiddleware,
        prefix: str
):
    app = FastAPI(
        openapi_url=prefix+"/openapi.json",
        docs_url=prefix+"/docs",
        redoc_url=prefix+"/redoc",
    )
    include_middleware(app, http_middleware)
    include_db_handler(app, db, prefix)

    include_vacancy_handlers(app, vacancy_controller, prefix)
    include_interview_handlers(app, interview_controller, prefix)

    return app


def include_middleware(
        app: FastAPI,
        http_middleware: interface.IHttpMiddleware
):
    http_middleware.logger_middleware03(app)
    http_middleware.metrics_middleware02(app)
    http_middleware.trace_middleware01(app)


def include_vacancy_handlers(
        app: FastAPI,
        vacancy_controller: interface.IVacancyController,
        prefix: str
):
    app.add_api_route(
        prefix + "/create",
        vacancy_controller.create_vacancy,
        methods=["POST"],
        tags=["Vacancy Management"],

    )

    app.add_api_route(
        prefix + "/all",
        vacancy_controller.get_all_vacancy,
        methods=["GET"],
        tags=["Vacancy Management"],
        response_model=list[model.Vacancy]
    )

    app.add_api_route(
        prefix + "/delete/{vacancy_id}",
        vacancy_controller.delete_vacancy,
        methods=["DELETE"],
        tags=["Vacancy Management"],
    )

    app.add_api_route(
        prefix + "/question/generate",
        vacancy_controller.generate_question,
        methods=["POST"],
        tags=["Vacancy Questions"],
        response_model=GenerateQuestionResponse
    )

    app.add_api_route(
        prefix + "/question/add",
        vacancy_controller.add_question,
        methods=["POST"],
        tags=["Vacancy Questions"],
    )

    app.add_api_route(
        prefix + "/question/edit",
        vacancy_controller.edit_question,
        methods=["PUT"],
        tags=["Vacancy Questions"],
    )

    app.add_api_route(
        prefix + "/question/all",
        vacancy_controller.get_all_question,
        methods=["GET"],
        tags=["Vacancy Questions"],
        response_model=list[model.VacancyQuestion]
    )

    app.add_api_route(
        prefix + "/question/delete/{question_id}",
        vacancy_controller.delete_question,
        methods=["DELETE"],
        tags=["Vacancy Questions"],
    )

    app.add_api_route(
        prefix + "/criterion-weights/edit",
        vacancy_controller.edit_vacancy_criterion_weights,
        methods=["PUT"],
        tags=["Vacancy Management"],
    )


def include_interview_handlers(
        app: FastAPI,
        interview_controller: interface.IInterviewController,
        prefix: str
):
    app.add_api_route(
        prefix + "/interview/start",
        interview_controller.start_interview,
        methods=["POST"],
        tags=["Interview Management"],
        response_model=StartInterviewResponse
    )

    app.add_api_route(
        prefix + "/interview/answer",
        interview_controller.send_answer,
        methods=["POST"],
        tags=["Interview Management"],
        response_model=SendAnswerResponse
    )

    app.add_api_route(
        prefix + "/interview/all/{vacancy_id}",
        interview_controller.get_all_interview,
        methods=["GET"],
        tags=["Interview Management"],
        response_model=list[model.Interview]
    )

    app.add_api_route(
        prefix + "/interview/details/{interview_id}",
        interview_controller.get_candidate_answers,
        methods=["GET"],
        tags=["Interview Management"],
        response_model=GetCandidateAnswersResponse
    )


def include_db_handler(app: FastAPI, db: interface.IDB, prefix: str):
    app.add_api_route(prefix + "/table/create", create_table_handler(db), methods=["GET"])
    app.add_api_route(prefix + "/table/drop", drop_table_handler(db), methods=["GET"])


def create_table_handler(db: interface.IDB):
    async def create_table():
        try:
            await db.multi_query(model.create_all_tables_queries)
        except Exception as err:
            raise err

    return create_table


def drop_table_handler(db: interface.IDB):
    async def drop_table():
        try:
            await db.multi_query(model.drop_all_tables_queries)
        except Exception as err:
            raise err

    return drop_table