from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Entorno
    APP_ENV: str = "local"
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8090
    MCP_PATH: str = "/mcp"
    LOG_LEVEL: str = "INFO"

    # Oracle
    ORACLE_DSN: str = ""
    ORACLE_USER: str = ""
    ORACLE_PASSWORD: str = ""
    ORACLE_INSTANT_CLIENT_DIR: str = "/Users/fernandosalvo/Downloads/instantclient_23_26"

    # Pool de conexiones Oracle
    DB_POOL_MIN: int = 2
    DB_POOL_MAX: int = 5
    DB_POOL_INCREMENT: int = 1
    DB_POOL_TIMEOUT: int = 30

    # Autenticación: Bearer token por rol
    AUTH_TOKEN_CONTADOR: str = ""
    AUTH_TOKEN_ANALISTA_FINANCIERO: str = ""
    AUTH_TOKEN_GERENTE_FINANZAS: str = ""
    AUTH_TOKEN_AI_AGENT: str = ""

    @property
    def oracle_configured(self) -> bool:
        return bool(self.ORACLE_DSN and self.ORACLE_USER)

    @property
    def token_roles(self) -> dict[str, str]:
        tokens = {
            self.AUTH_TOKEN_CONTADOR: "contador",
            self.AUTH_TOKEN_ANALISTA_FINANCIERO: "analista_financiero",
            self.AUTH_TOKEN_GERENTE_FINANZAS: "gerente_finanzas",
            self.AUTH_TOKEN_AI_AGENT: "ai_agent",
        }
        return {token: role for token, role in tokens.items() if token}


settings = Settings()