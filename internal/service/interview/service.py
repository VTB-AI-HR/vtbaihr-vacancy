import json
import re
from datetime import datetime

from fastapi import UploadFile

from internal import model, interface


class InterviewService(interface.IInterviewService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            vacancy_repo: interface.IVacancyRepo,
            interview_repo: interface.IInterviewRepo,
            interview_prompt_generator: interface.IInterviewPromptGenerator,
            llm_client: interface.ILLMClient,
            storage: interface.IStorage
    ):
        self.logger = tel.logger()

        self.vacancy_repo = vacancy_repo
        self.interview_repo = interview_repo
        self.interview_prompt_generator = interview_prompt_generator
        self.llm_client = llm_client
        self.storage = storage

    async def start_interview(self, interview_id: int) -> tuple[str, int, int]:
        interview = (await self.interview_repo.get_interview_by_id(interview_id))[0]
        vacancy = (await self.vacancy_repo.get_vacancy_by_id(interview.vacancy_id))[0]
        questions = await self.vacancy_repo.get_all_question(vacancy.id)
        current_question = questions[0]

        hello_interview_system_prompt = self.interview_prompt_generator.get_hello_interview_system_prompt(
            vacancy,
            questions,
            interview.candidate_name,
        )

        history = [
            model.InterviewMessage(
                id=0,
                interview_id=0,
                question_id=0,
                audio_fid="0",
                role="user",
                text="Здравствуйте!",
                created_at=datetime.now()
            )
        ]

        hello_interview_str = await self.llm_client.generate(
            history=history,
            system_prompt=hello_interview_system_prompt
        )

        hello_interview = self.extract_and_parse_json(hello_interview_str)
        message_to_candidate = hello_interview["message_to_candidate"]

        llm_message_id = await self.interview_repo.create_interview_message(
            interview_id=interview_id,
            question_id=current_question.id,
            audio_fid="0",
            role="assistant",
            text=message_to_candidate,
        )

        candidate_answer_id = await self.interview_repo.create_candidate_answer(
            question_id=current_question.id,
            interview_id=interview_id,
        )

        await self.interview_repo.add_message_to_candidate_answer(
            message_id=llm_message_id,
            candidate_answer_id=candidate_answer_id
        )

        return message_to_candidate, len(questions), questions[0].id

    async def send_answer(
            self,
            vacancy_id: int,
            question_id: int,
            interview_id: int,
            audio_file: UploadFile
    ) -> tuple[int, str, dict]:
        try:
            # 1. Получаем необходимые данные
            vacancy = (await self.vacancy_repo.get_vacancy_by_id(vacancy_id))[0]
            questions = await self.vacancy_repo.get_all_question(vacancy_id)
            current_question_order_number = \
                [idx + 1 for idx, question in enumerate(questions) if question.id == question_id][0]
            current_question = questions[current_question_order_number - 1]
            candidate_answer = (await self.interview_repo.get_candidate_answer(question_id, interview_id))[0]

            # 2. Транскрибируем аудио
            audio_content = await audio_file.read()
            transcribed_text = await self.llm_client.transcribe_audio(audio_content, audio_file.filename)

            # 3. Сохраняем аудио в storage
            # audio_file_io = io.BytesIO(audio_content)
            # upload_response = self.storage.upload(audio_file_io, audio_file.filename)
            audio_fid = "423432"

            # 4. Создаем сообщение от кандидата
            candidate_message_id = await self.interview_repo.create_interview_message(
                interview_id=interview_id,
                question_id=question_id,
                audio_fid=audio_fid,
                role="user",
                text=transcribed_text
            )
            await self.interview_repo.add_message_to_candidate_answer(
                message_id=candidate_message_id,
                candidate_answer_id=candidate_answer.id
            )

            # 5. Определяем действие через LLM (continue, next_question, finish_interview)
            interview_management_system_prompt = self.interview_prompt_generator.get_interview_management_system_prompt(
                vacancy=vacancy,
                questions=questions,
                current_question_order_number=current_question_order_number
            )
            interview_messages = await self.interview_repo.get_interview_messages(interview_id)
            llm_response_str = await self.llm_client.generate(
                history=interview_messages,
                system_prompt=interview_management_system_prompt
            )
            self.logger.info("Ответ от LLM", {"llm_response": llm_response_str})

            llm_response = self.extract_and_parse_json(llm_response_str)
            action = llm_response["action"]
            message_to_candidate: str = llm_response["message_to_candidate"]

            llm_message_id = await self.interview_repo.create_interview_message(
                interview_id=interview_id,
                question_id=question_id,
                audio_fid="",
                role="assistant",
                text=message_to_candidate
            )

            # 7. Обрабатываем разные сценарии
            if action == "delve_into_question":
                await self.__continue_question(
                    llm_message_id=llm_message_id,
                    candidate_answer_id=candidate_answer.id,
                )
                return (
                    question_id,
                    message_to_candidate,
                    {}
                )

            elif action == "next_question" and current_question_order_number < len(questions):
                next_question = await self.__next_question(
                    interview_id=interview_id,
                    llm_message_id=llm_message_id,
                    candidate_answer_id=candidate_answer.id,
                    response_time=60,
                    current_question=current_question,
                    questions=questions,
                    vacancy=vacancy,
                    interview_messages=interview_messages,
                )
                return (
                    next_question.id,
                    message_to_candidate,
                    {}
                )

            elif action == "finish_interview" or action == "next_question" and current_question_order_number == len(
                    questions):
                interview = await self.__finish_interview(
                    interview_id=interview_id,
                    candidate_answer_id=candidate_answer.id,
                    response_time=60,
                    interview_messages=interview_messages,
                    vacancy=vacancy,
                    current_question=current_question,
                )
                return (
                    question_id,
                    message_to_candidate,
                    interview.to_dict()
                )

            return question_id, message_to_candidate, {}
        except Exception as err:
            raise err


    async def __continue_question(
            self,
            llm_message_id: int,
            candidate_answer_id: int
    ):

        await self.interview_repo.add_message_to_candidate_answer(
            message_id=llm_message_id,
            candidate_answer_id=candidate_answer_id
        )

    async def __next_question(
            self,
            interview_id: int,
            llm_message_id: int,
            candidate_answer_id: int,
            response_time: int,
            current_question: model.VacancyQuestion,
            questions: list[model.VacancyQuestion],
            vacancy: model.Vacancy,
            interview_messages: list[model.InterviewMessage],
    ) -> model.VacancyQuestion | None:
        await self.__evaluate_answer(
            candidate_answer_id=candidate_answer_id,
            response_time=response_time,
            current_question=current_question,
            vacancy=vacancy,
            interview_messages=interview_messages,
        )

        for i, question in enumerate(questions):
            if question.id == current_question.id and i + 1 < len(questions):
                next_question = questions[i + 1]

                next_candidate_message_id = await self.interview_repo.create_candidate_answer(
                    next_question.id,
                    interview_id
                )

                await self.interview_repo.add_message_to_candidate_answer(
                    message_id=llm_message_id,
                    candidate_answer_id=next_candidate_message_id
                )

                return next_question
        return None

    async def __finish_interview(
            self,
            interview_id: int,
            candidate_answer_id: int,
            response_time: int,
            interview_messages: list[model.InterviewMessage],
            vacancy: model.Vacancy,
            current_question: model.VacancyQuestion
    ) -> model.Interview:
        await self.__evaluate_answer(
            candidate_answer_id=candidate_answer_id,
            response_time=response_time,
            current_question=current_question,
            vacancy=vacancy,
            interview_messages=interview_messages,
        )

        interview_summary_system_prompt = self.interview_prompt_generator.get_interview_summary_system_prompt(
            vacancy=vacancy,
        )

        interview_messages = interview_messages + [
            model.InterviewMessage(
                id=0,
                interview_id=0,
                question_id=0,
                audio_fid="",
                role="user",
                text=f"Подведи итоги интервью",
                created_at=datetime.now(),
            )
        ]

        interview_evaluation_str = await self.llm_client.generate(
            history=interview_messages,
            system_prompt=interview_summary_system_prompt
        )

        interview_evaluation = self.extract_and_parse_json(interview_evaluation_str)

        general_score = 0.5
        general_result = model.GeneralResult.NEXT if general_score > 0.6 else model.GeneralResult.REJECTED

        await self.interview_repo.fill_interview_criterion(
            interview_id=interview_id,
            red_flag_score=interview_evaluation["red_flag_score"],
            hard_skill_score=interview_evaluation["hard_skill_score"],
            soft_skill_score=interview_evaluation["soft_skill_score"],
            logic_structure_score=interview_evaluation["logic_structure_score"],
            accordance_xp_resume_score=interview_evaluation["accordance_xp_resume_score"],
            accordance_skill_resume_score=interview_evaluation["accordance_skill_resume_score"],
            strong_areas=interview_evaluation["strong_areas"],
            weak_areas=interview_evaluation["weak_areas"],
            general_score=general_score,
            general_result=general_result,
            message_to_candidate=interview_evaluation["message_to_candidate"],
            message_to_hr=interview_evaluation["message_to_hr"],
        )

        interview_data = await self.interview_repo.get_interview_by_id(interview_id)
        return interview_data[0]

    async def __evaluate_answer(
            self,
            candidate_answer_id: int,
            response_time: int,
            current_question: model.VacancyQuestion,
            vacancy: model.Vacancy,
            interview_messages: list[model.InterviewMessage]
    ) -> None:
        answer_evaluation_system_prompt = self.interview_prompt_generator.get_answer_evaluation_system_prompt(
            question=current_question,
            vacancy=vacancy
        )
        question_history = [msg for msg in interview_messages if msg.question_id == current_question.id]
        question_history = question_history + [
            model.InterviewMessage(
                id=0,
                interview_id=0,
                question_id=0,
                audio_fid="",
                role="user",
                text=f"Оцени мой ответ",
                created_at=datetime.now(),
            )
        ]
        question_evaluation_str = await self.llm_client.generate(
            history=question_history,
            system_prompt=answer_evaluation_system_prompt
        )

        evaluation_data = self.extract_and_parse_json(question_evaluation_str)
        score = evaluation_data["score"]
        message_to_candidate = evaluation_data["message_to_candidate"]
        message_to_hr = evaluation_data["message_to_hr"]

        await self.interview_repo.evaluation_candidate_answer(
            candidate_answer_id=candidate_answer_id,
            score=score,
            message_to_hr=message_to_hr,
            message_to_candidate=message_to_candidate,
            response_time=response_time
        )

    async def get_all_interview(self, vacancy_id: int) -> list[model.Interview]:
        return await self.interview_repo.get_all_interview(vacancy_id)

    async def get_interview_details(
            self,
            interview_id: int
    ) -> tuple[list[model.CandidateAnswer], list[model.InterviewMessage]]:
        candidate_answers = await self.interview_repo.get_all_candidate_answer(interview_id)
        interview_messages = await self.interview_repo.get_interview_messages(interview_id)

        return candidate_answers, interview_messages

    def extract_and_parse_json(self, text: str) -> dict:
        match = re.search(r"\{.*\}", text, re.DOTALL)

        json_str = match.group(0)
        data = json.loads(json_str)
        return data

