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


@dataclass
class Vacancy:
    id: int
    name: str
    tags: list[str]
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

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "tags": self.tags,
            "description": self.description,
            "red_flags": self.red_flags,
            "skill_lvl": self.skill_lvl.value,
            "question_response_time": self.question_response_time,
            "questions_type": self.questions_type.value,
        }

@dataclass
class VacancyQuestion:
    id: int
    vacancy_id: int
    order_number: int
    question: str
    hint_for_evaluation: str
    weight: int
    question_type: QuestionsType

    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> List['VacancyQuestion']:
        return [
            cls(
                id=row.id,
                vacancy_id=row.vacancy_id,
                order_number=row.order_number,
                question=row.question,
                hint_for_evaluation=row.hint_for_evaluation,
                weight=row.weight,
                question_type=QuestionsType(row.question_type),
                created_at=row.created_at
            )
            for row in rows
        ]


@dataclass
class VacancyCriterionWeights:
    id: int
    vacancy_id: int
    logic_structure_score_weight: int  # [0;10]
    soft_skill_score_weight: int  # [0;10]
    hard_skill_score_weight: int  # [0;10]
    accordance_xp_vacancy_score_weight: int  # [0;10]
    accordance_skill_vacancy_score_weight: int  # [0;10]
    accordance_xp_resume_score_weight: int  # [0;10]
    accordance_skill_resume_score_weight: int  # [0;10]
    red_flag_score_weight: int  # [0;10]

    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> List['VacancyCriterionWeights']:
        return [
            cls(
                id=row.id,
                vacancy_id=row.vacancy_id,
                logic_structure_score_weight=row.logic_structure_score_weight,
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