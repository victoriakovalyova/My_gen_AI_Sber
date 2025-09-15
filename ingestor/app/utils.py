import logging
import os
import yaml
from logging.handlers import RotatingFileHandler


def setup_logging(
    log_dir="logs",
    log_file="app.log",
    console_level=logging.INFO,
    file_level=logging.INFO,
    max_bytes=10_000_000,
    backup_count=5,
):
    """Настраивает централизованное логирование."""
    log = logging.getLogger()
    log.setLevel(logging.INFO)

    if log.hasHandlers():
        log.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    log.addHandler(console_handler)

    os.makedirs(log_dir, exist_ok=True)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, log_file),
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setLevel(file_level)
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)


"""
пока load_config не нужен я так понимаю
"""


def load_config(config_file: str = "config.yaml") -> dict:
    """
    Загружает конфигурацию из YAML или .env.
    """
    default_config = {
        "clickhouse": {
            "host": os.environ.get("CLICKHOUSE_HOST", "188.187.63.111"),
            "port": int(os.environ.get("CLICKHOUSE_PORT", 9049)),
            "username": os.environ.get("CLICKHOUSE_USERNAME", " "),
            "password": os.environ.get("CLICKHOUSE_PASSWORD", " "),
            "database": os.environ.get("CLICKHOUSE_DATABASE", " "),
            "connect_timeout": 10,
            "send_receive_timeout": 30,
        }
    }

    try:
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                config = yaml.safe_load(f)
            logging.info(f"Конфигурация успешно загружена из файла {config_file}")
            return {**default_config, **config}
        else:
            logging.info(
                f"Файл конфигурации {config_file} не найден, используется конфигурация по умолчанию"
            )
        return default_config
    except Exception as e:
        logging.warning(
            f"Не удалось загрузить файл конфигурации {config_file}: {str(e)}"
        )
        return default_config
