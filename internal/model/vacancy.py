from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class SkillLevel(Enum):
    JUNIOR = "junior"
    MIDDLE = "middle"
    SENIOR = "senior"
    LEAD = "lead"


class QuestionsType(Enum):
    SOFT = "soft"
    HARD = "hard"
    SOFT_HARD = "soft-hard"

class GeneralResult(Enum):
    NEXT = "next"
    REJECTED = "rejected"


@dataclass
class Vacancy:
    id: int
    name: str
    tags: List[str]
    description: str
    red_flags: str
    skill_lvl: SkillLevel
    question_response_time: int
    questions_type: QuestionsType

    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> List['Vacancy']:
        return [
            cls(
                id=row.id,
                name=row.name,
                tags=row.tags,
                description=row.description,
                red_flags=row.red_flags,
                skill_lvl=SkillLevel(row.skill_lvl),
                question_response_time=row.question_response_time,
                questions_type=QuestionsType(row.questions_type),
                created_at=row.created_at
            )
            for row in rows
        ]

@dataclass
class VacancyQuestion:
    id: int
    vacancy_id: int
    question: str
    hint: str
    weight: int  # [0;10]
    question_type: QuestionsType

    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> List['VacancyQuestion']:
        return [
            cls(
                id=row.id,
                vacancy_id=row.vacancy_id,
                question=row.question,
                hint=row.hint,
                weight=row.weight,
                question_type=QuestionsType(row.question_type),
                created_at=row.created_at
            )
            for row in rows
        ]


@dataclass
class Interview:
    id: int
    vacancy_id: int
    candidate_email: str
    candidate_resume_fid: str  # file_id
    general_score: float  # [0;1]
    general_result: GeneralResult
    general_recommendation: str
    red_flag_score: float  # [0;1]
    hard_skill_score: float  # [0;1]
    soft_skill_score: float  # [0;1]
    logic_structure_score: float  # [0;1]
    accordance_xp_vacancy_score: float  # [0;1]
    accordance_skill_vacancy_score: float  # [0;1]
    accordance_xp_resume_score: float  # [0;1]
    accordance_skill_resume_score: float  # [0;1]
    strong_areas: str
    weak_areas: str
    pause_detection_score: float  # [0;1]
    emotional_coloring: str

    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> List['Interview']:
        return [
            cls(
                id=row.id,
                vacancy_id=row.vacancy_id,
                candidate_email=row.candidate_email,
                candidate_resume_fid=row.candidate_resume_fid,
                general_score=row.general_score,
                general_result=GeneralResult(row.general_result),
                general_recommendation=row.general_recommendation,
                red_flag_score=row.red_flag_score,
                hard_skill_score=row.hard_skill_score,
                soft_skill_score=row.soft_skill_score,
                logic_structure_score=row.logic_structure_score,
                accordance_xp_vacancy_score=row.accordance_xp_vacancy_score,
                accordance_skill_vacancy_score=row.accordance_skill_vacancy_score,
                accordance_xp_resume_score=row.accordance_xp_resume_score,
                accordance_skill_resume_score=row.accordance_skill_resume_score,
                strong_areas=row.strong_areas,
                weak_areas=row.weak_areas,
                pause_detection_score=row.pause_detection_score,
                emotional_coloring=row.emotional_coloring,
                created_at=row.created_at
            )
            for row in rows
        ]


@dataclass
class InterviewWeights:
    id: int
    vacancy_id: int
    logic_structure_score_weight: int  # [0;10]
    pause_detection_score_weight: int  # [0;10]
    soft_skill_score_weight: int  # [0;10]
    hard_skill_score_weight: int  # [0;10]
    accordance_xp_vacancy_score_weight: int  # [0;10]
    accordance_skill_vacancy_score_weight: int  # [0;10]
    accordance_xp_resume_score_weight: int  # [0;10]
    accordance_skill_resume_score_weight: int  # [0;10]
    red_flag_score_weight: int  # [0;10]

    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> List['InterviewWeights']:
        return [
            cls(
                id=row.id,
                vacancy_id=row.vacancy_id,
                logic_structure_score_weight=row.logic_structure_score_weight,
                pause_detection_score_weight=row.pause_detection_score_weight,
                soft_skill_score_weight=row.soft_skill_score_weight,
                hard_skill_score_weight=row.hard_skill_score_weight,
                accordance_xp_vacancy_score_weight=row.accordance_xp_vacancy_score_weight,
                accordance_skill_vacancy_score_weight=row.accordance_skill_vacancy_score_weight,
                accordance_xp_resume_score_weight=row.accordance_xp_resume_score_weight,
                accordance_skill_resume_score_weight=row.accordance_skill_resume_score_weight,
                red_flag_score_weight=row.red_flag_score_weight,
                created_at=row.created_at
            )
            for row in rows
        ]


@dataclass
class QuestionResponse:
    id: int
    question_id: int
    interview_id: int
    response_time: int
    ask_text: str
    ask_audio_fid: str  # file_id
    llm_comment: str
    score: int  # [0;10]

    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> List['QuestionResponse']:
        return [
            cls(
                id=row.id,
                question_id=row.question_id,
                interview_id=row.interview_id,
                response_time=row.response_time,
                ask_text=row.ask_text,
                ask_audio_fid=row.ask_audio_fid,
                llm_comment=row.llm_comment,
                score=row.score,
                created_at=row.created_at
            )
            for row in rows
        ]
