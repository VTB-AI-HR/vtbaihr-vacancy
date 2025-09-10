from opentelemetry.trace import Status, StatusCode, SpanKind
from fastapi import UploadFile, Form
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
        self.logger = tel.logger()
        self.vacancy_service = vacancy_service

    async def create_vacancy(self, body: CreateVacancyBody) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "VacancyController.create_vacancy",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                self.logger.info("Начали создание вакансии", {
                    "vacancy_name": body.name,
                    "skill_level": body.skill_lvl.value,
                    "tags_count": len(body.tags),
                    "has_description": bool(body.description),
                    "has_red_flags": bool(body.red_flags),
                    "tags": body.tags
                })

                vacancy_id = await self.vacancy_service.create_vacancy(
                    name=body.name,
                    tags=body.tags,
                    description=body.description,
                    red_flags=body.red_flags,
                    skill_lvl=body.skill_lvl
                )

                self.logger.info("Создали вакансию", {
                    "vacancy_id": vacancy_id,
                    "vacancy_name": body.name,
                    "skill_level": body.skill_lvl.value
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=201,
                    content={
                        "message": "Vacancy created successfully",
                        "vacancy_id": vacancy_id
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
                attributes={"vacancy_id": vacancy_id}
        ) as span:
            try:
                self.logger.info("Начали удаление вакансии", {"vacancy_id": vacancy_id})

                await self.vacancy_service.delete_vacancy(vacancy_id)

                self.logger.info("Удалили вакансию", {"vacancy_id": vacancy_id})

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={"message": "Vacancy deleted successfully"}
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def edit_vacancy(self, body: EditVacancyBody) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "VacancyController.edit_vacancy",
                kind=SpanKind.INTERNAL,
                attributes={"vacancy_id": body.vacancy_id}
        ) as span:
            try:
                self.logger.info("Начали редактирование вакансии", {
                    "vacancy_id": body.vacancy_id,
                    "has_name": body.name is not None,
                    "has_tags": body.tags is not None,
                    "has_description": body.description is not None,
                    "has_red_flags": body.red_flags is not None,
                    "has_skill_lvl": body.skill_lvl is not None,
                    "new_name": body.name,
                    "new_tags_count": len(body.tags) if body.tags else None,
                    "new_skill_level": body.skill_lvl.value if body.skill_lvl else None
                })

                await self.vacancy_service.edit_vacancy(
                    vacancy_id=body.vacancy_id,
                    name=body.name,
                    tags=body.tags,
                    description=body.description,
                    red_flags=body.red_flags,
                    skill_lvl=body.skill_lvl
                )

                self.logger.info("Отредактировали вакансию", {
                    "vacancy_id": body.vacancy_id,
                    "updated_fields": [
                        field for field in ["name", "tags", "description", "red_flags", "skill_lvl"]
                        if getattr(body, field) is not None
                    ]
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={"message": "Vacancy updated successfully"}
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
                    "weight": body.weight
                }
        ) as span:
            try:
                self.logger.info("Начали добавление вопроса", {
                    "vacancy_id": body.vacancy_id,
                    "question_type": body.question_type.value,
                    "weight": body.weight,
                    "response_time": body.response_time,
                    "has_hint": bool(body.hint_for_evaluation),
                    "question_text": body.question[:100] + "..." if len(body.question) > 100 else body.question
                })

                question_id = await self.vacancy_service.add_question(
                    vacancy_id=body.vacancy_id,
                    question=body.question,
                    hint_for_evaluation=body.hint_for_evaluation,
                    weight=body.weight,
                    question_type=body.question_type,
                    response_time=body.response_time
                )

                self.logger.info("Добавили вопрос", {
                    "question_id": question_id,
                    "vacancy_id": body.vacancy_id,
                    "question_type": body.question_type.value,
                    "weight": body.weight
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=201,
                    content={
                        "message": "Question added successfully",
                        "question_id": question_id
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
                attributes={"question_id": body.question_id}
        ) as span:
            try:
                self.logger.info("Начали редактирование вопроса", {
                    "question_id": body.question_id,
                    "vacancy_id": body.vacancy_id,
                    "has_question": body.question is not None,
                    "has_hint": body.hint_for_evaluation is not None,
                    "has_weight": body.weight is not None,
                    "has_type": body.question_type is not None,
                    "has_response_time": body.response_time is not None,
                    "new_weight": body.weight,
                    "new_type": body.question_type.value if body.question_type else None,
                    "new_response_time": body.response_time
                })

                await self.vacancy_service.edit_question(
                    question_id=body.question_id,
                    question=body.question,
                    hint_for_evaluation=body.hint_for_evaluation,
                    weight=body.weight,
                    question_type=body.question_type,
                    response_time=body.response_time
                )

                self.logger.info("Отредактировали вопрос", {
                    "question_id": body.question_id,
                    "updated_fields": [
                        field for field in ["question", "hint_for_evaluation", "weight", "question_type", "response_time"]
                        if getattr(body, field) is not None
                    ]
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={"message": "Question updated successfully"}
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def delete_question(self, question_id: int) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "VacancyController.delete_question",
                kind=SpanKind.INTERNAL,
                attributes={"question_id": question_id}
        ) as span:
            try:
                self.logger.info("Начали удаление вопроса", {"question_id": question_id})

                await self.vacancy_service.delete_question(question_id)

                self.logger.info("Удалили вопрос", {"question_id": question_id})

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={"message": "Question deleted successfully"}
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def create_interview_weights(self, body: CreateInterviewWeightsBody) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "VacancyController.create_interview_criterion_weight",
                kind=SpanKind.INTERNAL,
                attributes={"vacancy_id": body.vacancy_id}
        ) as span:
            try:
                self.logger.info("Начали создание весов критериев интервью", {
                    "vacancy_id": body.vacancy_id,
                    "logic_structure_score_weight": body.logic_structure_score_weight,
                    "soft_skill_score_weight": body.soft_skill_score_weight,
                    "hard_skill_score_weight": body.hard_skill_score_weight,
                    "accordance_xp_resume_score_weight": body.accordance_xp_resume_score_weight,
                    "accordance_skill_resume_score_weight": body.accordance_skill_resume_score_weight,
                    "red_flag_score_weight": body.red_flag_score_weight
                })

                await self.vacancy_service.create_interview_weights(
                    vacancy_id=body.vacancy_id,
                    logic_structure_score_weight=body.logic_structure_score_weight,
                    soft_skill_score_weight=body.soft_skill_score_weight,
                    hard_skill_score_weight=body.hard_skill_score_weight,
                    accordance_xp_resume_score_weight=body.accordance_xp_resume_score_weight,
                    accordance_skill_resume_score_weight=body.accordance_skill_resume_score_weight,
                    red_flag_score_weight=body.red_flag_score_weight
                )

                self.logger.info("Создали веса критериев интервью", {"vacancy_id": body.vacancy_id})

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=201,
                    content={"message": "Vacancy criterion weights created successfully"}
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def edit_interview_weights(self, body: EditInterviewWeightsBody) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "VacancyController.edit_interview_criterion_weight",
                kind=SpanKind.INTERNAL,
                attributes={"vacancy_id": body.vacancy_id}
        ) as span:
            try:
                self.logger.info("Начали редактирование весов критериев интервью", {
                    "vacancy_id": body.vacancy_id,
                    "logic_structure_score_weight": body.logic_structure_score_weight,
                    "soft_skill_score_weight": body.soft_skill_score_weight,
                    "hard_skill_score_weight": body.hard_skill_score_weight,
                    "accordance_xp_resume_score_weight": body.accordance_xp_resume_score_weight,
                    "accordance_skill_resume_score_weight": body.accordance_skill_resume_score_weight,
                    "red_flag_score_weight": body.red_flag_score_weight
                })

                await self.vacancy_service.edit_interview_weights(
                    vacancy_id=body.vacancy_id,
                    logic_structure_score_weight=body.logic_structure_score_weight,
                    soft_skill_score_weight=body.soft_skill_score_weight,
                    hard_skill_score_weight=body.hard_skill_score_weight,
                    accordance_xp_resume_score_weight=body.accordance_xp_resume_score_weight,
                    accordance_skill_resume_score_weight=body.accordance_skill_resume_score_weight,
                    red_flag_score_weight=body.red_flag_score_weight
                )

                self.logger.info("Отредактировали веса критериев интервью", {"vacancy_id": body.vacancy_id})

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={"message": "Vacancy criterion weights updated successfully"}
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def create_resume_weights(self, body: CreateResumeWeightsBody) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "VacancyController.create_resume_weight",
                kind=SpanKind.INTERNAL,
                attributes={"vacancy_id": body.vacancy_id}
        ) as span:
            try:
                self.logger.info("Начали создание весов резюме", {
                    "vacancy_id": body.vacancy_id,
                    "accordance_xp_vacancy_score_threshold": body.accordance_xp_vacancy_score_threshold,
                    "accordance_skill_vacancy_score_threshold": body.accordance_skill_vacancy_score_threshold,
                    "recommendation_weight": body.recommendation_weight,
                    "portfolio_weight": body.portfolio_weight
                })

                await self.vacancy_service.create_resume_weights(
                    vacancy_id=body.vacancy_id,
                    accordance_xp_vacancy_score_threshold=body.accordance_xp_vacancy_score_threshold,
                    accordance_skill_vacancy_score_threshold=body.accordance_skill_vacancy_score_threshold,
                    recommendation_weight=body.recommendation_weight,
                    portfolio_weight=body.portfolio_weight
                )

                self.logger.info("Создали веса резюме", {"vacancy_id": body.vacancy_id})

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=201,
                    content={"message": "Resume weights created successfully"}
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def edit_resume_weights(self, body: EditResumeWeightsBody) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "VacancyController.edit_resume_weight",
                kind=SpanKind.INTERNAL,
                attributes={"vacancy_id": body.vacancy_id}
        ) as span:
            try:
                self.logger.info("Начали редактирование весов резюме", {
                    "vacancy_id": body.vacancy_id,
                    "accordance_xp_vacancy_score_threshold": body.accordance_xp_vacancy_score_threshold,
                    "accordance_skill_vacancy_score_threshold": body.accordance_skill_vacancy_score_threshold,
                    "recommendation_weight": body.recommendation_weight,
                    "portfolio_weight": body.portfolio_weight
                })

                await self.vacancy_service.edit_resume_weights(
                    vacancy_id=body.vacancy_id,
                    accordance_xp_vacancy_score_threshold=body.accordance_xp_vacancy_score_threshold,
                    accordance_skill_vacancy_score_threshold=body.accordance_skill_vacancy_score_threshold,
                    recommendation_weight=body.recommendation_weight,
                    portfolio_weight=body.portfolio_weight
                )

                self.logger.info("Отредактировали веса резюме", {"vacancy_id": body.vacancy_id})

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={"message": "Resume weights updated successfully"}
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def generate_tags(self, body: GenerateTagsBody) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "VacancyController.generate_tags",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                self.logger.info("Начали генерацию тегов", {
                    "description_length": len(body.vacancy_description),
                    "description_preview": body.vacancy_description[:100] + "..." if len(body.vacancy_description) > 100 else body.vacancy_description
                })

                tags = await self.vacancy_service.generate_tags(body.vacancy_description)

                self.logger.info("Сгенерировали теги", {
                    "tags_count": len(tags),
                    "tags": tags
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={"tags": tags}
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
                    "count_questions": body.count_questions
                }
        ) as span:
            try:
                if body.count_questions > 30:
                    raise Exception("Too many questions")

                self.logger.info("Начали генерацию вопросов", {
                    "vacancy_id": body.vacancy_id,
                    "questions_type": body.questions_type.value,
                    "count_questions": body.count_questions
                })

                questions = await self.vacancy_service.generate_question(
                    vacancy_id=body.vacancy_id,
                    questions_type=body.questions_type,
                    count_questions=body.count_questions
                )

                # Конвертируем в словари для JSON ответа
                questions_dict = [question.to_dict() for question in questions]

                self.logger.info("Сгенерировали вопросы", {
                    "vacancy_id": body.vacancy_id,
                    "generated_count": len(questions),
                    "questions_type": body.questions_type.value,
                    "requested_count": body.count_questions
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={"questions": questions_dict}
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def evaluate_resume(
            self,
            vacancy_id: int = Form(...),
            candidate_resume_files: list[UploadFile] = Form(...)
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "VacancyController.evaluate_resume",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": vacancy_id,
                    "resumes_count": len(candidate_resume_files)
                }
        ) as span:
            try:
                if len(candidate_resume_files) > 10:
                    raise Exception("Too many files")

                file_info = [
                    {
                        "filename": file.filename,
                        "content_type": file.content_type,
                        "size": file.size if hasattr(file, 'size') else None
                    }
                    for file in candidate_resume_files
                ]

                self.logger.info("Начали оценку резюме", {
                    "vacancy_id": vacancy_id,
                    "resumes_count": len(candidate_resume_files),
                    "files_info": file_info
                })

                created_interviews = await self.vacancy_service.evaluate_resume(
                    vacancy_id=vacancy_id,
                    candidate_resume_files=candidate_resume_files
                )

                # Формируем ответ согласно EvaluateResumeResponse
                evaluation_resumes = []
                for interview in created_interviews:
                    evaluation_resumes.append({
                        "candidate_email": interview.candidate_email,
                        "candidate_name": interview.candidate_name,
                        "candidate_phone": interview.candidate_phone,
                        "accordance_xp_vacancy_score": interview.accordance_xp_vacancy_score,
                        "accordance_skill_vacancy_score": interview.accordance_skill_vacancy_score
                    })

                self.logger.info("Оценили резюме", {
                    "vacancy_id": vacancy_id,
                    "total_resumes": len(candidate_resume_files),
                    "approved_resumes": len(evaluation_resumes),
                    "approval_rate": len(evaluation_resumes) / len(candidate_resume_files) if candidate_resume_files else 0
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={"evaluation_resumes": evaluation_resumes}
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def respond(
            self,
            vacancy_id: int = Form(...),
            candidate_email: str = Form(...),
            candidate_resume_file: UploadFile = Form(...)
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "VacancyController.respond",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": vacancy_id,
                    "candidate_email": candidate_email
                }
        ) as span:
            try:
                self.logger.info("Начали обработку отклика кандидата", {
                    "vacancy_id": vacancy_id,
                    "candidate_email": candidate_email,
                    "resume_filename": candidate_resume_file.filename,
                    "resume_content_type": candidate_resume_file.content_type,
                    "resume_size": candidate_resume_file.size if hasattr(candidate_resume_file, 'size') else None
                })

                interview_link, accordance_xp_score, accordance_skill_score, message_to_candidate = await self.vacancy_service.respond(
                    vacancy_id=vacancy_id,
                    candidate_email=candidate_email,
                    candidate_resume_file=candidate_resume_file
                )

                response_data = {
                    "interview_link": interview_link,
                    "accordance_xp_vacancy_score": accordance_xp_score,
                    "accordance_skill_vacancy_score": accordance_skill_score,
                    "message_to_candidate": message_to_candidate
                }

                if interview_link:
                    self.logger.info("Кандидат одобрен для интервью", {
                        "vacancy_id": vacancy_id,
                        "candidate_email": candidate_email,
                        "interview_link": interview_link,
                        "accordance_xp_score": accordance_xp_score,
                        "accordance_skill_score": accordance_skill_score
                    })
                    status_code = 200
                else:
                    self.logger.info("Кандидат отклонен", {
                        "vacancy_id": vacancy_id,
                        "candidate_email": candidate_email,
                        "accordance_xp_score": accordance_xp_score,
                        "accordance_skill_score": accordance_skill_score,
                        "rejection_reason": "Scores below threshold"
                    })
                    status_code = 200

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=status_code,
                    content=response_data
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
                self.logger.info("Начали получение всех вакансий")

                vacancies = await self.vacancy_service.get_all_vacancy()
                vacancies_dict = [vacancy.to_dict() for vacancy in vacancies]

                self.logger.info("Получили все вакансии", {
                    "vacancies_count": len(vacancies)
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content=vacancies_dict
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_all_question(self, vacancy_id: int) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "VacancyController.get_all_question",
                kind=SpanKind.INTERNAL,
                attributes={"vacancy_id": vacancy_id}
        ) as span:
            try:
                self.logger.info("Начали получение всех вопросов", {"vacancy_id": vacancy_id})

                questions = await self.vacancy_service.get_all_question(vacancy_id)
                questions_dict = [question.to_dict() for question in questions]

                self.logger.info("Получили все вопросы", {
                    "vacancy_id": vacancy_id,
                    "questions_count": len(questions)
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content=questions_dict
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_question_by_id(self, question_id: int) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "VacancyController.get_question_by_id",
                kind=SpanKind.INTERNAL,
                attributes={"question_id": question_id}
        ) as span:
            try:
                self.logger.info("Начали получение вопроса по ID", {"question_id": question_id})

                question = await self.vacancy_service.get_question_by_id(question_id)
                question_dict = question.to_dict()

                self.logger.info("Получили вопрос по ID", {
                    "question_id": question_id,
                    "vacancy_id": question.vacancy_id,
                    "question_type": question.question_type.value if hasattr(question, 'question_type') else None,
                    "weight": question.weight if hasattr(question, 'weight') else None
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content=question_dict
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_interview_weights(self, vacancy_id: int) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "VacancyController.get_interview_criterion_weights",
                kind=SpanKind.INTERNAL,
                attributes={"vacancy_id": vacancy_id}
        ) as span:
            try:
                self.logger.info("Начали получение весов критериев интервью", {"vacancy_id": vacancy_id})

                weights = await self.vacancy_service.get_interview_weights(vacancy_id)
                weights_dict = [weight.to_dict() for weight in weights]

                self.logger.info("Получили веса критериев интервью", {
                    "vacancy_id": vacancy_id,
                    "weights_found": len(weights) > 0,
                    "weights_count": len(weights)
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content=weights_dict
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_resume_weights(self, vacancy_id: int) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "VacancyController.get_resume_criterion_weights",
                kind=SpanKind.INTERNAL,
                attributes={"vacancy_id": vacancy_id}
        ) as span:
            try:
                self.logger.info("Начали получениие весов резюме", {"vacancy_id": vacancy_id})

                weights = await self.vacancy_service.get_resume_weights(vacancy_id)
                weights_dict = [weight.to_dict() for weight in weights]

                self.logger.info("Получили веса резюме", {
                    "vacancy_id": vacancy_id,
                    "weights_found": len(weights) > 0
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content=weights_dict
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err