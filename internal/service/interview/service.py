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
            audio_file: UploadFile
    ):
        pass
