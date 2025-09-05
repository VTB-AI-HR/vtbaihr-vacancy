import json
from datetime import datetime

from opentelemetry.trace import SpanKind, Status, StatusCode

from internal import interface, model


class VacancyService(interface.IVacancyService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            vacancy_repo: interface.IVacancyRepo,
            interview_prompt_generator: interface.IInterviewPromptGenerator,
            llm_client: interface.ILLMClient,
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.vacancy_repo = vacancy_repo
        self.interview_prompt_generator = interview_prompt_generator
        self.llm_client = llm_client

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
                "VacancyService.create_vacancy",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_name": name,
                    "skill_level": skill_lvl.value,
                    "questions_type": questions_type.value,
                }
        ) as span:
            try:
                vacancy_id = await self.vacancy_repo.create_vacancy(
                    name=name,
                    tags=tags,
                    description=description,
                    red_flags=red_flags,
                    skill_lvl=skill_lvl,
                    question_response_time=question_response_time,
                    questions_type=questions_type
                )

                span.set_attributes({"vacancy_id": vacancy_id})
                span.set_status(Status(StatusCode.OK))
                return vacancy_id

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def generate_questions(
            self,
            vacancy_id: int,
            questions_type: model.QuestionsType,
            count_questions: int
    ) -> list[dict]:
        with self.tracer.start_as_current_span(
                "VacancyService.generate_questions",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": vacancy_id,
                    "questions_type": questions_type.value,
                    "count_questions": count_questions,
                }
        ) as span:
            try:
                vacancy = await self.vacancy_repo.get_vacancy_by_id(vacancy_id)
                if not vacancy:
                    raise Exception(f"Вакансия с ID {vacancy_id} не найдена")
                vacancy = vacancy[0]

                question_generation_prompt = self.interview_prompt_generator.get_question_generation_prompt(
                    vacancy,
                    count_questions,
                    questions_type,
                )

                history = [
                    model.InterviewMessage(
                        id=0,
                        interview_id=0,
                        question_id=0,
                        audio_fid="",
                        role="user",
                        text=question_generation_prompt,
                        created_at=datetime.now(),
                    )
                ]

                questions_str = await self.llm_client.generate(
                    history=history,
                    temperature=0.7,
                )

                # Парсим ответ LLM
                questions_data = json.loads(questions_str)
                questions_list = questions_data["questions"]

                # Валидируем сгенерированные вопросы
                for question in questions_list:
                    if not all(
                            key in question for key in
                            ["question", "question_type", "hint_for_evaluation", "weight"]):
                        raise Exception("LLM сгенерировал вопрос с неполными данными")

                    if question["weight"] < 1 or question["weight"] > 10:
                        question["weight"] = 5

                span.set_attributes({
                    "generated_count": len(questions_list),
                    "success": True
                })
                span.set_status(Status(StatusCode.OK))
                return questions_list

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def delete_vacancy(self, vacancy_id: int) -> None:
        with self.tracer.start_as_current_span(
                "VacancyService.delete_vacancy",
                kind=SpanKind.INTERNAL,
                attributes={"vacancy_id": vacancy_id}
        ) as span:
            try:
                # Проверяем, существует ли вакансия
                vacancy = await self.vacancy_repo.get_vacancy_by_id(vacancy_id)
                if not vacancy:
                    raise Exception(f"Вакансия с ID {vacancy_id} не найдена")

                await self.vacancy_repo.delete_vacancy(vacancy_id)

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
            question_type: model.QuestionsType
    ) -> int:
        with self.tracer.start_as_current_span(
                "VacancyService.add_question",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": vacancy_id,
                    "question_type": question_type.value,
                    "weight": weight,
                }
        ) as span:
            try:
                question_id = await self.vacancy_repo.add_question(
                    vacancy_id=vacancy_id,
                    question=question,
                    hint_for_evaluation=hint_for_evaluation,
                    weight=weight,
                    question_type=question_type
                )

                span.set_attributes({
                    "question_id": question_id,
                })
                span.set_status(Status(StatusCode.OK))

                return question_id

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
                "VacancyService.edit_question",
                kind=SpanKind.INTERNAL,
                attributes={
                    "question_id": question_id,
                    "vacancy_id": vacancy_id,
                }
        ) as span:
            try:
                # Валидация веса, если предоставлен
                if weight is not None and (weight < 0 or weight > 10):
                    raise ValueError("Вес вопроса должен быть от 0 до 10")

                # Проверяем, существует ли вакансия
                vacancy = await self.vacancy_repo.get_vacancy_by_id(vacancy_id)
                if not vacancy:
                    raise Exception(f"Вакансия с ID {vacancy_id} не найдена")

                await self.vacancy_repo.edit_question(
                    question_id=question_id,
                    vacancy_id=vacancy_id,
                    question=question,
                    hint_for_evaluation=hint_for_evaluation,
                    weight=weight,
                    question_type=question_type
                )

                span.set_status(Status(StatusCode.OK))

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def delete_question(self, question_id: int) -> None:
        with self.tracer.start_as_current_span(
                "VacancyService.delete_question",
                kind=SpanKind.INTERNAL,
                attributes={"question_id": question_id}
        ) as span:
            try:
                await self.vacancy_repo.delete_question(question_id)

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
                "VacancyService.edit_vacancy_criterion_weights",
                kind=SpanKind.INTERNAL,
                attributes={"vacancy_id": vacancy_id}
        ) as span:
            try:
                # Валидация весов (должны быть от 0 до 10)
                weights_to_validate = [
                    ("logic_structure_score_weight", logic_structure_score_weight),
                    ("soft_skill_score_weight", soft_skill_score_weight),
                    ("hard_skill_score_weight", hard_skill_score_weight),
                    ("accordance_xp_vacancy_score_weight", accordance_xp_vacancy_score_weight),
                    ("accordance_skill_vacancy_score_weight", accordance_skill_vacancy_score_weight),
                    ("accordance_xp_resume_score_weight", accordance_xp_resume_score_weight),
                    ("accordance_skill_resume_score_weight", accordance_skill_resume_score_weight),
                    ("red_flag_score_weight", red_flag_score_weight),
                ]

                for weight_name, weight_value in weights_to_validate:
                    if weight_value is not None and (weight_value < 0 or weight_value > 10):
                        raise ValueError(f"{weight_name} должен быть от 0 до 10")

                # Проверяем, существует ли вакансия
                vacancy = await self.vacancy_repo.get_vacancy_by_id(vacancy_id)
                if not vacancy:
                    raise Exception(f"Вакансия с ID {vacancy_id} не найдена")

                await self.vacancy_repo.edit_vacancy_criterion_weights(
                    vacancy_id=vacancy_id,
                    logic_structure_score_weight=logic_structure_score_weight,
                    pause_detection_score_weight=pause_detection_score_weight,
                    soft_skill_score_weight=soft_skill_score_weight,
                    hard_skill_score_weight=hard_skill_score_weight,
                    accordance_xp_vacancy_score_weight=accordance_xp_vacancy_score_weight,
                    accordance_skill_vacancy_score_weight=accordance_skill_vacancy_score_weight,
                    accordance_xp_resume_score_weight=accordance_xp_resume_score_weight,
                    accordance_skill_resume_score_weight=accordance_skill_resume_score_weight,
                    red_flag_score_weight=red_flag_score_weight
                )

                span.set_status(Status(StatusCode.OK))

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_all_vacancy(self) -> list[model.Vacancy]:
        with self.tracer.start_as_current_span(
                "VacancyService.get_all_vacancy",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                vacancies = await self.vacancy_repo.get_all_vacancy()

                span.set_attributes({"vacancies_count": len(vacancies)})
                span.set_status(Status(StatusCode.OK))
                return vacancies

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err
