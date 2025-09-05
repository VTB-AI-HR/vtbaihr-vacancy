create_vacancy_table = """
CREATE TABLE IF NOT EXISTS vacancies(
    id SERIAL PRIMARY KEY,

    name TEXT NOT NULL,
    tags TEXT[] NOT NULL,
    description TEXT NOT NULL,
    red_flags TEXT NOT NULL,
    skill_lvl TEXT NOT NULL,
    question_response_time INTEGER NOT NULL,
    questions_type TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

create_vacancy_questions_table = """
CREATE TABLE IF NOT EXISTS vacancy_questions(
    id SERIAL PRIMARY KEY,
    vacancy_id INTEGER NOT NULL REFERENCES vacancies(id) ON DELETE CASCADE,
    
    question TEXT NOT NULL,
    hint_for_evaluation TEXT NOT NULL,
    weight INTEGER NOT NULL,
    question_type TEXT NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

create_interview_weights_table = """
CREATE TABLE IF NOT EXISTS vacancy_criterion_weights(
    id SERIAL PRIMARY KEY,
    vacancy_id INTEGER NOT NULL REFERENCES vacancies(id) ON DELETE CASCADE,
    
    logic_structure_score_weight INTEGER NOT NULL,
    soft_skill_score_weight INTEGER NOT NULL,
    hard_skill_score_weight INTEGER NOT NULL,
    accordance_xp_vacancy_score_weight INTEGER NOT NULL,
    accordance_skill_vacancy_score_weight INTEGER NOT NULL,
    accordance_xp_resume_score_weight INTEGER NOT NULL,
    accordance_skill_resume_score_weight INTEGER NOT NULL,
    red_flag_score_weight INTEGER NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

create_interviews_table = """
CREATE TABLE IF NOT EXISTS interviews(
    id SERIAL PRIMARY KEY,
    vacancy_id INTEGER NOT NULL REFERENCES vacancies(id) ON DELETE CASCADE,
    
    candidate_email TEXT NOT NULL,
    candidate_resume_fid TEXT NOT NULL,
    
    general_score INTEGER DEFAULT 0,
    general_result TEXT DEFAULT '',
    general_recommendation TEXT DEFAULT '',
    red_flag_score INTEGER DEFAULT 0,
    hard_skill_score INTEGER DEFAULT 0, 
    soft_skill_score INTEGER DEFAULT 0,
    logic_structure_score INTEGER DEFAULT 0,
    accordance_xp_vacancy_score INTEGER DEFAULT 0,
    accordance_skill_vacancy_score INTEGER DEFAULT 0,
    accordance_xp_resume_score INTEGER DEFAULT 0,
    accordance_skill_resume_score INTEGER DEFAULT 0,
    strong_areas TEXT DEFAULT '',
    weak_areas TEXT DEFAULT '',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

create_question_responses_table = """
CREATE TABLE IF NOT EXISTS candidate_responses(
    id SERIAL PRIMARY KEY,
    question_id INTEGER NOT NULL REFERENCES vacancy_questions(id) ON DELETE CASCADE,
    interview_id INTEGER NOT NULL REFERENCES interviews(id) ON DELETE CASCADE,
    
    response_time INTEGER DEFAULT 0,
    message_ids TEXT[] DEFAULT '{}',
    llm_comment TEXT DEFAULT '',
    score INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

create_interview_chat_table = """
CREATE TABLE IF NOT EXISTS interview_messages(
    id SERIAL PRIMARY KEY,
    interview_id INTEGER NOT NULL REFERENCES interviews(id) ON DELETE CASCADE,
    question_id INTEGER NOT NULL REFERENCES vacancy_questions(id) ON DELETE CASCADE,
    
    audio_fid TEXT NOT NULL,
    role TEXT NOT NULL,
    text TEXT NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

drop_vacancy_table = """
DROP TABLE IF EXISTS vacancies;
"""

drop_vacancy_questions_table = """
DROP TABLE IF EXISTS vacancy_questions;
"""

drop_interview_weights_table = """
DROP TABLE IF EXISTS vacancy_criterion_weights;
"""

drop_interviews_table = """
DROP TABLE IF EXISTS interviews;
"""

drop_candidate_responses_table = """
DROP TABLE IF EXISTS candidate_responses;
"""

drop_question_responses_table = """
DROP TABLE IF EXISTS interview_messages;
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