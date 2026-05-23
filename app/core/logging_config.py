"""
Logging estruturado — qualidade e rastreabilidade em produção.
Configurado uma vez no startup da aplicação (lifespan do FastAPI).
"""
import logging
import sys
from app.core.config import settings


def setup_logging() -> None:
    """
    Configura o logger raiz da aplicação.
    Em produção (ENVIRONMENT != development) usa formato JSON-like para facilitar
    ingestão em ferramentas como Datadog, CloudWatch ou Loki.
    """
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    if settings.ENVIRONMENT == "development":
        fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        datefmt = "%H:%M:%S"
    else:
        # Formato estruturado para produção
        fmt = '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","msg":"%(message)s"}'
        datefmt = "%Y-%m-%dT%H:%M:%S"

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)

    # Silencia loggers muito verbosos de libs externas
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    logging.getLogger(__name__).info(
        "Logging configured: level=%s env=%s", settings.LOG_LEVEL, settings.ENVIRONMENT
    )
