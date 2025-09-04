import os


class Config:
    def __init__(self):
        # Service configuration
        self.service_name = os.getenv("VTBAIHR_VACANCY_CONTAINER_NAME", "vtbaihr-vacancy")
        self.environment = os.getenv("ENVIRONMENT", "dev")
        self.service_version = os.getenv("VTBAIHR_VACANCY_SERVICE_VERSION", "1.0.0")
        self.log_level = os.getenv("VTBAIHR_LOG_LEVEL", "INFO")
        self.root_path = os.getenv("VTBAIHR_ROOT_PATH", "/")

        # HTTP server configuration
        self.http_port = os.getenv("VTBAIHR_VACANCY_PORT", "8000")
        self.prefix = os.getenv("VTBAIHR_VACANCY_PREFIX", "/api/vacancy")

        # PostgreSQL configuration
        self.db_host = os.getenv("VTBAIHR_VACANCY_POSTGRES_HOST", "localhost")
        self.db_port = os.getenv("VTBAIHR_VACANCY_POSTGRES_PORT", "10001")
        self.db_user = os.getenv("VTBAIHR_VACANCY_POSTGRES_USER", "vacancy-user")
        self.db_pass = os.getenv("VTBAIHR_VACANCY_POSTGRES_PASSWORD", "password")
        self.db_name = os.getenv("VTBAIHR_VACANCY_POSTGRES_DB_NAME", "vacancy")

        # Redis configuration for monitoring
        self.monitoring_redis_host = os.getenv("VTBAIHR_MONITORING_REDIS_HOST", "localhost")
        self.monitoring_redis_port = int(os.getenv("VTBAIHR_MONITORING_REDIS_PORT", "16000"))
        self.monitoring_redis_password = os.getenv("VTBAIHR_MONITORING_REDIS_PASSWORD", "")
        self.monitoring_redis_db = int(os.getenv("VTBAIHR_MONITORING_DEDUPLICATE_ERROR_ALERT_REDIS_DB", "1"))

        # WeedFS configuration
        self.weed_master_host = os.getenv("VTBAIHR_WEED_MASTER_HOST", "localhost")
        self.weed_master_port = int(os.getenv("VTBAIHR_WEED_MASTER_PORT", "9333"))

        # OpenTelemetry configuration
        self.otlp_host = os.getenv("VTBAIHR_OTEL_COLLECTOR_HOST", "localhost")
        self.otlp_port = int(os.getenv("VTBAIHR_OTEL_COLLECTOR_GRPC_PORT", "4317"))

        # Alert manager configuration (Telegram bot)
        self.alert_tg_bot_token = os.getenv("VTBAIHR_ALERT_TG_BOT_TOKEN", "")
        self.alert_tg_chat_id = int(os.getenv("VTBAIHR_ALERT_TG_CHAT_ID", "0"))
        self.alert_tg_chat_thread_id = int(os.getenv("VTBAIHR_ALERT_TG_CHAT_THREAD_ID", "0"))
        self.grafana_url = os.getenv("VTBAIHR_GRAFANA_URL", "http://localhost:3001")

        # OpenAI configuration
        self.openai_api_key = os.getenv("VTBAIHR_OPENAI_API_KEY", "")