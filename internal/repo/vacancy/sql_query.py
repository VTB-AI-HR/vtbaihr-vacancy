# SQL queries for VacancyRepo

create_vacancy_query = """
INSERT INTO vacancies (
    name,
    tags,
    description,
    red_flags,
    skill_lvl
)
VALUES (
    :name,
    :tags,
    :description,
    :red_flags,
    :skill_lvl
)
RETURNING id;
"""

delete_vacancy_query = """
DELETE FROM vacancies
WHERE id = :vacancy_id;
"""

add_question_query = """
INSERT INTO vacancy_questions (
    vacancy_id,
    question,
    hint_for_evaluation,
    weight,
    question_type,
    response_time
)
VALUES (
    :vacancy_id,
    :question,
    :hint_for_evaluation,
    :weight,
    :question_type,
    :response_time
)
RETURNING id;
"""

delete_question_query = """
DELETE FROM vacancy_questions
WHERE id = :question_id;
"""

create_vacancy_criterion_weight_query = """
INSERT INTO vacancy_criterion_weights (
    vacancy_id,
    logic_structure_score_weight,
    pause_detection_score_weight,
    soft_skill_score_weight,
    hard_skill_score_weight,
    accordance_xp_vacancy_score_weight,
    accordance_skill_vacancy_score_weight,
    accordance_xp_resume_score_weight,
    accordance_skill_resume_score_weight,
    red_flag_score_weight
)
VALUES (
    :vacancy_id,
    :logic_structure_score_weight,
    :pause_detection_score_weight,
    :soft_skill_score_weight,
    :hard_skill_score_weight,
    :accordance_xp_vacancy_score_weight,
    :accordance_skill_vacancy_score_weight,
    :accordance_xp_resume_score_weight,
    :accordance_skill_resume_score_weight,
    :red_flag_score_weight
)
RETURNING id;
"""

create_resume_weight_query = """
INSERT INTO resume_criterion_weights (
    vacancy_id,
    hard_skill_weight,
    work_xp_weight,
    recommendation_weight,
    portfolio_weight
)
VALUES (
    :vacancy_id,
    :hard_skill_weight,
    :work_xp_weight,
    :recommendation_weight,
    :portfolio_weight
)
RETURNING id;
"""

get_all_vacancy_query = """
SELECT * FROM vacancies
ORDER BY created_at DESC;
"""

get_vacancy_by_id_query = """
SELECT * FROM vacancies
WHERE id = :vacancy_id;
"""

get_all_question_query = """
SELECT * FROM vacancy_questions
WHERE vacancy_id = :vacancy_id
ORDER BY created_at;
"""

get_question_by_id_query = """
SELECT * FROM vacancy_questions
WHERE id = :question_id;
"""

get_vacancy_criterion_weights_query = """
SELECT * FROM vacancy_criterion_weights
WHERE vacancy_id = :vacancy_id;
"""

get_resume_criterion_weights_query = """
SELECT * FROM resume_criterion_weights
WHERE vacancy_id = :vacancy_id;
"""