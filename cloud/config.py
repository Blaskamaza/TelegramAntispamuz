"""
Alibaba Cloud Configuration
Free Tier лимиты оптимизированы для 2026
"""

import os
from dataclasses import dataclass

@dataclass
class AlibabaConfig:
    """Конфигурация Alibaba Cloud"""
    
    # === Credentials (из переменных окружения) ===
    ACCESS_KEY_ID: str = os.getenv("ALIBABA_ACCESS_KEY_ID", "")
    ACCESS_KEY_SECRET: str = os.getenv("ALIBABA_ACCESS_KEY_SECRET", "")
    REGION: str = os.getenv("ALIBABA_REGION", "ap-southeast-1")  # Сингапур (ближе к СНГ)
    
    # === Function Compute ===
    FC_SERVICE_NAME: str = "uz-ai-factory"
    FC_FUNCTION_NAME: str = "scout-agent"
    FC_MEMORY_MB: int = 128  # Минимум для экономии
    FC_TIMEOUT_SEC: int = 60
    FC_CRON: str = "0 0 */4 * * *"  # Каждые 4 часа
    
    # === Redis (ApsaraDB) ===
    REDIS_HOST: str = os.getenv("ALIBABA_REDIS_HOST", "")
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = os.getenv("ALIBABA_REDIS_PASSWORD", "")
    REDIS_DB: int = 0
    
    # === RDS PostgreSQL ===
    PG_HOST: str = os.getenv("ALIBABA_PG_HOST", "")
    PG_PORT: int = 5432
    PG_DATABASE: str = "uz_ai_factory"
    PG_USER: str = os.getenv("ALIBABA_PG_USER", "")
    PG_PASSWORD: str = os.getenv("ALIBABA_PG_PASSWORD", "")
    
    # === OSS ===
    OSS_BUCKET: str = "uz-ai-factory-static"
    OSS_ENDPOINT: str = f"oss-{REGION}.aliyuncs.com"
    
    # === CDN ===
    CDN_DOMAIN: str = "cdn.uz-ai-factory.com"
    
    # === ECS ===
    ECS_INSTANCE_TYPE: str = "ecs.t5-lc1m1.small"  # Free tier
    ECS_IMAGE_ID: str = "ubuntu_22_04_x64_20G_alibase_20240101.vhd"
    
    # === Gemini API ===
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = "gemini-1.5-flash"
    
    # === Free Tier Limits ===
    FC_FREE_REQUESTS: int = 1_000_000
    REDIS_FREE_MB: int = 256
    RDS_FREE_GB: int = 20
    OSS_FREE_GB: int = 5
    CDN_FREE_TB: int = 1
    PAI_FREE_GPU_HOURS: int = 50


config = AlibabaConfig()
