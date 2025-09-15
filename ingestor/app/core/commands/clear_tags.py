import logging
import os
import time
from pathlib import Path
from fastapi import HTTPException
from app.core.registry import register_command
from app.db.clickhouse_client import ClickHouseManager
from app.parser import clean_html_content, extract_urls_and_files
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import asyncio
import aiohttp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

log = logging.getLogger(__name__)

# --- Модели для команд ---
class ScanArgs(BaseModel):
    scan_id: int

class DownloadContractsArgs(BaseModel):
    limit: int = Field(5, description="Количество контрактов для обработки")
    headless: bool = Field(True, description="Запуск браузера в фоновом режиме")

class DownloadCSVArgs(BaseModel):
    batch_index: int = Field(0, description="Индекс батча для выгрузки (0-based)")
    headless: bool = Field(True, description="Запуск браузера в фоновом режиме")

class ScanResponse(BaseModel):
    scan_id: int
    result: list
    message: str = ""

class DownloadResponse(BaseModel):
    success: bool
    downloaded_files: List[str]
    message: str = ""

# --- Вспомогательные функции для Selenium ---
def create_driver(headless: bool = True, download_dir: Optional[Path] = None):
    """Создает и настраивает Chrome WebDriver"""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    if download_dir:
        prefs = {
            "download.default_directory": str(download_dir.resolve()),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    return driver

def set_download_folder(driver, path: Path):
    """Динамически меняет папку загрузки для Chrome"""
    driver.execute_cdp_cmd(
        "Page.setDownloadBehavior",
        {
            "behavior": "allow",
            "downloadPath": str(path.resolve())
        }
    )
    log.info(f"Папка загрузки изменена на: {path}")

def wait_for_file(folder: Path, extension: str = ".csv", timeout: int = 60):
    """Ждёт появления файла с указанным расширением"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        files = list(folder.glob(f"*{extension}"))
        if files:
            return files[0]
        time.sleep(1)
    return None

# --- Команды ---
@register_command(
    command_name="clear_tags",
    args_model=ScanArgs,
    response_model=ScanResponse,
    description="Очистка тегов в HTML по scan_id"
)
async def clear_tags_command(scan_id: int) -> dict:
    """Чистит HTML документ от тегов"""
    ch_manager = ClickHouseManager(config_path=None)

    try:
        raw_data = ch_manager.get_data_by_scan_id(scan_id)
        if not raw_data:
            log.warning(f"Данные не найдены для scan_id={scan_id}")
            raise HTTPException(status_code=404, detail=f"Данные не найдены для scan_id={scan_id}")

        list_contents = [doc.content for doc in raw_data]

        # Создаем директорию для результатов
        name_dir = f"data/{scan_id}"
        os.makedirs(name_dir, exist_ok=True)

        # Сохраняем оригинальные файлы
        for i, doc in enumerate(raw_data):
            file_path = os.path.join(name_dir, f"{scan_id}_main_{i}.html")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(doc.content)

        # Очищаем HTML контент
        parsed_result = clean_html_content(list_contents)

        # Сохраняем очищенные файлы
        for i, result in enumerate(parsed_result):
            file_path = os.path.join(name_dir, f"{scan_id}_result_{i}.html")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(result)

        output = {
            "scan_id": scan_id,
            "result": parsed_result,
            "message": f"Обработка завершена для scan_id={scan_id}. Обработано {len(parsed_result)} документов."
        }

        log.info(f"Обработка завершена для scan_id={scan_id}.")
        return output

    except Exception as e:
        log.error(f"Ошибка при обработке scan_id={scan_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Произошла ошибка: {e}")

@register_command(
    command_name="download_contracts",
    args_model=DownloadContractsArgs,
    response_model=DownloadResponse,
    description="Скачивание документов контрактов с zakupki.gov.ru"
)
async def download_contracts_command(limit: int = 5, headless: bool = True) -> dict:
    """Скачивает документы контрактов с портала закупок"""
    BASE_URL = "https://zakupki.gov.ru/epz/contract/search/results.html#"
    ROOT_DIR = Path("contracts_docs")
    ROOT_DIR.mkdir(exist_ok=True)

    downloaded_files = []

    try:
        # Создаем драйвер
        driver = create_driver(headless=headless)
        wait = WebDriverWait(driver, 30)

        log.info("Загружаем страницу поиска контрактов...")
        driver.get(BASE_URL)

        # Нажимаем кнопку выгрузки CSV
        try:
            download_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.downLoad-search")))
            driver.execute_script("arguments[0].click();", download_btn)
            log.info("Кнопка выгрузки CSV нажата")
            time.sleep(5)
        except Exception as e:
            log.warning(f"Не удалось нажать кнопку выгрузки CSV: {e}")

        # Находим ссылки на контракты
        try:
            elems = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='/epz/rdik/card/info.html']"))
            )
        except Exception as e:
            log.error(f"Не удалось найти ссылки на контракты: {e}")
            driver.quit()
            raise HTTPException(status_code=500, detail=f"Не удалось найти контракты: {e}")

        contract_links = list({el.get_attribute("href") for el in elems if el.get_attribute("href")})
        log.info(f"Найдено контрактов: {len(contract_links)}")
        contract_links = contract_links[:limit]

        # Обрабатываем контракты
        for idx, url in enumerate(contract_links, 1):
            log.info(f"[{idx}] Открываем контракт: {url}")
            driver.get(url)

            # Создаем папку для контракта
            contract_number = url.split("contractRegNum=")[-1]
            contract_dir = ROOT_DIR / contract_number
            contract_dir.mkdir(exist_ok=True)
            log.info(f"Создана папка: {contract_dir}")

            # Устанавливаем папку загрузки
            set_download_folder(driver, contract_dir)

            # Ищем документы для скачивания
            try:
                zip_links = WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='filestore/public/1.0/download/rdik/file.html']"))
                )
                log.info(f"Найдено документов: {len(zip_links)}")
            except Exception:
                log.warning("Документы не найдены для контракта")
                continue

            # Скачиваем файлы
            for i, el in enumerate(zip_links, 1):
                name = el.text.strip() or f"doc_{i}.zip"
                log.info(f"Скачиваем {i}/{len(zip_links)}: {name}")
                try:
                    driver.execute_script("arguments[0].click();", el)
                    time.sleep(2)
                except Exception as e:
                    log.error(f"Ошибка скачивания {name}: {e}")

            # Ждём завершения загрузки
            while any(f.suffix == ".crdownload" for f in contract_dir.iterdir()):
                log.info("Ждём завершения загрузки...")
                time.sleep(1)

            # Добавляем скачанные файлы в результат
            contract_files = [str(f) for f in contract_dir.iterdir() if f.is_file()]
            downloaded_files.extend(contract_files)
            log.info(f"Контракт {contract_number} обработан. Файлов: {len(contract_files)}")

        driver.quit()
        log.info("Все контракты обработаны!")

        return {
            "success": True,
            "downloaded_files": downloaded_files,
            "message": f"Успешно скачано {len(downloaded_files)} файлов из {len(contract_links)} контрактов"
        }

    except Exception as e:
        log.error(f"Ошибка при скачивании контрактов: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка скачивания контрактов: {e}")

@register_command(
    command_name="download_csv",
    args_model=DownloadCSVArgs,
    response_model=DownloadResponse,
    description="Выгрузка CSV файлов с результатами поиска контрактов"
)
async def download_csv_command(batch_index: int = 0, headless: bool = True) -> dict:
    """Выгружает CSV файлы с результатами поиска контрактов"""
    CSV_DIR = Path("contracts_csv")
    CSV_DIR.mkdir(exist_ok=True)

    try:
        # Создаем драйвер с указанием папки для загрузки
        driver = create_driver(headless=headless, download_dir=CSV_DIR)
        wait = WebDriverWait(driver, 20)

        log.info("Открываю страницу поиска контрактов...")
        driver.get("https://zakupki.gov.ru/epz/contract/search/results.html#")

        # Нажимаем кнопку "Выгрузить результаты поиска"
        try:
            download_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.downLoad-search")))
            driver.execute_script("arguments[0].click();", download_btn)
            log.info("Нажата кнопка 'Выгрузить результаты поиска'")
        except Exception as e:
            driver.quit()
            raise HTTPException(status_code=500, detail=f"Не удалось найти кнопку выгрузки: {e}")

        # Выбираем элемент из списка батчей
        try:
            items = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.csvDownload")))
            log.info(f"Найдено {len(items)} вариантов выгрузки")
            
            if batch_index >= len(items):
                driver.quit()
                raise HTTPException(status_code=400, detail=f"Индекс {batch_index} превышает количество доступных вариантов ({len(items)})")

            item = items[batch_index]
            driver.execute_script("arguments[0].click();", item)
            log.info(f"Нажата кнопка выгрузки #{batch_index + 1}")
        except Exception as e:
            driver.quit()
            raise HTTPException(status_code=500, detail=f"Ошибка при выборе варианта выгрузки: {e}")

        # Ждем завершения загрузки
        downloaded_file = wait_for_file(CSV_DIR, ".csv", timeout=120)
        
        if downloaded_file:
            log.info(f"Файл успешно скачан: {downloaded_file}")
            driver.quit()
            
            return {
                "success": True,
                "downloaded_files": [str(downloaded_file)],
                "message": f"CSV файл успешно скачан: {downloaded_file.name}"
            }
        else:
            driver.quit()
            raise HTTPException(status_code=500, detail="Не удалось дождаться загрузки CSV файла")

    except Exception as e:
        log.error(f"Ошибка при выгрузке CSV: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка выгрузки CSV: {e}")

@register_command(
    command_name="process_contracts_batch",
    args_model=DownloadContractsArgs,
    response_model=DownloadResponse,
    description="Пакетная обработка контрактов (скачивание документов)"
)
async def process_contracts_batch_command(limit: int = 5, headless: bool = True) -> dict:
    """Пакетная обработка контрактов - объединяет несколько операций"""
    # Здесь можно добавить комплексную обработку,
    # например: скачать CSV -> проанализировать -> скачать документы контрактов
    return await download_contracts_command(limit, headless)

# Дополнительные команды могут быть добавлены здесь
@register_command(
    command_name="list_downloaded_files",
    args_model=ScanArgs,
    response_model=DownloadResponse,
    description="Показать список скачанных файлов"
)
async def list_downloaded_files_command(scan_id: int) -> dict:
    """Показывает список скачанных файлов для указанного scan_id"""
    try:
        scan_dir = Path(f"data/{scan_id}")
        contracts_dir = Path("contracts_docs")
        csv_dir = Path("contracts_csv")
        
        all_files = []
        
        # Собираем файлы из всех директорий
        if scan_dir.exists():
            all_files.extend([str(f) for f in scan_dir.rglob("*") if f.is_file()])
        
        if contracts_dir.exists():
            all_files.extend([str(f) for f in contracts_dir.rglob("*") if f.is_file()])
        
        if csv_dir.exists():
            all_files.extend([str(f) for f in csv_dir.rglob("*") if f.is_file()])
        
        return {
            "success": True,
            "downloaded_files": all_files,
            "message": f"Найдено {len(all_files)} файлов"
        }
        
    except Exception as e:
        log.error(f"Ошибка при получении списка файлов: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения списка файлов: {e}")