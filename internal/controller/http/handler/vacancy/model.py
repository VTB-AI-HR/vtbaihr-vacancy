from pydantic import BaseModel
from internal import model

class CreateVacancyBody(BaseModel):
    name: str
    tags: list[str]
    description: str
    red_flags: str
    skill_lvl: model.SkillLevel
    question_response_time: int

class GenerateQuestionBody(BaseModel):
    vacancy_id: int
    questions_type: model.QuestionsType
    count_questions: int

class GenerateQuestionResponse(BaseModel):
    """
    {
        "question": str,
        "question_type": str
    }
    """
    questions: list[dict]

class AddQuestionBody(BaseModel):
    vacancy_id: int
    question: str
    hint_for_evaluation: str
    weight: int  # [0;10]
    question_type: model.QuestionsType

class EditQuestionBody(BaseModel):
    vacancy_id: int
    question: str | None
    hint_for_evaluation: str | None
    weight: int | None  # [0;10] 
    question_type: model.QuestionsType | None

class EditVacancyCriterionWeightsBody(BaseModel):
    vacancy_id: int
    logic_structure_score_weight: int | None 
    pause_detection_score_weight: int  | None
    soft_skill_score_weight: int  | None
    hard_skill_score_weight: int | None
    accordance_xp_vacancy_score_weight: int | None
    accordance_skill_vacancy_score_weight: int | None
    accordance_xp_resume_score_weight: int  | None
    accordance_skill_resume_score_weight: int  | None
    red_flag_score_weight: int | None
