create_vacancy_table = """
CREATE TABLE IF NOT EXISTS vacancies(
    id SERIAL PRIMARY KEY,

    name TEXT NOT NULL,
    tags TEXT[] NOT NULL DEFAULT '{}',
    description TEXT NOT NULL,
    red_flags TEXT NOT NULL DEFAULT '',
    skill_lvl TEXT NOT NULL CHECK (skill_lvl IN ('junior', 'middle', 'senior', 'lead')),
    question_response_time INTEGER NOT NULL DEFAULT 60,
    questions_type TEXT NOT NULL CHECK (questions_type IN ('soft', 'hard', 'soft-hard')),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

create_vacancy_questions_table = """
CREATE TABLE IF NOT EXISTS vacancy_questions(
    id SERIAL PRIMARY KEY,
    vacancy_id INTEGER NOT NULL REFERENCES vacancies(id) ON DELETE CASCADE,
    
    question TEXT NOT NULL,
    hint TEXT NOT NULL DEFAULT '',
    weight INTEGER NOT NULL DEFAULT 5 CHECK (weight >= 0 AND weight <= 10),
    question_type TEXT NOT NULL CHECK (question_type IN ('soft', 'hard', 'soft-hard')),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

create_interviews_table = """
CREATE TABLE IF NOT EXISTS interviews(
    id SERIAL PRIMARY KEY,
    vacancy_id INTEGER NOT NULL REFERENCES vacancies(id) ON DELETE CASCADE,
    
    candidate_email TEXT NOT NULL,
    candidate_resume_fid TEXT NOT NULL,
    general_score DECIMAL(3,2) NOT NULL CHECK (general_score >= 0 AND general_score <= 1),
    general_result TEXT NOT NULL CHECK (general_result IN ('next', 'rejected')),
    general_recommendation TEXT NOT NULL DEFAULT '',
    red_flag_score DECIMAL(3,2) NOT NULL CHECK (red_flag_score >= 0 AND red_flag_score <= 1),
    hard_skill_score DECIMAL(3,2) NOT NULL CHECK (hard_skill_score >= 0 AND hard_skill_score <= 1),
    soft_skill_score DECIMAL(3,2) NOT NULL CHECK (soft_skill_score >= 0 AND soft_skill_score <= 1),
    logic_structure_score DECIMAL(3,2) NOT NULL CHECK (logic_structure_score >= 0 AND logic_structure_score <= 1),
    accordance_xp_vacancy_score DECIMAL(3,2) NOT NULL CHECK (accordance_xp_vacancy_score >= 0 AND accordance_xp_vacancy_score <= 1),
    accordance_skill_vacancy_score DECIMAL(3,2) NOT NULL CHECK (accordance_skill_vacancy_score >= 0 AND accordance_skill_vacancy_score <= 1),
    accordance_xp_resume_score DECIMAL(3,2) NOT NULL CHECK (accordance_xp_resume_score >= 0 AND accordance_xp_resume_score <= 1),
    accordance_skill_resume_score DECIMAL(3,2) NOT NULL CHECK (accordance_skill_resume_score >= 0 AND accordance_skill_resume_score <= 1),
    strong_areas TEXT NOT NULL DEFAULT '',
    weak_areas TEXT NOT NULL DEFAULT '',
    pause_detection_score DECIMAL(3,2) NOT NULL CHECK (pause_detection_score >= 0 AND pause_detection_score <= 1),
    emotional_coloring TEXT NOT NULL DEFAULT '',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
"""

create_interview_weights_table = """
CREATE TABLE IF NOT EXISTS interview_weights(
    id SERIAL PRIMARY KEY,
    vacancy_id INTEGER NOT NULL REFERENCES vacancies(id) ON DELETE CASCADE,
    
    logic_structure_score_weight INTEGER NOT NULL DEFAULT 5 CHECK (logic_structure_score_weight >= 0 AND logic_structure_score_weight <= 10),
    pause_detection_score_weight INTEGER NOT NULL DEFAULT 5 CHECK (pause_detection_score_weight >= 0 AND pause_detection_score_weight <= 10),
    soft_skill_score_weight INTEGER NOT NULL DEFAULT 5 CHECK (soft_skill_score_weight >= 0 AND soft_skill_score_weight <= 10),
    hard_skill_score_weight INTEGER NOT NULL DEFAULT 5 CHECK (hard_skill_score_weight >= 0 AND hard_skill_score_weight <= 10),
    accordance_xp_vacancy_score_weight INTEGER NOT NULL DEFAULT 5 CHECK (accordance_xp_vacancy_score_weight >= 0 AND accordance_xp_vacancy_score_weight <= 10),
    accordance_skill_vacancy_score_weight INTEGER NOT NULL DEFAULT 5 CHECK (accordance_skill_vacancy_score_weight >= 0 AND accordance_skill_vacancy_score_weight <= 10),
    accordance_xp_resume_score_weight INTEGER NOT NULL DEFAULT 5 CHECK (accordance_xp_resume_score_weight >= 0 AND accordance_xp_resume_score_weight <= 10),
    accordance_skill_resume_score_weight INTEGER NOT NULL DEFAULT 5 CHECK (accordance_skill_resume_score_weight >= 0 AND accordance_skill_resume_score_weight <= 10),
    red_flag_score_weight INTEGER NOT NULL DEFAULT 5 CHECK (red_flag_score_weight >= 0 AND red_flag_score_weight <= 10),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

create_question_responses_table = """
CREATE TABLE IF NOT EXISTS question_responses(
    id SERIAL PRIMARY KEY,
    question_id INTEGER NOT NULL REFERENCES vacancy_questions(id) ON DELETE CASCADE,
    interview_id INTEGER NOT NULL REFERENCES interviews(id) ON DELETE CASCADE,
    
    response_time INTEGER NOT NULL,
    ask_text TEXT NOT NULL,
    ask_audio_fid TEXT NOT NULL,
    llm_comment TEXT NOT NULL DEFAULT '',
    score INTEGER NOT NULL DEFAULT 5 CHECK (score >= 0 AND score <= 10),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

drop_vacancy_table = """
DROP TABLE IF EXISTS vacancies;
"""
drop_vacancy_questions_table = """
DROP TABLE IF EXISTS vacancy_questions;
"""
drop_interviews_table = """
DROP TABLE IF EXISTS interviews;

"""
drop_interview_weights_table = """
DROP TABLE IF EXISTS interview_weights;
"""
drop_question_responses_table = """
DROP TABLE IF EXISTS question_responses;
"""

create_all_tables_queries = [
    create_vacancy_table,
    create_vacancy_questions_table,
    create_interviews_table,
    create_interview_weights_table,
    create_question_responses_table,
]


drop_all_tables_queries = [
    drop_question_responses_table,
    drop_interview_weights_table,
    drop_interviews_table,
    drop_vacancy_questions_table,
    drop_vacancy_table,
]