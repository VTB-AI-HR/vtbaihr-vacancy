from fastapi import FastAPI, Path, Form, File, UploadFile
from typing import List

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
        openapi_url=prefix + "/openapi.json",
        docs_url=prefix + "/docs",
        redoc_url=prefix + "/redoc",
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
    # Создание вакансии
    app.add_api_route(
        prefix + "/create",
        vacancy_controller.create_vacancy,
        methods=["POST"],
    )

    # Удаление вакансии
    app.add_api_route(
        prefix + "/delete/{vacancy_id}",
        vacancy_controller.delete_vacancy,
        methods=["DELETE"],
    )

    # Редактирование вакансии
    app.add_api_route(
        prefix + "/edit",
        vacancy_controller.edit_vacancy,
        methods=["PUT"],
    )

    # Добавление вопроса к вакансии
    app.add_api_route(
        prefix + "/question/add",
        vacancy_controller.add_question,
        methods=["POST"],
    )

    # Редактирование вопроса
    app.add_api_route(
        prefix + "/question/edit",
        vacancy_controller.edit_question,
        methods=["PUT"],
    )

    # Удаление вопроса
    app.add_api_route(
        prefix + "/question/delete/{question_id}",
        vacancy_controller.delete_question,
        methods=["DELETE"],
    )

    # Создание весов критериев вакансии
    app.add_api_route(
        prefix + "/criterion-weight/create",
        vacancy_controller.create_vacancy_criterion_weight,
        methods=["POST"]
    )

    # Редактирование весов критериев вакансии
    app.add_api_route(
        prefix + "/criterion-weight/edit",
        vacancy_controller.edit_vacancy_criterion_weight,
        methods=["PUT"],
    )

    # Создание весов резюме
    app.add_api_route(
        prefix + "/resume-weight/create",
        vacancy_controller.create_resume_weight,
        methods=["POST"],
    )

    # Редактирование весов резюме
    app.add_api_route(
        prefix + "/resume-weight/edit",
        vacancy_controller.edit_resume_weight,
        methods=["PUT"],
    )

    # Генерация тегов
    app.add_api_route(
        prefix + "/generate-tags",
        vacancy_controller.generate_tags,
        methods=["POST"],
        response_model=GenerateTagsResponse,
    )

    # Генерация вопросов
    app.add_api_route(
        prefix + "/question/generate",
        vacancy_controller.generate_question,
        methods=["POST"],
        response_model=GenerateQuestionResponse,
    )

    # Оценка резюме (множественная)
    app.add_api_route(
        prefix + "/evaluate-resumes",
        vacancy_controller.evaluate_resume,
        methods=["POST"],
        response_model=EvaluateResumeResponse,
    )

    # Отклик на вакансию (одиночное резюме)
    app.add_api_route(
        prefix + "/respond",
        vacancy_controller.respond,
        methods=["POST"],
        response_model=RespondResponse,
    )

    # Получение всех вакансий
    app.add_api_route(
        prefix + "/all",
        vacancy_controller.get_all_vacancy,
        methods=["GET"],
        response_model=list[model.Vacancy],
    )

    # Получение всех вопросов вакансии
    app.add_api_route(
        prefix + "/question/all/{vacancy_id}",
        vacancy_controller.get_all_question,
        methods=["GET"],
        response_model=list[model.VacancyQuestion],
    )


def include_interview_handlers(
        app: FastAPI,
        interview_controller: interface.IInterviewController,
        prefix: str
):
    # Начало интервью
    app.add_api_route(
        prefix + "/interview/start/{interview_id}",
        interview_controller.start_interview,
        methods=["POST"],
        response_model=StartInterviewResponse,
    )

    # Отправка ответа на вопрос интервью
    app.add_api_route(
        prefix + "/interview/answer",
        interview_controller.send_answer,
        methods=["POST"],
        response_model=SendAnswerResponse,
    )

    # Получение всех интервью для вакансии
    app.add_api_route(
        prefix + "/interview/vacancy/{vacancy_id}",
        interview_controller.get_all_interview,
        methods=["GET"],
        response_model=list[model.Interview],
    )

    # Получение деталей интервью
    app.add_api_route(
        prefix + "/interview/{interview_id}/details",
        interview_controller.get_interview_details,
        methods=["GET"],
        response_model=GetCandidateAnswersResponse,
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
