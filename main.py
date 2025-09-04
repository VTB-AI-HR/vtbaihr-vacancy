import uvicorn

from infrastructure.pg.pg import PG
from infrastructure.weedfs.weedfs import Weed
from infrastructure.telemetry.telemetry import Telemetry, AlertManager

from pkg.client.external.openai.client import GPTClient

from internal.controller.http.middlerware.middleware import HttpMiddleware

from internal.controller.http.handler.vacancy.handler import VacancyController
from internal.controller.http.handler.interview.handler import InterviewController

from internal.service.vacancy.service import VacancyService
from internal.service.interview.service import InterviewService
from internal.service.interview.prompt import InterviewPromptGenerator

from internal.repo.vacancy.repo import VacancyRepo
from internal.repo.interview.repo import InterviewRepo

from internal.app.http.app import NewHTTP

from internal.config.config import Config

cfg = Config()

alert_manager = AlertManager(
    cfg.alert_tg_bot_token,
    cfg.service_name,
    cfg.alert_tg_chat_id,
    cfg.alert_tg_chat_thread_id,
    cfg.grafana_url,
    cfg.monitoring_redis_host,
    cfg.monitoring_redis_port,
    cfg.monitoring_redis_db,
    cfg.monitoring_redis_password
)

tel = Telemetry(
    cfg.log_level,
    cfg.root_path,
    cfg.environment,
    cfg.service_name,
    cfg.service_version,
    cfg.otlp_host,
    cfg.otlp_port,
    alert_manager
)

# Инициализация клиентов
db = PG(tel, cfg.db_user, cfg.db_pass, cfg.db_host, cfg.db_port, cfg.db_name)
storage = Weed(cfg.weed_master_host, cfg.weed_master_port)
llm_client = GPTClient(tel, cfg.openai_api_key)

# Инициализация репозиториев
vacancy_repo = VacancyRepo(tel, db)
interview_repo = InterviewRepo(tel, db)

# Инициализация сервисов
interview_prompt_generator = InterviewPromptGenerator(tel)
vacancy_service = VacancyService(vacancy_repo)
interview_service = InterviewService(
    vacancy_repo,
    interview_repo,
    interview_prompt_generator,
    llm_client,
    storage
)

# Инициализация контроллеров
vacancy_controller = VacancyController(tel, interview_service)
interview_controller = InterviewController(tel, interview_service)

# Инициализация middleware
http_middleware = HttpMiddleware(tel, cfg.prefix)

if __name__ == "__main__":
    app = NewHTTP(
        db,
        vacancy_controller,
        interview_controller,
        http_middleware,
        cfg.prefix,
    )
    uvicorn.run(app, host="0.0.0.0", port=int(cfg.http_port), access_log=False)