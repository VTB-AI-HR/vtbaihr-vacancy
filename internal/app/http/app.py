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
    pass


def include_interview_handlers(
        app: FastAPI,
        interview_controller: interface.IInterviewController,
        prefix: str
):
    pass


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