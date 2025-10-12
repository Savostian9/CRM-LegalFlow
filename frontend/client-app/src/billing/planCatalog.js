// Central catalog of plan metadata (display-oriented)
// NOTE: Keep numeric limits in sync with backend billing/plans.py

export const PLAN_CATALOG = {
  TRIAL: {
    code: 'TRIAL',
    name: 'Trial',
    periodLabel: '14 дней',
    price: 0,
    pricePeriod: 'период',
    highlight: false,
    badge: '14 дней',
    description: 'Пробный доступ ко всем основным функциям с ограниченными лимитами.',
    limits: {
      users: 3,
      clients: 100,
      cases: 50,
      files: 200,
      files_storage_mb: 2 * 1024,
      tasks_per_month: 100,
      reminders_active: 30,
      emails_per_month: 50,
    },
    features: [
      'Все основные функции для теста',
      'Быстрый старт без карты',
      'Ограничения по лимитам',
      'Переход на блокировку по окончании',
    ],
    qualitative: [
      { key: 'support', label: 'Поддержка', value: 'Email (стандартное время ответа)' },
      { key: 'export', label: 'Экспорт данных', value: 'Базовые CSV (ограниченно)' },
    ],
  },
  STARTER: {
    code: 'STARTER',
    name: 'Starter',
    price: 249,
    pricePeriod: 'месяц',
    badge: 'Рекомендуем',
    highlight: true,
    description: 'Расширенные лимиты и поддержка для растущей команды.',
    limits: {
      users: 3,
      clients: 300,
      cases: 300,
      files: 2000,
      files_storage_mb: 10 * 1024,
      tasks_per_month: 1000,
      reminders_active: 300,
      emails_per_month: 500,
    },
    features: [
      'Расширенные лимиты',
      'Приоритетные улучшения',
      'Email поддержка',
      'Базовые отчеты',
      'Роли доступа (admin/staff/viewer)',
    ],
    qualitative: [
      { key: 'support', label: 'Поддержка', value: 'Приоритет email' },
      { key: 'reports', label: 'Отчеты', value: 'Базовые' },
      { key: 'integrations', label: 'Интеграции', value: 'Календарь (бета)' },
    ],
  },
  PRO: {
    code: 'PRO',
    name: 'Pro',
    price: 549,
    pricePeriod: 'месяц',
    badge: 'Максимум',
    highlight: true,
    description: 'Максимальные лимиты, аналитика и расширенные интеграции.',
    limits: {
      users: 15,
      clients: 3000,
      cases: 3000,
      files: 10000,
      files_storage_mb: 50 * 1024,
      tasks_per_month: 10000,
      reminders_active: 2000,
      emails_per_month: 5000,
    },
    features: [
      'Большие лимиты (до 3000 клиентов)',
      'Приоритетная поддержка',
      'Расширенные отчеты и аналитика (roadmap)',
      'Custom fields (roadmap)',
      'Webhooks & интеграции (roadmap)',
      'Расширенный аудит действий',
    ],
    qualitative: [
      { key: 'support', label: 'Поддержка', value: 'Высокий приоритет' },
      { key: 'reports', label: 'Отчеты', value: 'Расширенные' },
      { key: 'integrations', label: 'Интеграции', value: 'Webhooks / Slack (roadmap)' },
      { key: 'audit', label: 'Аудит', value: 'Полный журнал' },
    ],
  },
};

export const ORDERED_PLAN_CODES = ['TRIAL', 'STARTER', 'PRO'];

export function formatStorage(mb) {
  if (mb >= 1024) return (mb / 1024) + ' GB';
  return mb + ' MB';
}

export function getPlanCatalogArray() {
  return ORDERED_PLAN_CODES.map(code => PLAN_CATALOG[code]);
}
