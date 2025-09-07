import json
import io
from datetime import datetime
from fastapi import UploadFile

from opentelemetry.trace import SpanKind, Status, StatusCode

from internal import interface, model


class VacancyService(interface.IVacancyService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            vacancy_repo: interface.IVacancyRepo,
            interview_repo: interface.IInterviewRepo,
            storage: interface.IStorage,
            vacancy_prompt_generator: interface.IVacancyPromptGenerator,
            llm_client: interface.ILLMClient,
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.vacancy_repo = vacancy_repo
        self.interview_repo = interview_repo
        self.storage = storage
        self.vacancy_prompt_generator = vacancy_prompt_generator
        self.llm_client = llm_client

    async def create_vacancy(
            self,
            name: str,
            tags: list[str],
            description: str,
            red_flags: str,
            skill_lvl: model.SkillLevel,
    ) -> int:
        with self.tracer.start_as_current_span(
                "VacancyService.create_vacancy",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_name": name,
                    "skill_level": skill_lvl.value,
                }
        ) as span:
            try:
                self.logger.info("Creating new vacancy", {
                    "vacancy_name": name,
                    "skill_level": skill_lvl.value,
                    "tags_count": len(tags)
                })

                vacancy_id = await self.vacancy_repo.create_vacancy(
                    name=name,
                    tags=tags,
                    description=description,
                    red_flags=red_flags,
                    skill_lvl=skill_lvl
                )

                self.logger.info("Vacancy created successfully", {
                    "vacancy_id": vacancy_id,
                    "vacancy_name": name
                })

                span.set_status(Status(StatusCode.OK))
                return vacancy_id

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def delete_vacancy(self, vacancy_id: int) -> None:
        with self.tracer.start_as_current_span(
                "VacancyService.delete_vacancy",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": vacancy_id,
                }
        ) as span:
            try:
                self.logger.info("Deleting vacancy", {"vacancy_id": vacancy_id})

                await self.vacancy_repo.delete_vacancy(vacancy_id)

                self.logger.info("Vacancy deleted successfully", {"vacancy_id": vacancy_id})

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
                "VacancyService.edit_vacancy",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": vacancy_id,
                }
        ) as span:
            try:
                self.logger.info("Editing vacancy", {
                    "vacancy_id": vacancy_id,
                    "fields_to_update": {
                        "name": name is not None,
                        "tags": tags is not None,
                        "description": description is not None,
                        "red_flags": red_flags is not None,
                        "skill_lvl": skill_lvl is not None,
                    }
                })

                await self.vacancy_repo.edit_vacancy(
                    vacancy_id=vacancy_id,
                    name=name,
                    tags=tags,
                    description=description,
                    red_flags=red_flags,
                    skill_lvl=skill_lvl
                )

                self.logger.info("Vacancy edited successfully", {"vacancy_id": vacancy_id})

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
                "VacancyService.add_question",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": vacancy_id,
                    "question_type": question_type.value,
                    "weight": weight,
                }
        ) as span:
            try:
                self.logger.info("Adding question to vacancy", {
                    "vacancy_id": vacancy_id,
                    "question_type": question_type.value,
                    "weight": weight,
                    "response_time": response_time
                })

                question_id = await self.vacancy_repo.add_question(
                    vacancy_id=vacancy_id,
                    question=question,
                    hint_for_evaluation=hint_for_evaluation,
                    weight=weight,
                    question_type=question_type,
                    response_time=response_time
                )

                self.logger.info("Question added successfully", {
                    "question_id": question_id,
                    "vacancy_id": vacancy_id
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
            question: str | None,
            hint_for_evaluation: str | None,
            weight: int | None,
            question_type: model.QuestionsType | None,
            response_time: int | None,
    ) -> int:
        with self.tracer.start_as_current_span(
                "VacancyService.edit_question",
                kind=SpanKind.INTERNAL,
                attributes={
                    "question_id": question_id,
                }
        ) as span:
            try:
                self.logger.info("Editing question", {
                    "question_id": question_id,
                    "fields_to_update": {
                        "question": question is not None,
                        "hint_for_evaluation": hint_for_evaluation is not None,
                        "weight": weight is not None,
                        "question_type": question_type is not None,
                        "response_time": response_time is not None,
                    }
                })

                await self.vacancy_repo.edit_question(
                    question_id=question_id,
                    question=question,
                    hint_for_evaluation=hint_for_evaluation,
                    weight=weight,
                    question_type=question_type,
                    response_time=response_time
                )

                self.logger.info("Question edited successfully", {"question_id": question_id})

                span.set_status(Status(StatusCode.OK))
                return question_id

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def delete_question(self, question_id: int) -> None:
        with self.tracer.start_as_current_span(
                "VacancyService.delete_question",
                kind=SpanKind.INTERNAL,
                attributes={
                    "question_id": question_id,
                }
        ) as span:
            try:
                self.logger.info("Deleting question", {"question_id": question_id})

                await self.vacancy_repo.delete_question(question_id)

                self.logger.info("Question deleted successfully", {"question_id": question_id})

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
                "VacancyService.create_vacancy_criterion_weight",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": vacancy_id,
                }
        ) as span:
            try:
                self.logger.info("Creating vacancy criterion weights", {"vacancy_id": vacancy_id})

                await self.vacancy_repo.create_vacancy_criterion_weight(
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

                self.logger.info("Vacancy criterion weights created successfully", {"vacancy_id": vacancy_id})

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
                "VacancyService.edit_vacancy_criterion_weight",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": vacancy_id,
                }
        ) as span:
            try:
                self.logger.info("Editing vacancy criterion weights", {"vacancy_id": vacancy_id})

                await self.vacancy_repo.edit_vacancy_criterion_weight(
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

                self.logger.info("Vacancy criterion weights edited successfully", {"vacancy_id": vacancy_id})

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
                "VacancyService.create_resume_weight",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": vacancy_id,
                }
        ) as span:
            try:
                self.logger.info("Creating resume weights", {"vacancy_id": vacancy_id})

                await self.vacancy_repo.create_resume_weight(
                    vacancy_id=vacancy_id,
                    hard_skill_weight=hard_skill_weight,
                    work_xp_weight=work_xp_weight,
                    recommendation_weight=recommendation_weight,
                    portfolio_weight=portfolio_weight
                )

                self.logger.info("Resume weights created successfully", {"vacancy_id": vacancy_id})

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
                "VacancyService.edit_resume_weight",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": vacancy_id,
                }
        ) as span:
            try:
                self.logger.info("Editing resume weights", {"vacancy_id": vacancy_id})

                await self.vacancy_repo.edit_resume_weight(
                    vacancy_id=vacancy_id,
                    hard_skill_weight=hard_skill_weight,
                    work_xp_weight=work_xp_weight,
                    recommendation_weight=recommendation_weight,
                    portfolio_weight=portfolio_weight
                )

                self.logger.info("Resume weights edited successfully", {"vacancy_id": vacancy_id})

                span.set_status(Status(StatusCode.OK))

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def generate_tags(self, vacancy_description: str) -> list[str]:
        with self.tracer.start_as_current_span(
                "VacancyService.generate_tags",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                self.logger.info("Generating tags for vacancy description")

                generation_tag_system_prompt = self.vacancy_prompt_generator.get_generate_tags_system_prompt()

                history = [
                    model.InterviewMessage(
                        id=0,
                        interview_id=0,
                        question_id=0,
                        audio_fid="",
                        role="user",
                        text=f"Проанализируй описание вакансии и извлеки ключевые теги:\n\n{vacancy_description}",
                        created_at=datetime.now()
                    )
                ]

                llm_response = await self.llm_client.generate(
                    history=history,
                    system_prompt=generation_tag_system_prompt,
                    temperature=0.3
                )

                # Парсим JSON ответ
                try:
                    response_data = json.loads(llm_response)
                    tags = response_data.get("tags", [])
                except json.JSONDecodeError as e:
                    self.logger.error("Failed to parse LLM response for tags generation", {
                        "llm_response": llm_response,
                        "error": str(e)
                    })
                    raise ValueError(f"Invalid JSON response from LLM: {str(e)}")

                self.logger.info("Tags generated successfully", {
                    "tags_count": len(tags),
                    "tags": tags
                })

                span.set_status(Status(StatusCode.OK))
                return tags

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def generate_question(
            self,
            vacancy_id: int,
            questions_type: model.QuestionsType,
            count_questions: int,
    ) -> list[model.VacancyQuestion]:
        with self.tracer.start_as_current_span(
                "VacancyService.generate_question",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": vacancy_id,
                    "questions_type": questions_type.value,
                    "count_questions": count_questions,
                }
        ) as span:
            try:
                self.logger.info("Generating questions for vacancy", {
                    "vacancy_id": vacancy_id,
                    "questions_type": questions_type.value,
                    "count_questions": count_questions
                })

                # Получаем данные вакансии
                vacancy = (await self.vacancy_repo.get_vacancy_by_id(vacancy_id))[0]

                # Генерируем промпт
                question_generation_prompt = self.vacancy_prompt_generator.get_question_generation_prompt(
                    vacancy=vacancy,
                    count_questions=count_questions,
                    questions_type=questions_type
                )

                history = [
                    model.InterviewMessage(
                        id=0,
                        interview_id=0,
                        question_id=0,
                        audio_fid="",
                        role="user",
                        text="Сгенерируй вопросы для интервью согласно требованиям.",
                        created_at=datetime.now()
                    )
                ]

                llm_response = await self.llm_client.generate(
                    history=history,
                    system_prompt=question_generation_prompt,
                    temperature=0.7
                )

                # Парсим JSON ответ

                response_data = json.loads(llm_response)
                questions_data = response_data.get("questions", [])

                questions = []
                for q_data in questions_data:
                    question = model.VacancyQuestion(
                        id=0,
                        vacancy_id=vacancy_id,
                        question=q_data.get("question", "Нет вопроса"),
                        hint_for_evaluation=q_data.get("hint_for_evaluation", "Нет подсказки"),
                        weight=q_data.get("weight", 1),
                        question_type=model.QuestionsType(q_data.get("question_type", questions_type.value)),
                        response_time=q_data.get("response_time", 5),
                        created_at=datetime.now()
                    )
                    questions.append(question)

                self.logger.info("Questions generated successfully", {
                    "vacancy_id": vacancy_id,
                    "generated_count": len(questions)
                })

                span.set_status(Status(StatusCode.OK))
                return questions

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def evaluate_resume(self, vacancy_id: int, candidate_resume_files: list[UploadFile]) -> list[model.Interview]:
        with self.tracer.start_as_current_span(
                "VacancyService.evaluate_resume",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": vacancy_id,
                    "resumes_count": len(candidate_resume_files),
                }
        ) as span:
            try:
                self.logger.info("Evaluating resumes", {
                    "vacancy_id": vacancy_id,
                    "resumes_count": len(candidate_resume_files)
                })

                # Получаем данные вакансии
                vacancy = (await self.vacancy_repo.get_vacancy_by_id(vacancy_id))[0]

                # Генерируем промпт для оценки резюме
                system_prompt = self.vacancy_prompt_generator.get_resume_evaluation_system_prompt(
                    vacancy_description=vacancy.description,
                    vacancy_red_flags=vacancy.red_flags,
                    vacancy_name=vacancy.name,
                    vacancy_tags=vacancy.tags
                )

                created_interviews = []

                for resume_file in candidate_resume_files:

                    # Читаем файл резюме
                    resume_content = await resume_file.read()

                    # Создаем сообщение для LLM
                    history = [
                        model.InterviewMessage(
                            id=0,
                            interview_id=0,
                            question_id=0,
                            audio_fid="",
                            role="user",
                            text="Оцени это резюме и извлеки данные",
                            created_at=datetime.now()
                        )
                    ]

                    # Оцениваем резюме с помощью LLM
                    llm_response = await self.llm_client.generate(
                        history=history,
                        system_prompt=system_prompt,
                        pdf_file=resume_content
                    )

                    # Парсим ответ LLM
                    evaluation_data = json.loads(llm_response)

                    accordance_xp_score = evaluation_data.get("accordance_xp_vacancy_score", 0)
                    accordance_skill_score = evaluation_data.get("accordance_skill_vacancy_score", 0)

                    # Проверяем пороговые значения (4)
                    if accordance_xp_score >= 3 and accordance_skill_score >= 3:
                        # Сохраняем резюме в WeedFS
                        # resume_file_io = io.BytesIO(resume_content)
                        # upload_result = self.storage.upload(resume_file_io, resume_file.filename)
                        candidate_resume_fid = "45346545"

                        # Создаем интервью
                        interview_id = await self.interview_repo.create_interview(
                            vacancy_id=vacancy_id,
                            candidate_name=evaluation_data.get("candidate_name", "Unknown"),
                            candidate_email=evaluation_data.get("candidate_email", "unknown@example.com"),
                            candidate_phone=evaluation_data.get("candidate_phone", "Unknown"),
                            candidate_resume_fid=candidate_resume_fid,
                            accordance_xp_vacancy_score=accordance_xp_score,
                            accordance_skill_vacancy_score=accordance_skill_score
                        )

                        # Создаем объект Interview для возврата
                        interview = model.Interview(
                            id=interview_id,
                            vacancy_id=vacancy_id,
                            candidate_name=evaluation_data.get("candidate_name", "Unknown"),
                            candidate_email=evaluation_data.get("candidate_email", "unknown@example.com"),
                            candidate_phone=evaluation_data.get("candidate_phone", "Unknown"),
                            candidate_resume_fid=candidate_resume_fid,
                            accordance_xp_vacancy_score=accordance_xp_score,
                            accordance_skill_vacancy_score=accordance_skill_score,
                            red_flag_score=0,
                            hard_skill_score=0,
                            soft_skill_score=0,
                            logic_structure_score=0,
                            accordance_xp_resume_score=0,
                            accordance_skill_resume_score=0,
                            strong_areas="",
                            weak_areas="",
                            general_score=0.0,
                            general_result=model.GeneralResult.IN_PROCESS,
                            message_to_candidate=evaluation_data.get("message_to_candidate", ""),
                            message_to_hr=evaluation_data.get("message_to_hr", ""),
                            created_at=datetime.now()
                        )

                        created_interviews.append(interview)

                        self.logger.info("Resume passed evaluation, interview created", {
                            "interview_id": interview_id,
                            "accordance_xp_score": accordance_xp_score,
                            "accordance_skill_score": accordance_skill_score
                        })
                    else:
                        self.logger.info("Resume failed evaluation", {
                            "accordance_xp_score": accordance_xp_score,
                            "accordance_skill_score": accordance_skill_score
                        })

                self.logger.info("Resume evaluation completed", {
                    "vacancy_id": vacancy_id,
                    "total_resumes": len(candidate_resume_files),
                    "created_interviews": len(created_interviews)
                })

                span.set_status(Status(StatusCode.OK))
                return created_interviews

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def respond(
            self,
            vacancy_id: int,
            candidate_email: str,
            candidate_resume_file: UploadFile
    ) -> tuple[str, int, int]:
        with self.tracer.start_as_current_span(
                "VacancyService.respond",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": vacancy_id,
                    "candidate_email": candidate_email,
                }
        ) as span:
            try:
                self.logger.info("Processing candidate response", {
                    "vacancy_id": vacancy_id,
                    "candidate_email": candidate_email,
                    "filename": candidate_resume_file.filename
                })

                # Получаем данные вакансии
                vacancies = await self.vacancy_repo.get_vacancy_by_id(vacancy_id)
                if not vacancies:
                    raise ValueError(f"Vacancy with id {vacancy_id} not found")

                vacancy = vacancies[0]

                # Генерируем промпт для оценки резюме
                system_prompt = self.vacancy_prompt_generator.get_resume_evaluation_system_prompt(
                    vacancy_description=vacancy.description,
                    vacancy_red_flags=vacancy.red_flags,
                    vacancy_name=vacancy.name,
                    vacancy_tags=vacancy.tags
                )

                # Читаем файл резюме
                resume_content = await candidate_resume_file.read()

                # Создаем сообщение для LLM
                history = [
                    model.InterviewMessage(
                        id=0,
                        interview_id=0,
                        question_id=0,
                        audio_fid="",
                        role="user",
                        text="Оцени это резюме и извлеки данные кандидата",
                        created_at=datetime.now()
                    )
                ]

                # Оцениваем резюме с помощью LLM
                llm_response = await self.llm_client.generate(
                    history=history,
                    system_prompt=system_prompt,
                    pdf_file=resume_content
                )

                # Парсим ответ LLM

                evaluation_data = json.loads(llm_response)

                accordance_xp_score = evaluation_data.get("accordance_xp_vacancy_score", 0)
                accordance_skill_score = evaluation_data.get("accordance_skill_vacancy_score", 0)

                # Проверяем пороговые значения (например, 3 из 5)
                if accordance_xp_score >= 3 and accordance_skill_score >= 3:
                    # Сохраняем резюме в WeedFS
                    resume_file_io = io.BytesIO(resume_content)
                    upload_result = self.storage.upload(resume_file_io, candidate_resume_file.filename)
                    candidate_resume_fid = upload_result.fid

                    # Создаем интервью
                    interview_id = await self.interview_repo.create_interview(
                        vacancy_id=vacancy_id,
                        candidate_name=evaluation_data.get("candidate_name", "Unknown"),
                        candidate_email=candidate_email,  # Используем email из параметров
                        candidate_phone=evaluation_data.get("candidate_phone", "Unknown"),
                        candidate_resume_fid=candidate_resume_fid,
                        accordance_xp_vacancy_score=accordance_xp_score,
                        accordance_skill_vacancy_score=accordance_skill_score
                    )

                    # Генерируем ссылку на интервью
                    interview_link = f"/interview/start/{interview_id}"

                    self.logger.info("Candidate resume approved, interview created", {
                        "vacancy_id": vacancy_id,
                        "candidate_email": candidate_email,
                        "interview_id": interview_id,
                        "accordance_xp_score": accordance_xp_score,
                        "accordance_skill_score": accordance_skill_score,
                        "filename": candidate_resume_file.filename
                    })

                    span.set_status(Status(StatusCode.OK))
                    return interview_link, accordance_xp_score, accordance_skill_score

                else:
                    self.logger.info("Candidate resume rejected - scores below threshold", {
                        "vacancy_id": vacancy_id,
                        "candidate_email": candidate_email,
                        "accordance_xp_score": accordance_xp_score,
                        "accordance_skill_score": accordance_skill_score,
                        "min_threshold": 4,
                        "filename": candidate_resume_file.filename
                    })

                    # Возвращаем пустую ссылку при отклонении
                    span.set_status(Status(StatusCode.OK))
                    return "", accordance_xp_score, accordance_skill_score

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
                self.logger.info("Retrieving all vacancies")

                vacancies = await self.vacancy_repo.get_all_vacancy()

                self.logger.info("Successfully retrieved all vacancies", {
                    "vacancies_count": len(vacancies)
                })

                span.set_status(Status(StatusCode.OK))
                return vacancies

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_all_question(self, vacancy_id: int) -> list[model.VacancyQuestion]:
        with self.tracer.start_as_current_span(
                "VacancyService.get_all_question",
                kind=SpanKind.INTERNAL,
                attributes={
                    "vacancy_id": vacancy_id,
                }
        ) as span:
            try:
                self.logger.info("Retrieving all questions for vacancy", {
                    "vacancy_id": vacancy_id
                })

                # Проверяем существование вакансии
                vacancies = await self.vacancy_repo.get_vacancy_by_id(vacancy_id)
                if not vacancies:
                    raise ValueError(f"Vacancy with id {vacancy_id} not found")

                questions = await self.vacancy_repo.get_all_question(vacancy_id)

                self.logger.info("Successfully retrieved all questions for vacancy", {
                    "vacancy_id": vacancy_id,
                    "questions_count": len(questions)
                })

                span.set_status(Status(StatusCode.OK))
                return questions

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err
