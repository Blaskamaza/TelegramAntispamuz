"""
Database Client — PostgreSQL Integration
Подключение к Alibaba RDS PostgreSQL
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, List, Any
from contextlib import contextmanager

# PostgreSQL driver
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor, Json
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("database")


class DatabaseClient:
    """
    PostgreSQL клиент для Alibaba RDS.
    Free Tier: 20GB, 12 месяцев.
    """
    
    def __init__(
        self,
        host: str = None,
        port: int = 5432,
        database: str = "uz_ai_factory",
        user: str = None,
        password: str = None
    ):
        self.config = {
            "host": host or os.getenv("ALIBABA_PG_HOST", ""),
            "port": port,
            "database": database,
            "user": user or os.getenv("ALIBABA_PG_USER", ""),
            "password": password or os.getenv("ALIBABA_PG_PASSWORD", ""),
        }
        self.connection = None
    
    @contextmanager
    def get_cursor(self, dict_cursor: bool = True):
        """Context manager для курсора"""
        if not PSYCOPG2_AVAILABLE:
            raise ImportError("psycopg2 not installed")
        
        conn = psycopg2.connect(**self.config)
        cursor_factory = RealDictCursor if dict_cursor else None
        cursor = conn.cursor(cursor_factory=cursor_factory)
        
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    # ============================================================
    # MARKET PAINS
    # ============================================================
    
    def add_pain(self, pain: Dict[str, Any]) -> str:
        """Добавляет новую боль в базу"""
        with self.get_cursor() as cur:
            cur.execute("""
                INSERT INTO market_pains (
                    title, description, category, frequency, 
                    pain_score, monetization_potential,
                    sources, keywords, examples, business_idea,
                    estimated_price_min, estimated_price_max
                ) VALUES (
                    %(title)s, %(description)s, %(category)s, %(frequency)s,
                    %(pain_score)s, %(monetization_potential)s,
                    %(sources)s, %(keywords)s, %(examples)s, %(business_idea)s,
                    %(estimated_price_min)s, %(estimated_price_max)s
                )
                ON CONFLICT DO NOTHING
                RETURNING id
            """, {
                "title": pain.get("title"),
                "description": pain.get("description"),
                "category": pain.get("category", "other"),
                "frequency": pain.get("frequency", 1),
                "pain_score": pain.get("pain_score"),
                "monetization_potential": pain.get("monetization_potential"),
                "sources": Json(pain.get("sources", [])),
                "keywords": pain.get("keywords", []),
                "examples": pain.get("examples", []),
                "business_idea": pain.get("business_idea"),
                "estimated_price_min": pain.get("estimated_price_min"),
                "estimated_price_max": pain.get("estimated_price_max"),
            })
            result = cur.fetchone()
            return result["id"] if result else None
    
    def get_top_pains(self, limit: int = 10) -> List[Dict]:
        """Получает топ болей по композитному скору"""
        with self.get_cursor() as cur:
            cur.execute("""
                SELECT * FROM v_top_pains LIMIT %s
            """, (limit,))
            return cur.fetchall()
    
    def update_pain_status(self, pain_id: str, status: str):
        """Обновляет статус боли"""
        with self.get_cursor() as cur:
            cur.execute("""
                UPDATE market_pains 
                SET status = %s, last_seen_at = NOW()
                WHERE id = %s
            """, (status, pain_id))
    
    # ============================================================
    # PROJECTS
    # ============================================================
    
    def create_project(self, project: Dict[str, Any]) -> str:
        """Создает новый проект"""
        with self.get_cursor() as cur:
            cur.execute("""
                INSERT INTO projects (
                    name, description, status, pain_id,
                    tech_stack, estimated_revenue
                ) VALUES (
                    %(name)s, %(description)s, %(status)s, %(pain_id)s,
                    %(tech_stack)s, %(estimated_revenue)s
                )
                RETURNING id
            """, {
                "name": project.get("name"),
                "description": project.get("description"),
                "status": project.get("status", "idea"),
                "pain_id": project.get("pain_id"),
                "tech_stack": Json(project.get("tech_stack", [])),
                "estimated_revenue": project.get("estimated_revenue", 0),
            })
            return cur.fetchone()["id"]
    
    def update_project_status(self, project_id: str, status: str, xp_earned: int = 0):
        """Обновляет статус проекта"""
        with self.get_cursor() as cur:
            cur.execute("""
                UPDATE projects 
                SET status = %s, xp_earned = xp_earned + %s
                WHERE id = %s
            """, (status, xp_earned, project_id))
    
    def get_projects_by_status(self, status: str) -> List[Dict]:
        """Получает проекты по статусу"""
        with self.get_cursor() as cur:
            cur.execute("""
                SELECT * FROM projects WHERE status = %s ORDER BY created_at DESC
            """, (status,))
            return cur.fetchall()
    
    # ============================================================
    # AGENT LOGS
    # ============================================================
    
    def log_agent_action(
        self,
        agent_type: str,
        action: str,
        status: str = "started",
        input_data: Dict = None,
        output_data: Dict = None,
        project_id: str = None,
        pain_id: str = None,
        duration_ms: int = None,
        tokens_used: int = None,
        error_message: str = None
    ) -> str:
        """Записывает действие агента в лог"""
        with self.get_cursor() as cur:
            cur.execute("""
                INSERT INTO agent_logs (
                    agent_type, action, status,
                    input_data, output_data, error_message,
                    project_id, pain_id,
                    duration_ms, tokens_used,
                    completed_at
                ) VALUES (
                    %(agent_type)s, %(action)s, %(status)s,
                    %(input_data)s, %(output_data)s, %(error_message)s,
                    %(project_id)s, %(pain_id)s,
                    %(duration_ms)s, %(tokens_used)s,
                    %(completed_at)s
                )
                RETURNING id
            """, {
                "agent_type": agent_type,
                "action": action,
                "status": status,
                "input_data": Json(input_data) if input_data else None,
                "output_data": Json(output_data) if output_data else None,
                "error_message": error_message,
                "project_id": project_id,
                "pain_id": pain_id,
                "duration_ms": duration_ms,
                "tokens_used": tokens_used,
                "completed_at": datetime.now() if status in ["completed", "failed"] else None,
            })
            return cur.fetchone()["id"]
    
    def get_agent_stats(self, days: int = 7) -> List[Dict]:
        """Получает статистику агентов за последние N дней"""
        with self.get_cursor() as cur:
            cur.execute("""
                SELECT * FROM v_agent_stats 
                WHERE date >= CURRENT_DATE - INTERVAL '%s days'
                ORDER BY date DESC, agent_type
            """, (days,))
            return cur.fetchall()
    
    # ============================================================
    # FINANCIAL METRICS
    # ============================================================
    
    def add_financial_metric(self, metric: Dict[str, Any]):
        """Добавляет финансовую метрику"""
        with self.get_cursor() as cur:
            cur.execute("""
                INSERT INTO financial_metrics (
                    project_id, period_start, period_end, period_type,
                    revenue, transactions_count, active_users, new_users,
                    cloud_cost, ai_tokens_cost, marketing_cost,
                    mrr, churn_rate, cac, ltv
                ) VALUES (
                    %(project_id)s, %(period_start)s, %(period_end)s, %(period_type)s,
                    %(revenue)s, %(transactions_count)s, %(active_users)s, %(new_users)s,
                    %(cloud_cost)s, %(ai_tokens_cost)s, %(marketing_cost)s,
                    %(mrr)s, %(churn_rate)s, %(cac)s, %(ltv)s
                )
                ON CONFLICT (project_id, period_start, period_end) 
                DO UPDATE SET
                    revenue = EXCLUDED.revenue,
                    transactions_count = EXCLUDED.transactions_count,
                    active_users = EXCLUDED.active_users
            """, metric)
    
    def get_financial_dashboard(self) -> List[Dict]:
        """Получает финансовый дашборд"""
        with self.get_cursor() as cur:
            cur.execute("SELECT * FROM v_financial_dashboard ORDER BY total_revenue DESC")
            return cur.fetchall()


# Singleton instance
db = DatabaseClient()
