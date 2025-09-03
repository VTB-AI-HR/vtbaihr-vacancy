import io
import json
from datetime import datetime

from fastapi import UploadFile

from internal import model, interface


class InterviewService(interface.IInterviewService):
    def __init__(
            self,
            vacancy_repo: interface.IVacancyRepo,
            interview_repo: interface.IInterviewRepo,
            interview_prompt_generator: interface.IInterviewPromptGenerator,
            llm_client: interface.ILLMClient,
            storage: interface.IStorage
    ):
        self.vacancy_repo = vacancy_repo
        self.interview_repo = interview_repo
        self.interview_prompt_generator = interview_prompt_generator
        self.llm_client = llm_client
        self.storage = storage

    async def start_interview(
            self,
            vacancy_id: int,
            candidate_email: str,
            candidate_resume_file: UploadFile
    ) -> tuple[bool, str, int, int]:
        vacancy = await self.vacancy_repo.get_vacancy_by_id(vacancy_id)
        if not vacancy:
            raise Exception("Vacancy not found")
        vacancy = vacancy[0]

        # Оцениваем резюме с помощью LLM
        resume_evaluation_system_prompt = self.interview_prompt_generator.get_resume_evaluation_system_prompt(
            vacancy.description,
            vacancy.red_flags,
            vacancy.name,
            vacancy.tags,
        )
        history = [
            model.InterviewMessage(
                id=0,
                interview_id=0,
                question_id=0,
                audio_fid="",
                role="user",
                text="Проверь, подходит ли резюме к вакансии",
                created_at=datetime.now(),
            )
        ]
        candidate_resume_filename = candidate_resume_file.filename
        candidate_resume_file = await candidate_resume_file.read()

        resume_evaluation_str = await self.llm_client.generate(
            history=history,
            system_prompt=resume_evaluation_system_prompt,
            pdf_file=candidate_resume_file
        )

        resume_evaluation: dict = json.loads(resume_evaluation_str)

        is_suitable: bool = resume_evaluation["is_suitable"]
        llm_response: str = resume_evaluation["llm_response"]

        if is_suitable:
            total_question = len(await self.vacancy_repo.get_all_question(vacancy_id))
        else:
            total_question = 0

        # Сохраняем файл резюме
        candidate_resume_file_io = io.BytesIO(candidate_resume_file)
        upload_response = self.storage.upload(
            file=candidate_resume_file_io,
            name=candidate_resume_filename
        )
        candidate_resume_fid = upload_response.fid

        # Создаем интервью в БД
        interview_id = await self.interview_repo.create_interview(
            vacancy_id,
            candidate_email,
            candidate_resume_fid,
        )

        return is_suitable, llm_response, total_question, interview_id

    async def send_answer(
            self,
            vacancy_id: int,
            question_id: int,
            interview_id: int,
            audio_file: UploadFile
    ):
        try:
            # 1. Получаем необходимые данные
            vacancy = (await self.vacancy_repo.get_vacancy_by_id(vacancy_id))[0]
            questions = await self.vacancy_repo.get_all_question(vacancy_id)
            current_question = next((q for q in questions if q.id == question_id), None)

            # 2. Транскрибируем аудио
            audio_content = await audio_file.read()
            transcribed_text = await self.llm_client.transcribe_audio(audio_content, audio_file.filename)

            # 3. Сохраняем аудио в storage
            audio_file_io = io.BytesIO(audio_content)
            upload_response = self.storage.upload(audio_file_io, audio_file.filename)
            audio_fid = upload_response.fid

            # 4. Создаем сообщение интервью
            message_id = await self.interview_repo.create_interview_message(
                interview_id=interview_id,
                question_id=question_id,
                audio_fid=audio_fid,
                role="user",
                text=transcribed_text
            )

            # 5. Определяем действие через LLM (continue, next_question, finish_interview)
            interview_messages = await self.interview_repo.get_interview_messages(interview_id)
            interview_management_system_prompt = self.interview_prompt_generator.get_interview_management_system_prompt(
                vacancy=vacancy,
                questions=questions
            )

            management_response = await self.llm_client.generate(
                history=interview_messages,
                system_prompt=interview_management_system_prompt
            )

            management_data = json.loads(management_response)
            action = management_data["action"]
            user_message = management_data["user_message"]

            # 6. Обрабатываем разные сценарии
            if action == "continue":
                await self.__continue_question(
                    question_id,
                    interview_id,
                    message_id
                )

            elif action == "next_question":
                # Оцениваем ответ


                if action == "finish_interview":

                else:
                    # Переход к следующему вопросу
                    return SendAnswerResponse(
                        question_id=question_id,
                        llm_response=llm_message,
                        question_order_number=current_question_num,
                        interview_result={}
                    )

        except json.JSONDecodeError as e:
            # Обработка ошибок парсинга JSON
            raise Exception(f"Failed to parse LLM response: {e}")
        except Exception as e:
            # Общая обработка ошибок
            raise Exception(f"Error in send_answer: {e}")

    async def __continue_question(
            self,
            question_id: int,
            interview_id: int,
            message_id: int
    ):
        candidate_answer = await self.interview_repo.get_candidate_answer(question_id, interview_id)
        if not candidate_answer:
            await self.interview_repo.create_candidate_answer(
                question_id=question_id,
                interview_id=interview_id,
                message_id=message_id
            )
        else:
            candidate_answer_id = candidate_answer[0].id
            await self.interview_repo.add_message_to_candidate_answer(
                message_id=message_id,
                candidate_answer_id=candidate_answer_id
            )

    async def __next_question(
            self,
            interview_id: int,
            current_question: model.VacancyQuestion,
            vacancy: model.Vacancy,
            interview_messages: list[model.InterviewMessage],
    ):
        answer_evaluation_system_prompt = self.interview_prompt_generator.get_answer_evaluation_system_prompt(
            question=current_question,
            vacancy=vacancy
        )

        # Собираем все сообщения кандидата для данного вопроса
        question_messages = [msg for msg in interview_messages if msg.question_id == current_question.id]
        evaluation_history = question_messages + [
            model.InterviewMessage(
                id=0,
                interview_id=interview_id,
                question_id=current_question.id,
                audio_fid="",
                role="user",
                text=transcribed_text,
                created_at=datetime.now()
            )
        ]

        evaluation_response = await self.llm_client.generate(
            history=evaluation_history,
            system_prompt=evaluation_prompt
        )

        evaluation_data = json.loads(evaluation_response)
        score = evaluation_data["score"]
        comment = evaluation_data["comment"]

        # Создаем candidate_answer и оцениваем его
        candidate_answer_id = await self.interview_repo.create_candidate_answer(
            question_id=question_id,
            interview_id=interview_id,
            message_id=message_id
        )

        await self.interview_repo.add_message_to_candidate_answer(
            message_id=message_id,
            candidate_answer_id=candidate_answer_id
        )

        # Здесь нужно вычислить response_time (предполагаем, что клиент передает)
        response_time = 60  # Заглушка, должно приходить от клиента

        await self.interview_repo.evaluation_candidate_answer(
            candidate_answer_id=candidate_answer_id,
            score=score,
            llm_comment=comment,
            response_time=response_time
        )

    async def __finish_interview(
            self,
            interview_id: int,
    ):
        # Подводим итоги интервью
        candidate_answers = await self.interview_repo.get_candidate_answers(interview_id)

        summary_prompt = self.interview_prompt_generator.get_interview_summary_system_prompt(
            vacancy=vacancy,
            interview_messages=interview_messages,
            candidate_answers=candidate_answers
        )

        summary_response = await self.llm_client.generate(
            history=[],
            system_prompt=summary_prompt
        )

        summary_data = json.loads(summary_response)

        # Сохраняем критерии интервью
        await self.interview_repo.fill_interview_criterion(
            interview_id=str(interview_id),
            red_flag_score=summary_data["red_flag_score"],
            hard_skill_score=summary_data["hard_skill_score"],
            soft_skill_score=summary_data["soft_skill_score"],
            logic_structure_score=summary_data["logic_structure_score"],
            accordance_xp_vacancy_score=summary_data["accordance_xp_vacancy_score"],
            accordance_skill_vacancy_score=summary_data["accordance_skill_vacancy_score"],
            accordance_xp_resume_score=summary_data["accordance_xp_resume_score"],
            accordance_skill_resume_score=summary_data["accordance_skill_resume_score"],
            strong_areas=summary_data["strong_areas"],
            weak_areas=summary_data["weak_areas"],
            pause_detection_score=summary_data["pause_detection_score"],
            emotional_coloring=summary_data["emotional_coloring"]
        )

        # Рассчитываем и сохраняем общий результат (заглушка)
        general_score = 0.5  # Здесь должна быть формула расчета
        general_result = model.GeneralResult.NEXT if general_score > 0.6 else model.GeneralResult.REJECTED
        general_recommendation = "Рекомендация на основе интервью"

        await self.interview_repo.add_general_result(
            vacancy_id=vacancy_id,
            general_score=general_score,
            general_result=general_result,
            general_recommendation=general_recommendation
        )

        # Возвращаем финальный результат с полными данными интервью
        interview_data = await self.interview_repo.get_interview_by_id(interview_id)
        return SendAnswerResponse(
            question_id=question_id,
            llm_response=llm_message,
            question_order_number=current_question_num,
            interview_result=interview_data[0].__dict__ if interview_data else {}
        )