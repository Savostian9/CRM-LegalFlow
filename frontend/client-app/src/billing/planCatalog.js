// Central catalog of plan metadata (display-oriented)
// NOTE: Keep numeric limits in sync with backend billing/plans.py

export const PLAN_CATALOG = {
  TRIAL: {
    code: 'TRIAL',
    name: 'Trial',
    periodLabel: '14 дней',
    price: 0,
    priceYearly: 0,
    pricePeriod: 'период',
    highlight: false,
    badge: '14 дней',
    description: 'Пробный доступ ко всем основным функциям с ограниченными лимитами.',
    limits: {
      users: 1,
      clients: 10,
      cases: 10,
      files: 500,
      files_storage_mb: 1 * 1024,
      tasks_per_month: 20,
      reminders_active: 20,
      emails_per_month: 20,
    },
    features: [
      'До 10 клиентов; базовые возможности',
      'До 50 файлов на клиента (до 1 ГБ)',
      '1 сотрудник: администратор, доступ ко всем разделам',
      'До 20 задач; базовый календарь',
      'Авто email-уведомления: до 20 сообщений',
      'Финансы для 10 клиентов: сумма оплат и список должников',
      'Техподдержка стандартная',
    ],
    qualitative: [],
  },
  STARTER: {
    code: 'STARTER',
    name: 'Starter',
    price: 249,
    priceYearly: 199,
    pricePeriod: 'месяц',
    badge: 'Рекомендуем',
    highlight: true,
    description: 'Расширенные лимиты и поддержка для растущей команды.',
    limits: {
      users: 5,
      clients: 350,
      cases: 350,
      files: 3000,
      files_storage_mb: 3 * 1024,
      tasks_per_month: 500,
      reminders_active: 500,
      emails_per_month: 1000,
    },
    features: [
      'До 350 клиентов в год',
      'До 3 ГБ файлов в год',
      'До 5 сотрудников; расширенные/кастомные роли и доступы',
      'До 500 задач/год; календарь с фильтрами по датам и сотрудникам',
      'Авто email-уведомления: до 1000 сообщений/год',
      'Финансы: оплаты и долги; мини-отчеты (история, задолженность, фильтры)',
      'Техподдержка стандартная до 48 часов',
    ],
    qualitative: [],
  },
  PRO: {
    code: 'PRO',
    name: 'Pro',
    price: 549,
    priceYearly: 439,
    pricePeriod: 'месяц',
    badge: 'Максимум',
    highlight: true,
    description: 'Максимальные лимиты, аналитика и расширенные интеграции.',
    limits: {
      users: 15,
      clients: 1000000,
      cases: 1000000,
      files: 100000,
      files_storage_mb: 30 * 1024,
      tasks_per_month: 1000000,
      reminders_active: 10000,
      emails_per_month: 15000,
    },
    features: [
      'Безлимит клиентов',
      'До 30 ГБ файлов в год',
      'До 15 сотрудников; расширенные/кастомные роли и доступы (каждый след. +49 PLN/мес)',
      'Безлимит задач/год; календарь с фильтрами по датам и сотрудникам',
      'Авто email-уведомления: до 15000 сообщений/год (с возможностью увеличения)',
      'Финансы: полный мониторинг; расширенные отчеты; экспорт CSV; категории услуг',
      'Поддержка: высокий приоритет и быстрое реагирование',
    ],
    qualitative: [],
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
