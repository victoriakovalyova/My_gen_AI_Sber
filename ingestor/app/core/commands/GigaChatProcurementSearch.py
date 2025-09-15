import logging
import os
import numpy as np
import pandas as pd
from fastapi import HTTPException
from app.core.registry import register_command
from app.db.clickhouse_client import ClickHouseManager
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import asyncio
from gigachat import GigaChat
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
import json

log = logging.getLogger(__name__)

# --- Модели для GigaChat команд ---
class GigaChatSearchArgs(BaseModel):
    scan_id: int
    query: str = Field(..., description="Поисковый запрос")
    top_k: int = Field(5, description="Количество возвращаемых результатов")

class GigaChatBatchSearchArgs(BaseModel):
    scan_id: int
    queries: List[str] = Field(..., description="Список поисковых запросов")
    top_k: int = Field(3, description="Количество возвращаемых результатов на запрос")

class GigaChatPrepareArgs(BaseModel):
    scan_id: int
    text_column: str = Field("content", description="Название колонки с текстом")

class GigaChatSearchResponse(BaseModel):
    scan_id: int
    query: str
    results: List[Dict[str, Any]]
    processing_time: float

class GigaChatBatchResponse(BaseModel):
    scan_id: int
    results: Dict[str, List[Dict[str, Any]]]
    processing_time: float

class GigaChatPrepareResponse(BaseModel):
    scan_id: int
    embeddings_count: int
    valid_documents: int
    message: str

# --- GigaChat сервис ---
class GigaChatService:
    def __init__(self):
        self.client_secret = ""
        if not self.client_secret:
            log.warning("GIGACHAT_TOKEN не установлен в переменных окружения")
        
        self.embeddings = None
        self.data_df = None
        self.valid_indices = []
        self.original_to_valid_index = {}
        self.valid_to_original_index = {}

    def get_embedding(self, text: str) -> np.ndarray:
        """Получение эмбеддинга через GigaChat"""
        try:
            if not self.client_secret:
                raise ValueError("GIGACHAT_TOKEN не настроен")
            
            truncated_text = text[:500]  # Обрезаем для избежания ошибок
            with GigaChat(credentials=self.client_secret, verify_ssl_certs=False) as giga:
                response = giga.embeddings(truncated_text)
                return np.array(response.data[0].embedding)
        except Exception as e:
            log.error(f"Ошибка получения эмбеддинга: {e}")
            return np.zeros(1024)

    async def prepare_embeddings_async(self, data: List[Dict], text_field: str = "content"):
        """Асинхронная подготовка эмбеддингов"""
        if not data:
            raise ValueError("Нет данных для обработки")
        
        log.info(f"Начинаем создание эмбеддингов для {len(data)} документов")
        
        self.data_df = pd.DataFrame(data)
        texts = self.data_df[text_field].astype(str).tolist()
        embeddings_list = []
        
        for i, text in enumerate(texts):
            if i % 10 == 0:
                log.info(f"Обработано {i}/{len(texts)} записей...")
            
            # Используем синхронный вызов в отдельном потоке
            embedding = await asyncio.get_event_loop().run_in_executor(
                None, self.get_embedding, text
            )
            embeddings_list.append(embedding)
            
            # Небольшая задержка для избежания rate limiting
            await asyncio.sleep(0.1)
        
        # Фильтруем валидные эмбеддинги
        valid_embeddings = []
        
        for i, emb in enumerate(embeddings_list):
            if isinstance(emb, np.ndarray) and emb.shape == (1024,) and not np.all(emb == 0):
                valid_embeddings.append(emb)
                self.valid_indices.append(i)
        
        if valid_embeddings:
            self.embeddings = np.array(valid_embeddings)
            self.embeddings = normalize(self.embeddings)
            
            # Создаем маппинги индексов
            for valid_idx, original_idx in enumerate(self.valid_indices):
                self.original_to_valid_index[original_idx] = valid_idx
                self.valid_to_original_index[valid_idx] = original_idx
            
            log.info(f"Создано {len(valid_embeddings)} валидных эмбеддингов")
        else:
            raise ValueError("Не удалось создать ни одного валидного эмбеддинга")

    def search_similar(self, query: str, top_k: int = 5) -> List[Dict]:
        """Поиск похожих документов"""
        if self.embeddings is None or len(self.embeddings) == 0:
            raise ValueError("Эмбеддинги не подготовлены")
        
        # Получаем эмбеддинг для запроса
        query_embedding = self.get_embedding(query)
        if np.all(query_embedding == 0):
            raise ValueError("Не удалось получить эмбеддинг для запроса")
        
        query_embedding = normalize(query_embedding.reshape(1, -1))
        
        # Вычисляем косинусное сходство
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # Получаем индексы top_k наиболее похожих
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        # Формируем результаты
        results = []
        for idx in top_indices:
            if idx in self.valid_to_original_index:
                original_idx = self.valid_to_original_index[idx]
                if original_idx < len(self.data_df):
                    result = {
                        **self.data_df.iloc[original_idx].to_dict(),
                        'similarity': float(similarities[idx])
                    }
                    results.append(result)
        
        return results

# --- Команды GigaChat ---
@register_command(
    command_name="gigachat_prepare_embeddings",
    args_model=GigaChatPrepareArgs,
    response_model=GigaChatPrepareResponse,
    description="Подготовка векторных представлений для документов scan_id"
)
async def gigachat_prepare_embeddings_command(scan_id: int, text_column: str = "content") -> dict:
    """Подготавливает эмбеддинги для документов указанного scan_id"""
    start_time = asyncio.get_event_loop().time()
    
    try:
        # Получаем данные из ClickHouse
        ch_manager = ClickHouseManager(config_path=None)
        raw_data = ch_manager.get_data_by_scan_id(scan_id)
        
        if not raw_data:
            raise HTTPException(status_code=404, detail=f"Данные не найдены для scan_id={scan_id}")

        # Подготавливаем данные
        documents = []
        for i, doc in enumerate(raw_data):
            documents.append({
                "id": i,
                "content": doc.content,
                "scan_id": scan_id,
                "document_index": i
            })

        # Инициализируем и подготавливаем эмбеддинги
        service = GigaChatService()
        await service.prepare_embeddings_async(documents, text_column)
        
        processing_time = asyncio.get_event_loop().time() - start_time
        
        return {
            "scan_id": scan_id,
            "embeddings_count": len(service.embeddings) if service.embeddings is not None else 0,
            "valid_documents": len(service.valid_indices),
            "message": f"Эмбеддинги подготовлены за {processing_time:.2f} секунд",
            "processing_time": processing_time
        }
        
    except Exception as e:
        log.error(f"Ошибка при подготовке эмбеддингов для scan_id={scan_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка подготовки эмбеддингов: {e}")

@register_command(
    command_name="gigachat_search",
    args_model=GigaChatSearchArgs,
    response_model=GigaChatSearchResponse,
    description="Семантический поиск по документам scan_id с использованием GigaChat"
)
async def gigachat_search_command(scan_id: int, query: str, top_k: int = 5) -> dict:
    """Выполняет семантический поиск по документам"""
    start_time = asyncio.get_event_loop().time()
    
    try:
        # Получаем данные из ClickHouse
        ch_manager = ClickHouseManager(config_path=None)
        raw_data = ch_manager.get_data_by_scan_id(scan_id)
        
        if not raw_data:
            raise HTTPException(status_code=404, detail=f"Данные не найдены для scan_id={scan_id}")

        # Подготавливаем данные
        documents = []
        for i, doc in enumerate(raw_data):
            documents.append({
                "id": i,
                "content": doc.content,
                "scan_id": scan_id,
                "document_index": i
            })

        # Инициализируем сервис и подготавливаем эмбеддинги
        service = GigaChatService()
        await service.prepare_embeddings_async(documents)
        
        # Выполняем поиск
        results = service.search_similar(query, top_k)
        
        processing_time = asyncio.get_event_loop().time() - start_time
        
        return {
            "scan_id": scan_id,
            "query": query,
            "results": results,
            "processing_time": processing_time
        }
        
    except Exception as e:
        log.error(f"Ошибка при поиске для scan_id={scan_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка поиска: {e}")

@register_command(
    command_name="gigachat_batch_search",
    args_model=GigaChatBatchSearchArgs,
    response_model=GigaChatBatchResponse,
    description="Пакетный семантический поиск по нескольким запросам"
)
async def gigachat_batch_search_command(scan_id: int, queries: List[str], top_k: int = 3) -> dict:
    """Выполняет пакетный поиск по нескольким запросам"""
    start_time = asyncio.get_event_loop().time()
    
    try:
        # Получаем данные из ClickHouse
        ch_manager = ClickHouseManager(config_path=None)
        raw_data = ch_manager.get_data_by_scan_id(scan_id)
        
        if not raw_data:
            raise HTTPException(status_code=404, detail=f"Данные не найдены для scan_id={scan_id}")

        # Подготавливаем данные
        documents = []
        for i, doc in enumerate(raw_data):
            documents.append({
                "id": i,
                "content": doc.content,
                "scan_id": scan_id,
                "document_index": i
            })

        # Инициализируем сервис и подготавливаем эмбеддинги
        service = GigaChatService()
        await service.prepare_embeddings_async(documents)
        
        # Выполняем поиск для каждого запроса
        all_results = {}
        for query in queries:
            try:
                results = service.search_similar(query, top_k)
                all_results[query] = results
            except Exception as e:
                log.error(f"Ошибка при поиске для запроса '{query}': {e}")
                all_results[query] = []
        
        processing_time = asyncio.get_event_loop().time() - start_time
        
        return {
            "scan_id": scan_id,
            "results": all_results,
            "processing_time": processing_time
        }
        
    except Exception as e:
        log.error(f"Ошибка при пакетном поиске для scan_id={scan_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка пакетного поиска: {e}")

@register_command(
    command_name="gigachat_similarity_check",
    args_model=GigaChatSearchArgs,
    response_model=GigaChatSearchResponse,
    description="Проверка схожести документов с эталонным запросом"
)
async def gigachat_similarity_check_command(scan_id: int, query: str, top_k: int = 5) -> dict:
    """Проверяет схожесть документов с эталонным запросом"""
    # Эта команда может использоваться для мониторинга качества документов
    return await gigachat_search_command(scan_id, query, top_k)

@register_command(
    command_name="gigachat_get_stats",
    args_model=GigaChatPrepareArgs,
    response_model=GigaChatPrepareResponse,
    description="Получение статистики по подготовленным эмбеддингам"
)
async def gigachat_get_stats_command(scan_id: int, text_column: str = "content") -> dict:
    """Возвращает статистику по эмбеддингам (подготавливает их если нужно)"""
    return await gigachat_prepare_embeddings_command(scan_id, text_column)

# --- Дополнительная команда для тестирования GigaChat ---
@register_command(
    command_name="gigachat_test_connection",
    args_model=GigaChatPrepareArgs,
    response_model=GigaChatPrepareResponse,
    description="Тестирование подключения к GigaChat API"
)
async def gigachat_test_connection_command(scan_id: int, text_column: str = "content") -> dict:
    """Тестирует подключение к GigaChat API"""
    try:
        service = GigaChatService()
        
        # Пробуем получить эмбеддинг для тестового запроса
        test_embedding = service.get_embedding("тестовый запрос")
        
        if np.all(test_embedding == 0):
            raise HTTPException(status_code=500, detail="Не удалось получить эмбеддинг")
        
        return {
            "scan_id": scan_id,
            "embeddings_count": 1,
            "valid_documents": 1,
            "message": "Подключение к GigaChat API успешно проверено",
            "processing_time": 0.0
        }
        
    except Exception as e:
        log.error(f"Ошибка тестирования подключения к GigaChat: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка подключения к GigaChat: {e}")