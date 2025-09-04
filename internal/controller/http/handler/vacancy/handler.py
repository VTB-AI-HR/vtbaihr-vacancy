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

    async def create_vacancy(self, body: CreateVacancyBody) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "VacancyController.create_vacancy",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_name": body.name,
                    "skill_level": body.skill_lvl.value,
                    "tags_count": len(body.tags),
                    "question_response_time": body.question_response_time,
                }
        ) as span:
            try:
                vacancy_id = await self.vacancy_service.create_vacancy(
                    name=body.name,
                    tags=body.tags,
                    description=body.description,
                    red_flags=body.red_flags,
                    skill_lvl=body.skill_lvl,
                    question_response_time=body.question_response_time,
                    questions_type=model.QuestionsType.SOFT_HARD  # Default value
                )

                span.set_attributes({"vacancy_id": vacancy_id})
                span.set_status(Status(StatusCode.OK))

                return JSONResponse(
                    status_code=201,
                    content={
                        "vacancy_id": vacancy_id,
                        "message": "Вакансия успешно создана"
                    }
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def delete_vacancy(self, vacancy_id: int) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "VacancyController.delete_vacancy",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": vacancy_id,
                }
        ) as span:
            try:
                await self.vacancy_service.delete_vacancy(vacancy_id)

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={"message": f"Вакансия с ID {vacancy_id} успешно удалена"}
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))

                raise err

    async def generate_question(self, body: GenerateQuestionBody) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "VacancyController.generate_question",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": body.vacancy_id,
                    "questions_type": body.questions_type.value,
                    "count_questions": body.count_questions,
                }
        ) as span:
            try:
                questions = await self.vacancy_service.generate_questions(
                    vacancy_id=body.vacancy_id,
                    questions_type=body.questions_type,
                    count_questions=body.count_questions
                )

                span.set_attributes({
                    "generated_count": len(questions)
                })
                span.set_status(Status(StatusCode.OK))

                return JSONResponse(
                    status_code=200,
                    content=questions
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))

                raise err

    async def add_question(self, body: AddQuestionBody) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "VacancyController.add_question",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": body.vacancy_id,
                    "question_type": body.question_type.value,
                    "weight": body.weight,
                }
        ) as span:
            try:
                question_id, order_number = await self.vacancy_service.add_question(
                    vacancy_id=body.vacancy_id,
                    question=body.question,
                    hint_for_evaluation=body.hint_for_evaluation,
                    weight=body.weight,
                    question_type=body.question_type
                )

                span.set_attributes({
                    "question_id": question_id,
                    "order_number": order_number
                })
                span.set_status(Status(StatusCode.OK))

                return JSONResponse(
                    status_code=201,
                    content={
                        "question_id": question_id,
                        "order_number": order_number,
                        "message": "Вопрос успешно добавлен"
                    }
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))

                raise err

    async def edit_question(self, body: EditQuestionBody) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "VacancyController.edit_question",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": body.vacancy_id,
                    "question_type": body.question_type.value if body.question_type else None,
                    "weight": body.weight,
                }
        ) as span:
            try:
                await self.vacancy_service.edit_question(
                    question_id=body.question_id,
                    vacancy_id=body.vacancy_id,
                    question=body.question,
                    hint_for_evaluation=body.hint_for_evaluation,
                    weight=body.weight,
                    question_type=body.question_type
                )

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={"message": "Вопрос успешно обновлен"}
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))

                raise err

    async def delete_question(self, question_id: int) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "VacancyController.delete_question",
                kind=SpanKind.INTERNAL,
                attributes={
                    "question_id": question_id,
                }
        ) as span:
            try:
                await self.vacancy_service.delete_question(question_id)

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={"message": f"Вопрос с ID {question_id} успешно удален"}
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def edit_vacancy_criterion_weights(self, body: EditVacancyCriterionWeightsBody) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "VacancyController.edit_vacancy_criterion_weights",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": body.vacancy_id,
                }
        ) as span:
            try:
                await self.vacancy_service.edit_vacancy_criterion_weights(
                    vacancy_id=body.vacancy_id,
                    logic_structure_score_weight=body.logic_structure_score_weight,
                    pause_detection_score_weight=body.pause_detection_score_weight,
                    soft_skill_score_weight=body.soft_skill_score_weight,
                    hard_skill_score_weight=body.hard_skill_score_weight,
                    accordance_xp_vacancy_score_weight=body.accordance_xp_vacancy_score_weight,
                    accordance_skill_vacancy_score_weight=body.accordance_skill_vacancy_score_weight,
                    accordance_xp_resume_score_weight=body.accordance_xp_resume_score_weight,
                    accordance_skill_resume_score_weight=body.accordance_skill_resume_score_weight,
                    red_flag_score_weight=body.red_flag_score_weight
                )

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={"message": "Веса критериев успешно обновлены"}
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))

                raise err

    async def get_all_vacancy(self) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "VacancyController.get_all_vacancy",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                vacancies = await self.vacancy_service.get_all_vacancy()

                span.set_attributes({
                    "vacancies_count": len(vacancies)
                })
                span.set_status(Status(StatusCode.OK))

                return JSONResponse(
                    status_code=200,
                    content=[vacancy.to_dict() for vacancy in vacancies]
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err