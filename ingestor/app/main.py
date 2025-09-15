from app.utils import setup_logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.router import router
import logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    log = logging.getLogger(__name__)
    logging.info("Запуск приложения")
    yield
    log.info("Завершение работы")


app = FastAPI(lifespan=lifespan)
app.include_router(router)


# import logging
# from utils import setup_logging
# from cli import run_cli

# def main():
#     setup_logging()
#     logger = logging.getLogger(__name__)
#     logger.info('Запуск приложения')
#     run_cli()

# if __name__ == "__main__":
#     main()
