create_vacancy = """
INSERT INTO vacancies (
    name,
    tags,
    description,
    red_flags,
    skill_lvl,
    question_response_time,
    questions_type
)
VALUES (
    :name,
    :tags,
    :description,
    :red_flags,
    :skill_lvl,
    :question_response_time,
    :questions_type
)
RETURNING id;
"""

delete_vacancy = """
DELETE FROM vacancies
WHERE id = :vacancy_id;
"""

add_question = """
INSERT INTO vacancy_questions (
    vacancy_id,
    question,
    hint_for_evaluation,
    weight,
    question_type
)
VALUES (
    :vacancy_id,
    :question,
    :hint_for_evaluation,
    :weight,
    :question_type
)
RETURNING id;
"""

edit_question = """
UPDATE vacancy_questions
SET 
    question = COALESCE(:question, question),
    hint_for_evaluation = COALESCE(:hint_for_evaluation, hint_for_evaluation),
    weight = COALESCE(:weight, weight),
    question_type = COALESCE(:question_type, question_type)
WHERE id = :question_id AND vacancy_id = :vacancy_id;
"""

delete_question = """
DELETE FROM vacancy_questions
WHERE id = :question_id;
"""

create_vacancy_criterion_weights = """
INSERT INTO vacancy_criterion_weights (
    vacancy_id,
    logic_structure_score_weight,
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

edit_vacancy_criterion_weights = """
UPDATE vacancy_criterion_weights
SET 
    logic_structure_score_weight = COALESCE(:logic_structure_score_weight, logic_structure_score_weight),
    soft_skill_score_weight = COALESCE(:soft_skill_score_weight, soft_skill_score_weight),
    hard_skill_score_weight = COALESCE(:hard_skill_score_weight, hard_skill_score_weight),
    accordance_xp_vacancy_score_weight = COALESCE(:accordance_xp_vacancy_score_weight, accordance_xp_vacancy_score_weight),
    accordance_skill_vacancy_score_weight = COALESCE(:accordance_skill_vacancy_score_weight, accordance_skill_vacancy_score_weight),
    accordance_xp_resume_score_weight = COALESCE(:accordance_xp_resume_score_weight, accordance_xp_resume_score_weight),
    accordance_skill_resume_score_weight = COALESCE(:accordance_skill_resume_score_weight, accordance_skill_resume_score_weight),
    red_flag_score_weight = COALESCE(:red_flag_score_weight, red_flag_score_weight)
WHERE vacancy_id = :vacancy_id;
"""

get_all_vacancy = """
SELECT * FROM vacancies
ORDER BY created_at DESC;
"""

get_all_question = """
SELECT * FROM vacancy_questions
WHERE vacancy_id = :vacancy_id
"""

get_vacancy_by_id = """
SELECT * FROM vacancies
WHERE id = :vacancy_id;
"""

get_question_by_id = """
SELECT * FROM vacancy_questions
WHERE id = :question_id;
"""