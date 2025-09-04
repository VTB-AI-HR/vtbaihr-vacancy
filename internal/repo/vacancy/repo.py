from opentelemetry.trace import SpanKind, Status, StatusCode

from .sql_query import *
from internal import interface, model


class VacancyRepo(interface.IVacancyRepo):
    def __init__(self, tel: interface.ITelemetry, db: interface.IDB):
        self.db = db
        self.tracer = tel.tracer()

    async def create_vacancy(
            self,
            name: str,
            tags: list[str],
            description: str,
            red_flags: str,
            skill_lvl: model.SkillLevel,
            question_response_time: int,
            questions_type: model.QuestionsType
    ) -> int:
        with self.tracer.start_as_current_span(
                "VacancyRepo.create_vacancy",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_name": name,
                    "skill_level": skill_lvl.value,
                    "questions_type": questions_type.value,
                    "question_response_time": question_response_time,
                }
        ) as span:
            try:
                # Создаем вакансию
                vacancy_args = {
                    'name': name,
                    'tags': tags,
                    'description': description,
                    'red_flags': red_flags,
                    'skill_lvl': skill_lvl.value,
                    'question_response_time': question_response_time,
                    'questions_type': questions_type.value
                }
                vacancy_id = await self.db.insert(create_vacancy, vacancy_args)

                # Создаем веса критериев по умолчанию
                weights_args = {
                    'vacancy_id': vacancy_id,
                    'logic_structure_score_weight': 5,
                    'soft_skill_score_weight': 5,
                    'hard_skill_score_weight': 7,
                    'accordance_xp_vacancy_score_weight': 8,
                    'accordance_skill_vacancy_score_weight': 8,
                    'accordance_xp_resume_score_weight': 6,
                    'accordance_skill_resume_score_weight': 7,
                    'red_flag_score_weight': 10
                }
                await self.db.insert(create_vacancy_criterion_weights, weights_args)

                span.set_attributes({"vacancy_id": vacancy_id})
                span.set_status(Status(StatusCode.OK))
                return vacancy_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def delete_vacancy(self, vacancy_id: int) -> None:
        with self.tracer.start_as_current_span(
                "VacancyRepo.delete_vacancy",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": vacancy_id,
                }
        ) as span:
            try:
                args = {'vacancy_id': vacancy_id}
                await self.db.delete(delete_vacancy, args)

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def add_question(
            self,
            vacancy_id: int,
            question: str,
            hint_for_evaluation: str,
            weight: int,  # [0;10]
            question_type: model.QuestionsType
    ) -> tuple[int, int]:
        with self.tracer.start_as_current_span(
                "VacancyRepo.add_question",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": vacancy_id,
                    "question_type": question_type.value,
                    "weight": weight,
                }
        ) as span:
            try:
                args = {
                    'vacancy_id': vacancy_id,
                    'question': question,
                    'hint_for_evaluation': hint_for_evaluation,
                    'weight': weight,
                    'question_type': question_type.value
                }
                result = await self.db.select(add_question, args)
                question_id = result[0].id
                order_number = result[0].order_number

                span.set_attributes({
                    "question_id": question_id,
                    "order_number": order_number
                })
                span.set_status(Status(StatusCode.OK))
                return question_id, order_number
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def edit_question(
            self,
            question_id: int,
            vacancy_id: int,
            question: str | None,
            hint_for_evaluation: str | None,
            weight: int | None,  # [0;10]
            question_type: model.QuestionsType | None
    ) -> None:
        with self.tracer.start_as_current_span(
                "VacancyRepo.edit_question",
                kind=SpanKind.INTERNAL,
                attributes={
                    "question_id": question_id,
                    "vacancy_id": vacancy_id,
                }
        ) as span:
            try:
                args = {
                    'question_id': question_id,
                    'vacancy_id': vacancy_id,
                    'question': question,
                    'hint_for_evaluation': hint_for_evaluation,
                    'weight': weight,
                    'question_type': question_type.value if question_type else None
                }
                await self.db.update(edit_question, args)

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def delete_question(self, question_id: int) -> None:
        with self.tracer.start_as_current_span(
                "VacancyRepo.delete_question",
                kind=SpanKind.INTERNAL,
                attributes={
                    "question_id": question_id,
                }
        ) as span:
            try:
                args = {'question_id': question_id}
                await self.db.delete(delete_question, args)

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def edit_vacancy_criterion_weights(
            self,
            vacancy_id: int,
            logic_structure_score_weight: int | None,
            pause_detection_score_weight: int | None,
            soft_skill_score_weight: int | None,
            hard_skill_score_weight: int | None,
            accordance_xp_vacancy_score_weight: int | None,
            accordance_skill_vacancy_score_weight: int | None,
            accordance_xp_resume_score_weight: int | None,
            accordance_skill_resume_score_weight: int | None,
            red_flag_score_weight: int | None
    ) -> None:
        with self.tracer.start_as_current_span(
                "VacancyRepo.edit_vacancy_criterion_weights",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": vacancy_id,
                }
        ) as span:
            try:
                args = {
                    'vacancy_id': vacancy_id,
                    'logic_structure_score_weight': logic_structure_score_weight,
                    # pause_detection_score_weight не используется в текущей схеме БД
                    'soft_skill_score_weight': soft_skill_score_weight,
                    'hard_skill_score_weight': hard_skill_score_weight,
                    'accordance_xp_vacancy_score_weight': accordance_xp_vacancy_score_weight,
                    'accordance_skill_vacancy_score_weight': accordance_skill_vacancy_score_weight,
                    'accordance_xp_resume_score_weight': accordance_xp_resume_score_weight,
                    'accordance_skill_resume_score_weight': accordance_skill_resume_score_weight,
                    'red_flag_score_weight': red_flag_score_weight
                }
                await self.db.update(edit_vacancy_criterion_weights, args)

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_all_vacancy(self) -> list[model.Vacancy]:
        with self.tracer.start_as_current_span(
                "VacancyRepo.get_all_vacancy",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                rows = await self.db.select(get_all_vacancy, {})
                vacancies = model.Vacancy.serialize(rows) if rows else []

                span.set_attributes({"vacancies_count": len(vacancies)})
                span.set_status(Status(StatusCode.OK))
                return vacancies
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_all_question(self, vacancy_id: int) -> list[model.VacancyQuestion]:
        with self.tracer.start_as_current_span(
                "VacancyRepo.get_all_question",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": vacancy_id,
                }
        ) as span:
            try:
                args = {'vacancy_id': vacancy_id}
                rows = await self.db.select(get_all_question, args)
                questions = model.VacancyQuestion.serialize(rows) if rows else []

                span.set_attributes({"questions_count": len(questions)})
                span.set_status(Status(StatusCode.OK))
                return questions
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_vacancy_by_id(self, vacancy_id: int) -> list[model.Vacancy]:
        with self.tracer.start_as_current_span(
                "VacancyRepo.get_vacancy_by_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": vacancy_id,
                }
        ) as span:
            try:
                args = {'vacancy_id': vacancy_id}
                rows = await self.db.select(get_vacancy_by_id, args)
                vacancies = model.Vacancy.serialize(rows) if rows else []

                span.set_attributes({"found": len(vacancies) > 0})
                span.set_status(Status(StatusCode.OK))
                return vacancies
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err