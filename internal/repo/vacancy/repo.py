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
    ) -> int:
        with self.tracer.start_as_current_span(
                "VacancyRepo.create_vacancy",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_name": name,
                    "skill_level": skill_lvl.value,
                }
        ) as span:
            try:
                args = {
                    'name': name,
                    'tags': tags,
                    'description': description,
                    'red_flags': red_flags,
                    'skill_lvl': skill_lvl.value,
                }
                vacancy_id = await self.db.insert(create_vacancy_query, args)

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
                await self.db.delete(delete_vacancy_query, args)

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def edit_vacancy(
            self,
            vacancy_id: int,
            name: str | None,
            tags: list[str] | None,
            description: str | None,
            red_flags: str | None,
            skill_lvl: model.SkillLevel | None,
    ) -> None:
        with self.tracer.start_as_current_span(
                "VacancyRepo.edit_vacancy",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": vacancy_id,
                }
        ) as span:
            try:
                # Строим динамический запрос на основе переданных параметров
                update_fields = []
                args: dict = {'vacancy_id': vacancy_id}

                if name is not None:
                    update_fields.append("name = :name")
                    args['name'] = name

                if tags is not None:
                    update_fields.append("tags = :tags")
                    args['tags'] = tags

                if description is not None:
                    update_fields.append("description = :description")
                    args['description'] = description

                if red_flags is not None:
                    update_fields.append("red_flags = :red_flags")
                    args['red_flags'] = red_flags

                if skill_lvl is not None:
                    update_fields.append("skill_lvl = :skill_lvl")
                    args['skill_lvl'] = skill_lvl.value

                if not update_fields:
                    span.set_status(Status(StatusCode.OK))
                    return

                query = f"""
                UPDATE vacancies
                SET {', '.join(update_fields)}
                WHERE id = :vacancy_id;
                """

                await self.db.update(query, args)

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
            weight: int,
            question_type: model.QuestionsType,
            response_time: int,
    ) -> int:
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
                    'question_type': question_type.value,
                    'response_time': response_time,
                }
                question_id = await self.db.insert(add_question_query, args)

                span.set_status(Status(StatusCode.OK))
                return question_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def edit_question(
            self,
            question_id: int,
            question: str | None,
            hint_for_evaluation: str | None,
            weight: int | None,
            question_type: model.QuestionsType | None,
            response_time: int | None,
    ) -> None:
        with self.tracer.start_as_current_span(
                "VacancyRepo.edit_question",
                kind=SpanKind.INTERNAL,
                attributes={
                    "question_id": question_id,
                }
        ) as span:
            try:
                update_fields = []
                args: dict = {'question_id': question_id}

                if question is not None:
                    update_fields.append("question = :question")
                    args['question'] = question

                if hint_for_evaluation is not None:
                    update_fields.append("hint_for_evaluation = :hint_for_evaluation")
                    args['hint_for_evaluation'] = hint_for_evaluation

                if weight is not None:
                    update_fields.append("weight = :weight")
                    args['weight'] = weight

                if question_type is not None:
                    update_fields.append("question_type = :question_type")
                    args['question_type'] = question_type.value

                if response_time is not None:
                    update_fields.append("response_time = :response_time")
                    args['response_time'] = response_time

                if not update_fields:
                    span.set_status(Status(StatusCode.OK))
                    return

                query = f"""
                UPDATE vacancy_questions
                SET {', '.join(update_fields)}
                WHERE id = :question_id;
                """

                await self.db.update(query, args)

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
                await self.db.delete(delete_question_query, args)

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def create_vacancy_criterion_weight(
            self,
            vacancy_id: int,
            logic_structure_score_weight: int,
            pause_detection_score_weight: int,
            soft_skill_score_weight: int,
            hard_skill_score_weight: int,
            accordance_xp_vacancy_score_weight: int,
            accordance_skill_vacancy_score_weight: int,
            accordance_xp_resume_score_weight: int,
            accordance_skill_resume_score_weight: int,
            red_flag_score_weight: int,
    ) -> None:
        with self.tracer.start_as_current_span(
                "VacancyRepo.create_vacancy_criterion_weight",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": vacancy_id,
                }
        ) as span:
            try:
                args = {
                    'vacancy_id': vacancy_id,
                    'logic_structure_score_weight': logic_structure_score_weight,
                    'pause_detection_score_weight': pause_detection_score_weight,
                    'soft_skill_score_weight': soft_skill_score_weight,
                    'hard_skill_score_weight': hard_skill_score_weight,
                    'accordance_xp_vacancy_score_weight': accordance_xp_vacancy_score_weight,
                    'accordance_skill_vacancy_score_weight': accordance_skill_vacancy_score_weight,
                    'accordance_xp_resume_score_weight': accordance_xp_resume_score_weight,
                    'accordance_skill_resume_score_weight': accordance_skill_resume_score_weight,
                    'red_flag_score_weight': red_flag_score_weight,
                }
                await self.db.insert(create_vacancy_criterion_weight_query, args)

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def edit_vacancy_criterion_weight(
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
            red_flag_score_weight: int | None,
    ) -> None:
        with self.tracer.start_as_current_span(
                "VacancyRepo.edit_vacancy_criterion_weight",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": vacancy_id,
                }
        ) as span:
            try:
                update_fields = []
                args = {'vacancy_id': vacancy_id}

                if logic_structure_score_weight is not None:
                    update_fields.append("logic_structure_score_weight = :logic_structure_score_weight")
                    args['logic_structure_score_weight'] = logic_structure_score_weight

                if pause_detection_score_weight is not None:
                    update_fields.append("pause_detection_score_weight = :pause_detection_score_weight")
                    args['pause_detection_score_weight'] = pause_detection_score_weight

                if soft_skill_score_weight is not None:
                    update_fields.append("soft_skill_score_weight = :soft_skill_score_weight")
                    args['soft_skill_score_weight'] = soft_skill_score_weight

                if hard_skill_score_weight is not None:
                    update_fields.append("hard_skill_score_weight = :hard_skill_score_weight")
                    args['hard_skill_score_weight'] = hard_skill_score_weight

                if accordance_xp_vacancy_score_weight is not None:
                    update_fields.append("accordance_xp_vacancy_score_weight = :accordance_xp_vacancy_score_weight")
                    args['accordance_xp_vacancy_score_weight'] = accordance_xp_vacancy_score_weight

                if accordance_skill_vacancy_score_weight is not None:
                    update_fields.append(
                        "accordance_skill_vacancy_score_weight = :accordance_skill_vacancy_score_weight")
                    args['accordance_skill_vacancy_score_weight'] = accordance_skill_vacancy_score_weight

                if accordance_xp_resume_score_weight is not None:
                    update_fields.append("accordance_xp_resume_score_weight = :accordance_xp_resume_score_weight")
                    args['accordance_xp_resume_score_weight'] = accordance_xp_resume_score_weight

                if accordance_skill_resume_score_weight is not None:
                    update_fields.append("accordance_skill_resume_score_weight = :accordance_skill_resume_score_weight")
                    args['accordance_skill_resume_score_weight'] = accordance_skill_resume_score_weight

                if red_flag_score_weight is not None:
                    update_fields.append("red_flag_score_weight = :red_flag_score_weight")
                    args['red_flag_score_weight'] = red_flag_score_weight

                if not update_fields:
                    span.set_status(Status(StatusCode.OK))
                    return

                query = f"""
                UPDATE vacancy_criterion_weights
                SET {', '.join(update_fields)}
                WHERE vacancy_id = :vacancy_id;
                """

                await self.db.update(query, args)

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def create_resume_weight(
            self,
            vacancy_id: int,
            hard_skill_weight: int,
            work_xp_weight: int,
            recommendation_weight: int,
            portfolio_weight: int,
    ) -> None:
        with self.tracer.start_as_current_span(
                "VacancyRepo.create_resume_weight",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": vacancy_id,
                }
        ) as span:
            try:
                args = {
                    'vacancy_id': vacancy_id,
                    'hard_skill_weight': hard_skill_weight,
                    'work_xp_weight': work_xp_weight,
                    'recommendation_weight': recommendation_weight,
                    'portfolio_weight': portfolio_weight,
                }
                await self.db.insert(create_resume_weight_query, args)

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def edit_resume_weight(
            self,
            vacancy_id: int,
            hard_skill_weight: int | None,
            work_xp_weight: int | None,
            recommendation_weight: int | None,
            portfolio_weight: int | None,
    ) -> None:
        with self.tracer.start_as_current_span(
                "VacancyRepo.edit_resume_weight",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": vacancy_id,
                }
        ) as span:
            try:
                update_fields = []
                args = {'vacancy_id': vacancy_id}

                if hard_skill_weight is not None:
                    update_fields.append("hard_skill_weight = :hard_skill_weight")
                    args['hard_skill_weight'] = hard_skill_weight

                if work_xp_weight is not None:
                    update_fields.append("work_xp_weight = :work_xp_weight")
                    args['work_xp_weight'] = work_xp_weight

                if recommendation_weight is not None:
                    update_fields.append("recommendation_weight = :recommendation_weight")
                    args['recommendation_weight'] = recommendation_weight

                if portfolio_weight is not None:
                    update_fields.append("portfolio_weight = :portfolio_weight")
                    args['portfolio_weight'] = portfolio_weight

                if not update_fields:
                    span.set_status(Status(StatusCode.OK))
                    return

                query = f"""
                UPDATE resume_criterion_weights
                SET {', '.join(update_fields)}
                WHERE vacancy_id = :vacancy_id;
                """

                await self.db.update(query, args)

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
                rows = await self.db.select(get_all_vacancy_query, {})
                vacancies = model.Vacancy.serialize(rows) if rows else []

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
                rows = await self.db.select(get_all_question_query, args)
                questions = model.VacancyQuestion.serialize(rows) if rows else []

                span.set_status(Status(StatusCode.OK))
                return questions
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err