from opentelemetry.trace import Status, StatusCode, SpanKind
from fastapi import UploadFile, Form, File
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
                self.logger.info("Creating vacancy request", {
                    "vacancy_name": body.name,
                    "skill_level": body.skill_lvl.value,
                    "tags_count": len(body.tags)
                })

                vacancy_id = await self.vacancy_service.create_vacancy(
                    name=body.name,
                    tags=body.tags,
                    description=body.description,
                    red_flags=body.red_flags,
                    skill_lvl=body.skill_lvl
                )

                self.logger.info("Vacancy created successfully", {
                    "vacancy_id": vacancy_id,
                    "vacancy_name": body.name
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
                self.logger.info("Deleting vacancy request", {"vacancy_id": vacancy_id})

                await self.vacancy_service.delete_vacancy(vacancy_id)

                self.logger.info("Vacancy deleted successfully", {"vacancy_id": vacancy_id})

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
                self.logger.info("Editing vacancy request", {
                    "vacancy_id": body.vacancy_id,
                    "has_name": body.name is not None,
                    "has_tags": body.tags is not None,
                    "has_description": body.description is not None,
                    "has_red_flags": body.red_flags is not None,
                    "has_skill_lvl": body.skill_lvl is not None
                })

                await self.vacancy_service.edit_vacancy(
                    vacancy_id=body.vacancy_id,
                    name=body.name,
                    tags=body.tags,
                    description=body.description,
                    red_flags=body.red_flags,
                    skill_lvl=body.skill_lvl
                )

                self.logger.info("Vacancy edited successfully", {"vacancy_id": body.vacancy_id})

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
                self.logger.info("Adding question request", {
                    "vacancy_id": body.vacancy_id,
                    "question_type": body.question_type.value,
                    "weight": body.weight,
                    "response_time": body.response_time
                })

                question_id = await self.vacancy_service.add_question(
                    vacancy_id=body.vacancy_id,
                    question=body.question,
                    hint_for_evaluation=body.hint_for_evaluation,
                    weight=body.weight,
                    question_type=body.question_type,
                    response_time=body.response_time
                )

                self.logger.info("Question added successfully", {
                    "question_id": question_id,
                    "vacancy_id": body.vacancy_id
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
                self.logger.info("Editing question request", {
                    "question_id": body.question_id,
                    "vacancy_id": body.vacancy_id,
                    "has_question": body.question is not None,
                    "has_hint": body.hint_for_evaluation is not None,
                    "has_weight": body.weight is not None,
                    "has_type": body.question_type is not None
                })

                await self.vacancy_service.edit_question(
                    question_id=body.question_id,
                    question=body.question,
                    hint_for_evaluation=body.hint_for_evaluation,
                    weight=body.weight,
                    question_type=body.question_type,
                    response_time=body.response_time
                )

                self.logger.info("Question edited successfully", {"question_id": body.question_id})

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
                self.logger.info("Deleting question request", {"question_id": question_id})

                await self.vacancy_service.delete_question(question_id)

                self.logger.info("Question deleted successfully", {"question_id": question_id})

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={"message": "Question deleted successfully"}
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def create_vacancy_criterion_weight(self, body: CreateVacancyCriterionWeightBody) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "VacancyController.create_vacancy_criterion_weight",
                kind=SpanKind.INTERNAL,
                attributes={"vacancy_id": body.vacancy_id}
        ) as span:
            try:
                self.logger.info("Creating vacancy criterion weights", {"vacancy_id": body.vacancy_id})

                await self.vacancy_service.create_vacancy_criterion_weight(
                    vacancy_id=body.vacancy_id,
                    logic_structure_score_weight=body.logic_structure_score_weight,
                    soft_skill_score_weight=body.soft_skill_score_weight,
                    hard_skill_score_weight=body.hard_skill_score_weight,
                    accordance_xp_vacancy_score_weight=body.accordance_xp_vacancy_score_weight,
                    accordance_skill_vacancy_score_weight=body.accordance_skill_vacancy_score_weight,
                    accordance_xp_resume_score_weight=body.accordance_xp_resume_score_weight,
                    accordance_skill_resume_score_weight=body.accordance_skill_resume_score_weight,
                    red_flag_score_weight=body.red_flag_score_weight
                )

                self.logger.info("Vacancy criterion weights created successfully", {"vacancy_id": body.vacancy_id})

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=201,
                    content={"message": "Vacancy criterion weights created successfully"}
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def edit_vacancy_criterion_weight(self, body: EditVacancyCriterionWeightBody) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "VacancyController.edit_vacancy_criterion_weight",
                kind=SpanKind.INTERNAL,
                attributes={"vacancy_id": body.vacancy_id}
        ) as span:
            try:
                self.logger.info("Editing vacancy criterion weights", {"vacancy_id": body.vacancy_id})

                await self.vacancy_service.edit_vacancy_criterion_weight(
                    vacancy_id=body.vacancy_id,
                    logic_structure_score_weight=body.logic_structure_score_weight,
                    soft_skill_score_weight=body.soft_skill_score_weight,
                    hard_skill_score_weight=body.hard_skill_score_weight,
                    accordance_xp_vacancy_score_weight=body.accordance_xp_vacancy_score_weight,
                    accordance_skill_vacancy_score_weight=body.accordance_skill_vacancy_score_weight,
                    accordance_xp_resume_score_weight=body.accordance_xp_resume_score_weight,
                    accordance_skill_resume_score_weight=body.accordance_skill_resume_score_weight,
                    red_flag_score_weight=body.red_flag_score_weight
                )

                self.logger.info("Vacancy criterion weights edited successfully", {"vacancy_id": body.vacancy_id})

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={"message": "Vacancy criterion weights updated successfully"}
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def create_resume_weight(self, body: CreateResumeWeightBody) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "VacancyController.create_resume_weight",
                kind=SpanKind.INTERNAL,
                attributes={"vacancy_id": body.vacancy_id}
        ) as span:
            try:
                self.logger.info("Creating resume weights", {"vacancy_id": body.vacancy_id})

                await self.vacancy_service.create_resume_weight(
                    vacancy_id=body.vacancy_id,
                    hard_skill_weight=body.hard_skill_weight,
                    work_xp_weight=body.work_xp_weight,
                    recommendation_weight=body.recommendation_weight,
                    portfolio_weight=body.portfolio_weight
                )

                self.logger.info("Resume weights created successfully", {"vacancy_id": body.vacancy_id})

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=201,
                    content={"message": "Resume weights created successfully"}
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def edit_resume_weight(self, body: EditResumeWeightBody) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "VacancyController.edit_resume_weight",
                kind=SpanKind.INTERNAL,
                attributes={"vacancy_id": body.vacancy_id}
        ) as span:
            try:
                self.logger.info("Editing resume weights", {"vacancy_id": body.vacancy_id})

                await self.vacancy_service.edit_resume_weight(
                    vacancy_id=body.vacancy_id,
                    hard_skill_weight=body.hard_skill_weight,
                    work_xp_weight=body.work_xp_weight,
                    recommendation_weight=body.recommendation_weight,
                    portfolio_weight=body.portfolio_weight
                )

                self.logger.info("Resume weights edited successfully", {"vacancy_id": body.vacancy_id})

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
                self.logger.info("Generating tags request")

                tags = await self.vacancy_service.generate_tags(body.vacancy_description)

                self.logger.info("Tags generated successfully", {
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
                self.logger.info("Generating questions request", {
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

                self.logger.info("Questions generated successfully", {
                    "vacancy_id": body.vacancy_id,
                    "generated_count": len(questions)
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
                self.logger.info("Evaluating resumes request", {
                    "vacancy_id": vacancy_id,
                    "resumes_count": len(candidate_resume_files)
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

                self.logger.info("Resumes evaluated successfully", {
                    "vacancy_id": vacancy_id,
                    "total_resumes": len(candidate_resume_files),
                    "approved_resumes": len(evaluation_resumes)
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
                self.logger.info("Processing candidate response", {
                    "vacancy_id": vacancy_id,
                    "candidate_email": candidate_email,
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
                    self.logger.info("Candidate approved for interview", {
                        "vacancy_id": vacancy_id,
                        "candidate_email": candidate_email,
                        "interview_link": interview_link
                    })
                    status_code = 200
                else:
                    self.logger.info("Candidate rejected", {
                        "vacancy_id": vacancy_id,
                        "candidate_email": candidate_email,
                        "accordance_xp_score": accordance_xp_score,
                        "accordance_skill_score": accordance_skill_score
                    })
                    status_code = 200  # Все еще успешный ответ, но без ссылки на интервью

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
                self.logger.info("Getting all vacancies request")

                vacancies = await self.vacancy_service.get_all_vacancy()

                # Конвертируем в словари для JSON ответа
                vacancies_dict = [vacancy.to_dict() for vacancy in vacancies]

                self.logger.info("All vacancies retrieved successfully", {
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
                self.logger.info("Getting all questions request", {"vacancy_id": vacancy_id})

                questions = await self.vacancy_service.get_all_question(vacancy_id)

                # Конвертируем в словари для JSON ответа
                questions_dict = [question.to_dict() for question in questions]

                self.logger.info("All questions retrieved successfully", {
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