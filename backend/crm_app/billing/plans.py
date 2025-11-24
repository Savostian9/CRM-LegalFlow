# billing/plans.py
"""Константы лимитов тарифных планов и утилиты получения лимитов.
На старте реализован один коммерческий план STARTER.
Позже можно добавить FREE, PRO и т.п., а также динамическое чтение из Stripe metadata.
"""
from __future__ import annotations
from typing import Dict, Any

TRIAL_LIMITS: Dict[str, Any] = {
    'users': 1,
    'clients': 10,
    'cases': 10,
    'files': 500,
    'files_storage_mb': 1 * 1024,  # 1 GB
    'tasks_per_month': 20,
    'reminders_active': 20,
    'emails_per_month': 20,
}

STARTER_LIMITS: Dict[str, Any] = {
    'users': 5,
    'clients': 5,
    'cases': 5,
    'files': 5,          # количество файлов
    'files_storage_mb': 5,  # 5 MB
    'tasks_per_month': 5,
    'reminders_active': 5,
    'emails_per_month': 5,
}

PRO_LIMITS: Dict[str, Any] = {
    'users': 15,
    'clients': 1000000,
    'cases': 1000000,
    'files': 100000,
    'files_storage_mb': 30 * 1024,  # 30 GB
    'tasks_per_month': 1000000,
    'reminders_active': 10000,
    'emails_per_month': 15000,
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
