# billing/plans.py
"""Константы лимитов тарифных планов и утилиты получения лимитов.
На старте реализован один коммерческий план STARTER.
Позже можно добавить FREE, PRO и т.п., а также динамическое чтение из Stripe metadata.
"""
from __future__ import annotations
from typing import Dict, Any

TRIAL_LIMITS: Dict[str, Any] = {
    'users': 3,
    'clients': 100,
    'cases': 50,
    'files': 200,
    'files_storage_mb': 2 * 1024,  # 2 GB
    'tasks_per_month': 100,
    'reminders_active': 30,
    'emails_per_month': 50,
}

STARTER_LIMITS: Dict[str, Any] = {
    'users': 3,
    'clients': 300,
    'cases': 300,
    'files': 2000,          # количество файлов
    'files_storage_mb': 10 * 1024,  # 10 GB в мегабайтах
    'tasks_per_month': 1000,
    'reminders_active': 300,
    'emails_per_month': 500,
}

PRO_LIMITS: Dict[str, Any] = {
    'users': 15,
    'clients': 3000,
    'cases': 3000,
    'files': 10000,
    'files_storage_mb': 50 * 1024,  # 50 GB
    'tasks_per_month': 10000,
    'reminders_active': 2000,
    'emails_per_month': 5000,
}

PLAN_LIMITS: Dict[str, Dict[str, Any]] = {
    'TRIAL': TRIAL_LIMITS,
    'STARTER': STARTER_LIMITS,
    'PRO': PRO_LIMITS,
}

def get_plan_limits(plan_code: str) -> Dict[str, Any]:
    return PLAN_LIMITS.get(plan_code.upper(), STARTER_LIMITS)


def format_usage(limits: Dict[str, Any], usage: Dict[str, int]) -> Dict[str, Any]:
    formatted = {}
    for key, limit in limits.items():
        current = usage.get(key, 0)
        percent = None
        if isinstance(limit, (int, float)) and limit > 0:
            percent = round((current / limit) * 100, 2) if current <= limit else 100.0
        formatted[key] = {
            'current': current,
            'limit': limit,
            'percent': percent
        }
    return formatted
