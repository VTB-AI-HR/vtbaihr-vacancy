from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface, model


class VacancyPromptGenerator(interface.IVacancyPromptGenerator):
    def __init__(
            self,
            tel: interface.ITelemetry
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()

    def get_question_generation_prompt(
            self,
            vacancy: model.Vacancy,
            count_questions: int,
            questions_type: model.QuestionsType,
    ) -> str:
        return f"""Ты эксперт по созданию вопросов для технических интервью.

ИНФОРМАЦИЯ О ВАКАНСИИ:
Название: {vacancy.name}
Описание: {vacancy.description}
Уровень: {vacancy.skill_lvl.value}
Теги/навыки: {', '.join(vacancy.tags)}

ЗАДАЧА: Сгенерируй вопросы для интервью соответствующего типа и уровня сложности.

ТРЕБОВАНИЯ К ГЕНЕРАЦИИ:
- Количество вопросов: {count_questions}
- Тип вопросов: {questions_type.value}
- Все вопросы должны соответствовать уровню {vacancy.skill_lvl.value}

ФОРМАТ ОТВЕТА:
{{
  "questions": [
    {{
      "question": "Текст вопроса",
      "question_type": "{questions_type.value}",
      "hint_for_evaluation": "Подсказка для оценки ответа",
      "weight": число от 1 до 10
    }}
  ]
}}

ВАЖНО: Отвечай ТОЛЬКО валидным JSON без markdown разметки.
"""
