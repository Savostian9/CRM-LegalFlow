import { createI18n } from 'vue-i18n'

const saved = localStorage.getItem('locale') || 'ru'

const messages = {
  ru: {
    app: { name: 'LegalFlow' },
    nav: {
      dashboard: 'Главная',
      clients: 'Клиенты',
      finance: 'Финансы',
      tasks: 'Задачи',
      calendar: 'Календарь',
      settings: 'Настройки',
      notifications: 'Уведомления',
      faq: 'FAQ',
      logout: 'Выйти'
    },
    modal: {
      logout: { title: 'Выйти из аккаунта?', confirm: 'Да, выйти', cancel: 'Отмена' }
    },
    common: {
      loading: 'Загрузка...',
      all: 'Все',
      save: 'Сохранить',
      cancel: 'Отмена',
      yes: 'Да',
      delete: 'Удалить',
      yesDelete: 'Да, удалить',
      copy: 'Копировать',
      firstName: 'Имя',
      lastName: 'Фамилия',
      phone: 'Телефон',
      email: 'Email',
      openAll: 'Открыть',
      processing: 'Выполняется...'
    },
    roles: {
      admin: 'Администратор',
      lead: 'Руководитель',
      leadFull: 'Руководитель (владелец/главный аккаунт)',
      manager: 'Менеджер',
      lawyer: 'Юрист/Консультант',
      assistant: 'Ассистент'
    },
    case: {
      status: {
        preparation: 'Подготовка документов',
        submitted: 'Подано',
        inProgress: 'На рассмотрении',
        decisionPositive: 'Решение положительное',
        decisionNegative: 'Решение отрицательное',
        closed: 'Дело закрыто',
        none: 'Нет дела'
      }
    },
    modals: {
      addClient: {
        title: 'Новый клиент',
        manager: 'Ответственный менеджер',
        chooseManager: 'выберите менеджера',
        managerHint: 'Только руководитель или администратор может выбрать менеджера. Если оставить пустым — ответственным станет создатель.'
      },
      addCase: {
        title: 'Новое дело',
        submissionDate: 'Дата подачи',
        status: 'Статус',
        create: 'Создать дело'
      }
    },
    auth: {
      fields: {
        email: 'Электронная почта',
        password: 'Пароль',
        username: 'Имя пользователя',
        newPassword: 'Новый пароль',
        confirmPassword: 'Подтвердите пароль'
      },
      placeholders: { username: 'Придумайте имя' },
      common: {
        sending: 'Отправка...',
        saving: 'Сохранение...',
        backToLogin: 'Вернуться ко входу',
        error: 'Произошла ошибка.',
        cannotConnect: 'Не удалось подключиться к серверу.',
        passwordsNoMatch: 'Пароли не совпадают.'
      },
      errors: {
        generic: 'Произошла ошибка.',
        cannotConnect: 'Не удалось подключиться к серверу.',
        inviteAccept: 'Произошла ошибка при принятии приглашения.',
        register: 'Произошла ошибка при регистрации.',
        emailPrefix: 'Email: {msg}',
        usernamePrefix: 'Имя пользователя: {msg}',
        passwordPrefix: 'Пароль: {msg}'
      },
      login: {
        welcome: 'С возвращением!',
        subtitle: 'Войдите в свой аккаунт, чтобы продолжить.',
        signingIn: 'Входим...',
        signIn: 'Войти',
        forgot: 'Забыли пароль?',
        create: 'Создать аккаунт',
        invalidCredentials: 'Неверные учетные данные.',
        notActivated: 'Учетная запись не активирована.',
        missingCredentials: 'Укажите email/имя пользователя и пароль.'
      },
      register: {
        title: 'Создайте аккаунт',
        subtitle: 'Начните работу с нашей CRM уже сегодня.',
        inviteBanner: 'Вы регистрируетесь по приглашению. Аккаунт будет привязан к компании.',
        companyNameLabel: 'Название компании',
        companyNamePH: 'Название вашей компании',
        firstNamePH: 'Ваше имя',
        lastNamePH: 'Ваша фамилия',
        creating: 'Создание аккаунта...',
        signUp: 'Зарегистрироваться',
        haveAccount: 'Уже есть аккаунт? Войти',
        userExists: 'Пользователь с таким email уже зарегистрирован. Войдите или воспользуйтесь восстановлением пароля.'
      },
      reset: {
        title: 'Сброс пароля',
        subtitle: 'Введите ваш email, и мы вышлем вам ссылку для восстановления доступа.',
        sendLink: 'Отправить ссылку',
        sentShort: 'Письмо отправлено.'
        ,errors: {
          emailNotFound: 'Пользователь с таким email не найден.',
          requiredEmail: 'Укажите адрес электронной почты.',
          generic: 'Ошибка при отправке письма.'
        }
      },
      resetConfirm: {
        title: 'Установите новый пароль',
        subtitle: 'Придумайте надежный пароль, который вы еще не использовали.',
        savePassword: 'Сохранить пароль',
        redirecting: ' Перенаправляем на страницу входа...'
      },
      verify: {
        title: 'Подтверждение Email',
        sent: 'Мы отправили 6-значный код на',
        codeLabel: 'Код подтверждения',
        confirm: 'Подтвердить',
        resendIn: 'Отправить код повторно можно через:',
        sec: 'сек.',
        resend: 'Отправить код еще раз',
        resendError: 'Ошибка при повторной отправке.',
        sentToast: 'Мы отправили код подтверждения на вашу почту'
      }
    },
    dashboard: {
      title: 'Главная',
      financeSummary: 'Финансовая сводка',
      tasksUpcoming: 'Ближайшие задачи',
      today: 'Сегодня',
      tomorrow: 'Завтра',
      week: 'Неделя',
      month: 'Месяц',
      noTasks: 'Нет задач.',
      noTasksHint: 'Создайте задачу — это поможет не упустить важное.',
      createTask: 'Создать задачу',
      openCalendar: 'Открыть календарь',
      expectedPaymentsMonth: 'Ожидаемые платежи (месяц)',
      receiptsMonth: 'Поступления (месяц)',
      expectedPaymentsTotal: 'Ожидаемые платежи (всего)',
      receiptsTotal: 'Поступления (всего)',
      markDone: 'Готово',
      postpone: 'Отложить',
      open: 'Открыть',
      taskStatus: { scheduled: 'Запланировано', done: 'Выполнено', cancelled: 'Отменено' }
    },
    settings: {
      title: 'Настройки',
      tabs: {
        profile: 'Профиль',
        company: 'Компания',
        users: 'Пользователи',
        invites: 'Приглашения'
      },
      profile: {
        title: 'Профиль пользователя',
        username: 'Имя пользователя',
  usernameTitle: 'Допустимы буквы, цифры и символы . ＠ + - _',
        firstName: 'Имя',
        lastName: 'Фамилия',
        phone: 'Телефон'
      },
      password: {
        title: 'Смена пароля',
        current: 'Текущий пароль',
        new: 'Новый пароль',
        update: 'Обновить пароль'
      },
      danger: {
        title: 'Опасная зона',
        desc: 'Удаление аккаунта необратимо. Все данные будут утрачены.',
        confirmPassword: 'Подтвердите паролем',
        confirmPasswordPH: 'Введите пароль для подтверждения',
        deleteAccount: 'Удалить аккаунт',
        deleteConfirm: 'Вы уверены, что хотите удалить аккаунт? Это действие нельзя отменить.'
      },
      company: {
        title: 'Компания',
        name: 'Название компании',
        address: 'Адрес',
        legal: 'Юридические реквизиты'
      },
      users: {
        title: 'Пользователи компании',
        name: 'Имя и Фамилия',
        email: 'Email',
        role: 'Роль',
        phone: 'Телефон',
        phonePH: 'Номер телефона',
        status: 'Статус',
        blocked: 'Заблокирован',
        deleteUser: 'Удалить пользователя'
      },
      invites: {
        title: 'Приглашения',
        roleAria: 'Роль приглашенного пользователя',
        create: 'Создать приглашение'
      },
      toasts: {
        savedProfile: 'Профиль сохранён',
        saved: 'Сохранено',
        saveError: 'Не удалось сохранить',
        needPasswords: 'Введите текущий и новый пароль',
        passwordUpdated: 'Пароль обновлён',
        passwordUpdateError: 'Не удалось изменить пароль',
        needPassword: 'Введите пароль',
        accountDeleted: 'Аккаунт удалён',
        accountDeleteError: 'Не удалось удалить аккаунт',
        companySaveError: 'Не удалось сохранить настройки компании',
        userDeleted: 'Пользователь удалён',
        userDeleteError: 'Не удалось удалить пользователя',
        createCompanyFirst: 'Сначала создайте компанию на вкладке Компания',
        inviteCreateError: 'Не удалось создать приглашение',
        linkCopied: 'Ссылка скопирована'
      }
    },
    clients: {
      title: 'Клиенты',
      add: 'Добавить клиента',
      searchPlaceholder: 'Поиск по имени, фамилии, email, телефону...',
      date: { all: 'Все', today: 'Сегодня', seven: '7 дней', month: 'Этот месяц', custom: 'Пользовательский' },
      manager: 'Менеджер',
      columns: { name: 'Имя и Фамилия', email: 'Email', phone: 'Телефон', manager: 'Менеджер', created: 'Дата добавления', status: 'Статус дела' },
      extra: {
        from: 'от',
        to: 'до',
        reset: 'Сбросить',
        allStatuses: 'Все статусы',
        statusFilterAria: 'Фильтр по статусу',
        activeFilter: 'Активный фильтр:',
        noResults: 'Клиенты по вашему запросу не найдены',
        empty: 'У вас еще нет клиентов. Нажмите "Добавить клиента", чтобы начать.',
        allOption: 'Все'
      }
    },
    finance: {
      title: 'Финансы',
      revenue: 'Выручка (получено)',
      plan: 'План (стоимость услуг)',
      debt: 'Задолженность',
      columns: { name: 'Имя и Фамилия', email: 'Email', manager: 'Менеджер', cost: 'Стоимость услуги', paid: 'Оплачено', balance: 'Остаток' }
    },
    calendar: {
      actions: { prev: 'Назад', today: 'Сегодня', next: 'Вперёд' },
      view: { month: 'Месяц', week: 'Неделя', day: 'День' },
      searchPH: 'Поиск...',
      statusAll: 'Все статусы',
      typeAll: 'Все типы',
      types: { CALL: 'Звонок', MEETING: 'Встреча', SUBMISSION: 'Подача документов' },
      empty: 'Нет задач в выбранном периоде.',
      createTask: 'Создать задачу',
      weekdays: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    },
    tasks: {
      title: 'Задачи',
      add: 'Добавить задачу',
      cancel: 'Отмена',
      newTask: 'Новая задача',
      create: 'Создать',
      created: 'Задача создана',
      validationDate: 'Укажите дату задачи',
      optional: 'Необязательно: будет сейчас',
      updateForbidden: 'Нет прав для редактирования этой задачи',
      updateMethodNotAllowed: 'Метод не разрешён для этого URL',
      createError: 'Не удалось создать задачу',
      editTask: 'Редактировать задачу',
      client: 'Клиент',
      chooseClient: 'Выберите клиента',
      type: 'Тип',
      titleLabel: 'Заголовок',
      titlePH: 'Короткое описание',
      untitled: 'Без названия',
      start: 'Начало',
      end: 'Окончание',
      allDay: 'Весь день',
      assignee: 'Ответственный',
      unassigned: '— не назначен —',
  assigneeFallback: 'Показан только ваш аккаунт (нужны права Руководителя или Администратора для списка пользователей).',
      save: 'Сохранить',
  gotoClient: 'К клиенту',
      form: {
        location: 'Место/ссылка',
        locationPH: 'Адрес или ссылка',
        reminderMinutes: 'Напоминание, мин',
        description: 'Описание'
      },
      confirm: {
        deleteOne: 'Удалить задачу?',
        discardTitle: 'Несохранённые изменения',
        discardChanges: 'Есть несохранённые изменения. Закрыть без сохранения?'
      },
      validation: {
        requiredCoreFields: 'Заполните обязательные поля: Тип, Клиент, Начало и Окончание',
        endAfterStart: 'Время окончания должно быть позже времени начала'
      },
      toasts: {
        saveError: 'Не удалось сохранить задачу',
        deleteError: 'Не удалось удалить задачу'
      },
      filters: {
        searchPH: 'Поиск по названию...',
        statusAll: 'Все статусы'
      },
      table: { date: 'Дата', time: 'Время', client: 'Клиент', name: 'Название', type: 'Тип', status: 'Статус', assignee: 'Ответственный' },
      loading: 'Загрузка…',
      empty: 'Нет задач.',
      status: { SCHEDULED: 'Запланировано', DONE: 'Выполнено', CANCELLED: 'Отменено' },
      types: { CALL: 'Звонок', MEETING: 'Встреча', SUBMISSION: 'Подача документов' }
    },
    home: {
      login: 'Войти',
      getStarted: 'Начать работу',
      headline: 'Автоматизируйте легализацию. Управляйте бизнесом легко.',
      subheadline: 'Наша CRM — это единая платформа для безупречной работы с клиентами по визам, TRC и картам побыту. Увеличьте продуктивность вашей команды уже сегодня.',
      cta: 'Попробовать бесплатно'
    },
    clientDetail: {
  back: 'Назад',
      title: 'Карточка клиента',
      actions: { deleteClient: 'Удалить клиента' },
      sections: {
        personal: 'Личные данные',
        reminders: 'Напоминания клиенту',
        finance: 'Финансы',
        caseData: 'Данные по делу о легализации',
        checklist: 'Чек-лист поданных документов',
        notes: 'Заметки'
      },
      notesPlaceholder: 'Добавьте внутренние заметки по клиенту...',
      fields: {
        firstName: 'Имя',
        lastName: 'Фамилия',
        phone: 'Телефон',
        email: 'Email',
        address: 'Адрес',
        passportNumber: 'Номер паспорта',
        passportExpiry: 'Паспорт действителен до',
        visaType: 'Тип текущей визы',
        visaExpiry: 'Виза действительна до',
        serviceCost: 'Стоимость услуги',
        amountPaid: 'Оплачено',
        balance: 'Остаток'
      },
      reminders: {
        UMOWA_PRACA_ZLECENIA: 'Umowa o pracę / zlecenia — дата и время',
        UMOWA_NAJMU: 'Umowa najmu — дата и время',
        ZUS_ZUA_ZZA: 'ZUS ZUA / ZZA — дата и время',
        ZUS_RCA_DRA: 'ZUS RCA/DRA — дата и время'
      },
      cases: {
        none: 'У этого клиента еще нет дел.',
        caseN: 'Дело №{n}: {type}',
        type: 'Вид дела',
        submissionDate: 'Дата подачи',
        decisionDate: 'Дата решения',
        status: 'Статус дела',
        addNew: 'Добавить новое дело',
        deleteCase: 'Удалить дело',
        deleteRow: 'Удалить строку',
        addDoc: 'Добавить документ',
        upload: 'Загрузить'
      },
      confirm: {
        deleteRow: 'Вы уверены, что хотите удалить эту строку?',
        deleteCase: 'Вы уверены, что хотите удалить это дело?',
        yesDelete: 'Да, удалить',
        cancel: 'Отмена',
        deleteClient: 'Удалить этого клиента? Все связанные данные будут удалены.'
      },
      toasts: {
        saved: 'Сохранено!',
        saveError: 'Не удалось сохранить данные.',
        loadError: 'Ошибка при загрузке данных клиента'
      },
      caseTypes: {
        '-': '-',
        CZASOWY_POBYT: 'ВНЖ (Czasowy pobyt)',
        STALY_POBYT: 'ПМЖ (Staly pobyt)',
        REZydent_UE: 'Карта резидента ЕС (Karta rezydenta UE)',
        OBYWATELSTWO: 'Гражданство (Obywatelstwo)'
      },
      caseStatus: {
        '-': '-',
        PREPARATION: 'Подготовка документов',
        SUBMITTED: 'Подано',
        IN_PROGRESS: 'На рассмотрении',
        DECISION_POSITIVE: 'Решение положительное',
        DECISION_NEGATIVE: 'Решение отрицательное',
        CLOSED: 'Дело закрыто'
      },
      docTypes: {
        ZALACZNIK_1: 'Załącznik nr 1',
        UMOWA_PRACA: 'Umowa o pracę / zlecenia',
        UMOWA_NAJMU: 'Umowa najmu',
        ZUS_ZUA_ZZA: 'ZUS ZUA / ZZA',
        ZUS_RCA_DRA: 'ZUS RCA/DRA',
        POLISA: 'Polisa ubezpieczeniowa',
        ZASWIADCZENIE_US: 'Zaświadczenie z Urzędu Skarbowego',
        ZASWIADCZENIA_ZUS: 'Zaświadczenia ZUS pracodawcy',
        PIT_37: 'PIT 37',
        BADANIE_LEKARSKIE: 'Badanie lekarskie',
        BADANIE_MEDYCZNE: 'Badanie medyczne',
        SWIADECTWO_KIEROWCY: 'Świadectwo kierowcy'
      }
    },
    lang: { label: 'Язык', ru: 'Русский', pl: 'Polski' }
    ,notifications: {
      title: 'Уведомления',
      loading: 'Загрузка...',
      refresh: 'Обновить',
      markAll: 'Отметить все прочитанными',
      unreadCount: 'Непрочитанных: {count}',
      marking: 'Отмечаем...',
      markOne: 'Прочитано',
      unread: 'Непрочитанных: {n}',
      empty: 'Нет уведомлений.',
      loadError: 'Не удалось загрузить уведомления.',
      sourceReminder: 'Напоминание',
      sourceSystem: 'Система',
      selectAll: 'Выбрать все',
      deselectAll: 'Снять выделение'
      ,confirmDeleteOne: 'Удалить это уведомление?'
      ,confirmDeleteMany: 'Удалить выбранные уведомления ({n})?'
      ,deletedOne: 'Уведомление удалено'
      ,deletedMany: 'Удалено уведомлений: {n}'
    }
    ,faq: {
      title: 'FAQ — Частые вопросы',
      lead: 'Ниже собрали ответы на популярные вопросы по работе с системой.',
      footer: 'Не нашли ответ? Напишите нам на почту',
      prompt: {
        title: 'Хотите быстрее разобраться в системе?',
        subtitle: 'Загляните в раздел FAQ — короткие ответы помогут быстро освоиться с нашей CRM.',
        go: 'Перейти в FAQ',
        later: 'Позже'
      },
      items: [
        {
          anchor: 'invite-users',
          q: 'Как пригласить сотрудника в компанию?',
          a: `<div>
      <p><strong>Приглашение создаётся во вкладке «Приглашения»</strong> в разделе «Настройки».</p>
      <ul>
        <li>Выберите роль, которая будет присвоена приглашённому (например: Менеджер, Юрист/Консультант, Ассистент).</li>
        <li>Нажмите «Создать приглашение» — система создаст ссылку-приглашение.</li>
        <li>Скопируйте и отправьте ссылку коллеге — после регистрации он автоматически появится в списке «Пользователи».</li>
      </ul>
      <p>Приглашать сотрудников может только Руководитель компании.</p>
    </div>`
        },
        {
          anchor: 'roles-rights',
          q: 'Какие роли есть в системе?',
          a: `<ul class="faq-roles">
      <li><strong>Руководитель</strong> — полный доступ к клиентам, задачам и делам компании, настройкам и пользователям.</li>
      <li><strong>Менеджер</strong> — работа с клиентами и делами компании, задачи и календарь, доступ к разделу «Финансы».</li>
        <li><strong>Юрист/Консультант</strong> — работа с клиентами и делами, задачи и календарь, доступ к разделу «Финансы».</li>
        <li><strong>Ассистент</strong> — нет доступа к разделу «Финансы»; помогает по задачам и календарю.</li>
    </ul>
    <div class="faq-matrix">
      <p><strong>Доступ и видимость:</strong></p>
      <ul>
        <li>Финансы: доступны ролям <strong>Руководитель</strong>, <strong>Менеджер</strong>, <strong>Юрист/Консультант</strong>; у <strong>Ассистент</strong> доступа нет.</li>
        <li>Клиенты и дела: <strong>Руководитель</strong> видит всех клиентов компании; <strong>Менеджер</strong> — только своих (назначенных ему) клиентов и их дела; <strong>Юрист/Консультант</strong> и <strong>Ассистент</strong> — видят всех клиентов.</li>
        <li>Пользователи и настройки компании: только <strong>Руководитель</strong>.</li>
        <li>Задачи и календарь: доступны всем ролям.</li>
        <li>Уведомления: доступны всем ролям.</li>
      </ul>
    </div>`
        },
        {
          anchor: 'create-client',
          q: 'Как создать клиента?',
          a: `<div>
      <p><strong>Где:</strong> раздел «Клиенты».</p>
      <ol>
        <li>Нажмите кнопку «Добавить клиента».</li>
        <li>Заполните поля: Имя, Фамилия, Email, Телефон.</li>
        <li>Если у вас роль Руководитель/Администратор — вы можете назначить ответственного менеджера.</li>
        <li>Сохраните. Новый клиент появится в списке. Менеджер увидит только назначенных ему клиентов.</li>
      </ol>
    </div>`
        },
        {
          anchor: 'create-case',
          q: 'Как создать дело и добавить документы?',
          a: `<div>
      <p><strong>Где:</strong> в карточке клиента (открывается кликом по строке клиента в списке).</p>
      <ol>
        <li>Откройте Клиенты → клик по нужному клиенту.</li>
        <li>Внизу карточки нажмите «Добавить новое дело».</li>
        <li>Укажите Вид дела, даты подачи/решения и Статус дела.</li>
        <li>Изменения в карточке сохраняются автоматически при выборе значений.</li>
        <li>При необходимости добавьте напоминания клиенту в секции «Напоминания клиенту» — письмо уйдёт на email клиента в указанное время.</li>
      </ol>
      <p style="margin-top:8px"><strong>Документы по делу (чек‑лист):</strong></p>
      <ul>
        <li>Раскройте дело и перейдите в «Чек-лист поданных документов».</li>
        <li>Отмечайте галочкой документы, которые уже поданы.</li>
        <li>Чтобы приложить файлы, нажмите «Загрузить» напротив документа и выберите файлы — они появятся как метки и доступны для просмотра.</li>
        <li>Если нужен другой тип документа, нажмите «Добавить документ», впишите название и при необходимости загрузите файлы.</li>
        <li>Ненужную строку можно удалить крестиком.</li>
      </ul>
    </div>`
        },
        {
          anchor: 'tasks-usage',
          q: 'Как работают задачи (создание, права, статусы)?',
          a: `<ul>
      <li><strong>Где создать:</strong> разделы «Календарь» и «Задачи» — кнопка «Создать задачу».</li>
      <li><strong>Что можно менять:</strong> заголовок, даты, клиента, статус, ответственного.</li>
      <li><strong>Назначение:</strong> Руководитель может назначать задачу менеджеру и другим пользователям компании.</li>
      <li><strong>Статусы:</strong> Запланировано, Выполнено, Отменено. На главной есть кнопка «Готово» для быстрого закрытия задачи.</li>
      <li><strong>Права по задачам:</strong> задачи и календарь доступны всем ролям. Руководитель — видит все задачи компании; Менеджер — видит только задачи, где он назначен ответственным; Юрист/Консультант и Ассистент — видят все задачи.</li>
      <li><strong>Уведомления:</strong> входящие оповещения видны в разделе «Уведомления»; можно отмечать как прочитанные.</li>
    </ul>`
        },
        {
          anchor: 'notifications-how',
          q: 'Как работают уведомления?',
          a: `<ul>
      <li><strong>Что приходит:</strong> уведомления о назначенных задачах и о факте отправки напоминания клиенту.</li>
      <li><strong>Напоминания клиенту:</strong> вы создаёте напоминание в карточке клиента; в назначенный день и (если указано) время система автоматически отправит клиенту письмо на его email. После отправки в системе появляется внутреннее уведомление для ответственного сотрудника с пометкой «отправлено» (или «ошибка отправки», если письмо не ушло).</li>
      <li><strong>Куда отправляется:</strong> письмо — на email из карточки клиента; внутреннее уведомление — в виджете и разделе «Уведомления».</li>
      <li><strong>Где смотреть:</strong> виджет «Уведомления» на главной и раздел «Уведомления» в кабинете. В сайдбаре отображается счётчик непрочитанных.</li>
      <li><strong>Как читать:</strong> клик по уведомлению открывает карточку клиента, если он указан в задаче либо напоминании. Можно отметить одно или все уведомления как прочитанные.</li>
      <li><strong>Метки:</strong> в уведомлении отображаются клиент, пользователь, тип напоминания и источник (Напоминание/Система).</li>
    </ul>`
        }
      ]
    }
    ,help: {
      title: 'Нужна помощь?',
      subtitle: 'Ответы на частые вопросы и короткие подсказки по работе с системой.',
      openFaq: 'Открыть FAQ',
      contactSupport: 'Написать в поддержку'
    }
    ,billing: {
      title: 'Мой план',
      error: 'Ошибка',
      usageLimits: 'Использование и лимиты',
      resource: 'Ресурс',
      current: 'Текущее',
      limit: 'Лимит',
      rows: {
        users: 'Пользователи',
        clients: 'Клиенты',
        cases: 'Дела',
        files: 'Файлы',
        storageMb: 'Хранилище (MB)',
        tasksMonth: 'Задачи / месяц',
        remindersActive: 'Активные напоминания',
        emailsMonth: 'Email / месяц'
      },
      trial: {
        remaining: 'Осталось {days} {dayWord} Trial периода.',
        until: 'До: {date}',
        expired: 'Срок истёк — обновите план, чтобы продолжить без ограничений.',
        upgradeStarter: 'Перейти на Starter'
      },
      upgrade: { toPro: 'Апгрейд до Pro' },
      plan: {
        currentStarter: 'Текущий план Starter активен.',
        proActive: 'План Pro активен. Максимальные лимиты.',
        active: 'Активен'
      },
      toast: {
        upgradeSoon: 'Функция апгрейда скоро будет доступна.',
        upgraded: 'План обновлён до {plan}',
        upgradeFailed: 'Не удалось обновить план'
      }
    }
  },
  pl: {
    app: { name: 'LegalFlow' },
    nav: {
      dashboard: 'Główna',
      clients: 'Klienci',
      finance: 'Finanse',
      tasks: 'Zadania',
      calendar: 'Kalendarz',
      settings: 'Ustawienia',
      notifications: 'Powiadomienia',
      faq: 'FAQ',
      logout: 'Wyloguj się'
    },
    modal: {
      logout: { title: 'Wylogować się?', confirm: 'Tak, wyloguj', cancel: 'Anuluj' }
    },
    common: {
      loading: 'Ładowanie...',
      all: 'Wszystkie',
      save: 'Zapisz',
      cancel: 'Anuluj',
      yes: 'Tak',
      delete: 'Usuń',
      yesDelete: 'Tak, usuń',
      copy: 'Kopiuj',
      firstName: 'Imię',
      lastName: 'Nazwisko',
      phone: 'Telefon',
      email: 'Email',
      openAll: 'Otwórz',
      processing: 'Przetwarzanie...'
    },
    roles: {
      admin: 'Administrator',
      lead: 'Kierownik',
      leadFull: 'Kierownik (właściciel/główne konto)',
      manager: 'Menedżer',
      lawyer: 'Prawnik/Konsultant',
      assistant: 'Asystent'
    },
    case: {
      status: {
        preparation: 'Przygotowanie dokumentów',
        submitted: 'Złożono',
        inProgress: 'W trakcie rozpatrywania',
        decisionPositive: 'Decyzja pozytywna',
        decisionNegative: 'Decyzja negatywna',
        closed: 'Sprawa zamknięta',
        none: 'Brak sprawy'
      }
    },
    modals: {
      addClient: {
        title: 'Nowy klient',
        manager: 'Odpowiedzialny menedżer',
        chooseManager: 'wybierz menedżera',
        managerHint: 'Tylko kierownik lub administrator może wybrać menedżera. Jeśli pozostawisz puste — odpowiedzialnym zostanie twórca.'
      },
      addCase: {
        title: 'Nowa sprawa',
        submissionDate: 'Data złożenia',
        status: 'Status',
        create: 'Utwórz sprawę'
      }
    },
    auth: {
      fields: {
        email: 'Adres e-mail',
        password: 'Hasło',
        username: 'Nazwa użytkownika',
        newPassword: 'Nowe hasło',
        confirmPassword: 'Potwierdź hasło'
      },
      placeholders: { username: 'Wymyśl nazwę' },
      common: {
        sending: 'Wysyłanie...',
        saving: 'Zapisywanie...',
        backToLogin: 'Powrót do logowania',
        error: 'Wystąpił błąd.',
        cannotConnect: 'Nie udało się połączyć z serwerem.',
        passwordsNoMatch: 'Hasła się nie zgadzają.'
      },
      errors: {
        generic: 'Wystąpił błąd.',
        cannotConnect: 'Nie udało się połączyć z serwerem.',
        inviteAccept: 'Wystąpił błąd podczas akceptacji zaproszenia.',
        register: 'Wystąpił błąd podczas rejestracji.',
        emailPrefix: 'Email: {msg}',
        usernamePrefix: 'Nazwa użytkownika: {msg}',
        passwordPrefix: 'Hasło: {msg}'
      },
      login: {
        welcome: 'Witamy ponownie!',
        subtitle: 'Zaloguj się, aby kontynuować.',
        signingIn: 'Logowanie...',
        signIn: 'Zaloguj się',
        forgot: 'Zapomniałeś hasła?',
        create: 'Utwórz konto',
        invalidCredentials: 'Nieprawidłowe dane logowania.',
        notActivated: 'Konto nie zostało aktywowane.',
        missingCredentials: 'Podaj email/nazwę użytkownika i hasło.'
      },
      register: {
        title: 'Utwórz konto',
        subtitle: 'Zacznij korzystać z naszego CRM już dziś.',
        inviteBanner: 'Rejestrujesz się przez zaproszenie. Konto zostanie przypisane do firmy.',
        companyNameLabel: 'Nazwa firmy',
        companyNamePH: 'Nazwa Twojej firmy',
        firstNamePH: 'Twoje imię',
        lastNamePH: 'Twoje nazwisko',
        creating: 'Tworzenie konta...',
        signUp: 'Zarejestruj się',
        haveAccount: 'Masz już konto? Zaloguj się',
        userExists: 'Użytkownik z takim adresem e-mail już istnieje. Zaloguj się lub użyj odzyskiwania hasła.'
      },
      reset: {
        title: 'Resetowanie hasła',
        subtitle: 'Podaj swój adres e-mail, a wyślemy link do odzyskania dostępu.',
        sendLink: 'Wyślij link',
        sentShort: 'Link został wysłany.'
        ,errors: {
          emailNotFound: 'Użytkownik z takim adresem e-mail nie został znaleziony.',
          requiredEmail: 'Podaj adres e-mail.',
          generic: 'Wystąpił błąd podczas wysyłania wiadomości.'
        }
      },
      resetConfirm: {
        title: 'Ustaw nowe hasło',
        subtitle: 'Wymyśl silne hasło, którego wcześniej nie używałeś.',
        savePassword: 'Zapisz hasło',
        redirecting: ' Przekierowujemy do logowania...'
      },
      verify: {
        title: 'Potwierdzenie e-maila',
        sent: 'Wysłaliśmy 6-cyfrowy kod na',
        codeLabel: 'Kod potwierdzający',
        confirm: 'Potwierdź',
        resendIn: 'Możesz ponownie wysłać kod za:',
        sec: 'sek.',
        resend: 'Wyślij kod ponownie',
        resendError: 'Błąd przy ponownym wysyłaniu.',
        sentToast: 'Wysłaliśmy kod potwierdzający na Twój e-mail'
      }
    },
    dashboard: {
      title: 'Główna',
      financeSummary: 'Podsumowanie finansowe',
      tasksUpcoming: 'Nadchodzące zadania',
      today: 'Dziś',
      tomorrow: 'Jutro',
      week: 'Tydzień',
      month: 'Miesiąc',
      noTasks: 'Brak zadań.',
      noTasksHint: 'Utwórz zadanie — to pomoże nie przegapić ważnych spraw.',
      createTask: 'Utwórz zadanie',
      openCalendar: 'Otwórz kalendarz',
      expectedPaymentsMonth: 'Oczekiwane płatności (miesiąc)',
      receiptsMonth: 'Wpływy (miesiąc)',
      expectedPaymentsTotal: 'Oczekiwane płatności (łącznie)',
      receiptsTotal: 'Wpływy (łącznie)',
      markDone: 'Gotowe',
      postpone: 'Przełóż',
      open: 'Otwórz',
      taskStatus: { scheduled: 'Zaplanowano', done: 'Wykonano', cancelled: 'Anulowano' }
    },
    settings: {
      title: 'Ustawienia',
      tabs: {
        profile: 'Profil',
        company: 'Firma',
        users: 'Użytkownicy',
        invites: 'Zaproszenia'
      },
      profile: {
        title: 'Profil użytkownika',
        username: 'Nazwa użytkownika',
  usernameTitle: 'Dozwolone litery, cyfry oraz znaki . ＠ + - _',
        firstName: 'Imię',
        lastName: 'Nazwisko',
        phone: 'Telefon'
      },
      password: {
        title: 'Zmiana hasła',
        current: 'Obecne hasło',
        new: 'Nowe hasło',
        update: 'Zmień hasło'
      },
      danger: {
        title: 'Strefa ryzyka',
        desc: 'Usunięcie konta jest nieodwracalne. Wszystkie dane zostaną utracone.',
        confirmPassword: 'Potwierdź hasłem',
        confirmPasswordPH: 'Wpisz hasło, aby potwierdzić',
        deleteAccount: 'Usuń konto',
        deleteConfirm: 'Czy na pewno chcesz usunąć konto? Tego nie można cofnąć.'
      },
      company: {
        title: 'Firma',
        name: 'Nazwa firmy',
        address: 'Adres',
        legal: 'Dane prawne'
      },
      users: {
        title: 'Użytkownicy firmy',
        name: 'Imię i nazwisko',
        email: 'Email',
        role: 'Rola',
        phone: 'Telefon',
        phonePH: 'Numer telefonu',
        status: 'Status',
        blocked: 'Zablokowany',
        deleteUser: 'Usuń użytkownika'
      },
      invites: {
        title: 'Zaproszenia',
        roleAria: 'Rola zapraszanej osoby',
        create: 'Utwórz zaproszenie'
      },
      toasts: {
        savedProfile: 'Profil zapisano',
        saved: 'Zapisano',
        saveError: 'Nie udało się zapisać',
        needPasswords: 'Podaj obecne i nowe hasło',
        passwordUpdated: 'Hasło zmieniono',
        passwordUpdateError: 'Nie udało się zmienić hasła',
        needPassword: 'Wpisz hasło',
        accountDeleted: 'Konto usunięto',
        accountDeleteError: 'Nie udało się usunąć konta',
        companySaveError: 'Nie udało się zapisać ustawień firmy',
        userDeleted: 'Użytkownika usunięto',
        userDeleteError: 'Nie udało się usunąć użytkownika',
        createCompanyFirst: 'Najpierw utwórz firmę w zakładce Firma',
        inviteCreateError: 'Nie udało się utworzyć zaproszenia',
        linkCopied: 'Link skopiowano'
      }
    },
    clients: {
      title: 'Klienci',
      add: 'Dodaj klienta',
      searchPlaceholder: 'Szukaj po imieniu, nazwisku, e-mailu, telefonie...',
      date: { all: 'Wszystkie', today: 'Dziś', seven: '7 dni', month: 'Ten miesiąc', custom: 'Niestandardowy' },
      manager: 'Menedżer',
      columns: { name: 'Imię i nazwisko', email: 'Email', phone: 'Telefon', manager: 'Menedżer', created: 'Data dodania', status: 'Status sprawy' },
      extra: {
        from: 'od',
        to: 'do',
        reset: 'Wyczyść',
        allStatuses: 'Wszystkie statusy',
        statusFilterAria: 'Filtr statusu',
        activeFilter: 'Aktywny filtr:',
        noResults: 'Nie znaleziono klientów dla Twojego zapytania',
        empty: 'Nie masz jeszcze klientów. Kliknij „Dodaj klienta”, aby rozpocząć.',
        allOption: 'Wszyscy'
      }
    },
    finance: {
      title: 'Finanse',
      revenue: 'Przychód (otrzymano)',
      plan: 'Plan (koszt usług)',
      debt: 'Zadłużenie',
      columns: { name: 'Imię i nazwisko', email: 'Email', manager: 'Menedżer', cost: 'Koszt usługi', paid: 'Opłacono', balance: 'Saldo' }
    },
    calendar: {
      actions: { prev: 'Wstecz', today: 'Dziś', next: 'Naprzód' },
      view: { month: 'Miesiąc', week: 'Tydzień', day: 'Dzień' },
      searchPH: 'Szukaj...',
      statusAll: 'Wszystkie statusy',
      typeAll: 'Wszystkie typy',
      types: { CALL: 'Telefon', MEETING: 'Spotkanie', SUBMISSION: 'Złożenie dokumentów' },
      empty: 'Brak zadań w wybranym okresie.',
      createTask: 'Utwórz zadanie',
      weekdays: ['Pn', 'Wt', 'Śr', 'Cz', 'Pt', 'So', 'Nd']
    },
    tasks: {
      title: 'Zadania',
      add: 'Dodaj zadanie',
      cancel: 'Anuluj',
      newTask: 'Nowe zadanie',
      create: 'Utwórz',
      created: 'Zadanie utworzone',
      validationDate: 'Podaj datę zadania',
      optional: 'Opcjonalnie: ustawiamy teraz',
      updateForbidden: 'Brak uprawnień do edycji tego zadania',
      updateMethodNotAllowed: 'Metoda niedozwolona dla tego adresu',
      createError: 'Nie udało się utworzyć zadania',
      editTask: 'Edytuj zadanie',
      client: 'Klient',
      chooseClient: 'Wybierz klienta',
      type: 'Typ',
      titleLabel: 'Tytuł',
      titlePH: 'Krótki opis',
      untitled: 'Bez tytułu',
      start: 'Początek',
      end: 'Koniec',
      allDay: 'Cały dzień',
      assignee: 'Odpowiedzialny',
      unassigned: '— nieprzypisane —',
  assigneeFallback: 'Wyświetlono tylko Twoje konto (wymagane uprawnienia Kierownik/Administrator do listy użytkowników).',
      save: 'Zapisz',
  gotoClient: 'Do klienta',
      form: {
        location: 'Miejsce/link',
        locationPH: 'Adres lub link',
        reminderMinutes: 'Przypomnienie, min',
        description: 'Opis'
      },
      confirm: {
        deleteOne: 'Usunąć zadanie?',
        discardTitle: 'Niezapisane zmiany',
        discardChanges: 'Są niezapisane zmiany. Zamknąć bez zapisu?'
      },
      validation: {
        requiredCoreFields: 'Wypełnij wymagane pola: Typ, Klient, Początek i Koniec',
        endAfterStart: 'Czas zakończenia musi być późniejszy niż czas rozpoczęcia'
      },
      toasts: {
        saveError: 'Nie udało się zapisać zadania',
        deleteError: 'Nie udało się usunąć zadania'
      },
      filters: {
        searchPH: 'Szukaj po nazwie...',
        statusAll: 'Wszystkie statusy'
      },
      table: { date: 'Data', time: 'Czas', client: 'Klient', name: 'Nazwa', type: 'Typ', status: 'Status', assignee: 'Odpowiedzialny' },
      loading: 'Ładowanie…',
      empty: 'Brak zadań.',
      status: { SCHEDULED: 'Zaplanowano', DONE: 'Wykonano', CANCELLED: 'Anulowano' },
      types: { CALL: 'Telefon', MEETING: 'Spotkanie', SUBMISSION: 'Złożenie dokumentów' }
    },
    home: {
      login: 'Zaloguj się',
      getStarted: 'Zacznij',
      headline: 'Zautomatyzuj legalizację. Zarządzaj biznesem z łatwością.',
      subheadline: 'Nasz CRM to jedna platforma do bezbłędnej pracy z klientami w zakresie wiz, TRC i kart pobytu. Zwiększ produktywność swojego zespołu już dziś.',
      cta: 'Wypróbuj za darmo'
    },
    clientDetail: {
      back: 'Wróć',
      title: 'Karta klienta',
      actions: { deleteClient: 'Usuń klienta' },
      sections: {
        personal: 'Dane osobowe',
        reminders: 'Przypomnienia dla klienta',
        finance: 'Finanse',
        caseData: 'Dane sprawy legalizacyjnej',
        checklist: 'Lista złożonych dokumentów',
        notes: 'Notatki'
      },
      notesPlaceholder: 'Dodaj wewnętrzne notatki o kliencie...',
      fields: {
        firstName: 'Imię',
        lastName: 'Nazwisko',
        phone: 'Telefon',
        email: 'Email',
        address: 'Adres',
        passportNumber: 'Numer paszportu',
        passportExpiry: 'Paszport ważny do',
        visaType: 'Rodzaj aktualnej wizy',
        visaExpiry: 'Wiza ważna do',
        serviceCost: 'Koszt usługi',
        amountPaid: 'Zapłacono',
        balance: 'Saldo'
      },
      reminders: {
        UMOWA_PRACA_ZLECENIA: 'Umowa o pracę / zlecenia — data i godzina',
        UMOWA_NAJMU: 'Umowa najmu — data i godzina',
        ZUS_ZUA_ZZA: 'ZUS ZUA / ZZA — data i godzina',
        ZUS_RCA_DRA: 'ZUS RCA/DRA — data i godzina'
      },
      cases: {
        none: 'Ten klient nie ma jeszcze spraw.',
        caseN: 'Sprawa nr {n}: {type}',
        type: 'Rodzaj sprawy',
        submissionDate: 'Data złożenia',
        decisionDate: 'Data decyzji',
        status: 'Status sprawy',
        addNew: 'Dodaj nową sprawę',
        deleteCase: 'Usuń sprawę',
        deleteRow: 'Usuń wiersz',
        addDoc: 'Dodaj dokument',
        upload: 'Prześlij'
      },
      confirm: {
        deleteRow: 'Czy na pewno chcesz usunąć ten wiersz?',
        deleteCase: 'Czy na pewno chcesz usunąć tę sprawę?',
        yesDelete: 'Tak, usuń',
        cancel: 'Anuluj',
        deleteClient: 'Usunąć tego klienta? Wszystkie powiązane dane zostaną usunięte.'
      },
      toasts: {
        saved: 'Zapisano!',
        saveError: 'Nie udało się zapisać danych.',
        loadError: 'Błąd podczas wczytywania danych klienta'
      },
      caseTypes: {
        '-': '-',
        CZASOWY_POBYT: 'Karta pobytu czasowego (Czasowy pobyt)',
        STALY_POBYT: 'Pobyt stały (Staly pobyt)',
        REZydent_UE: 'Karta rezydenta UE (Karta rezydenta UE)',
        OBYWATELSTWO: 'Obywatelstwo (Obywatelstwo)'
      },
      caseStatus: {
        '-': '-',
        PREPARATION: 'Przygotowanie dokumentów',
        SUBMITTED: 'Złożono',
        IN_PROGRESS: 'W trakcie rozpatrywania',
        DECISION_POSITIVE: 'Decyzja pozytywna',
        DECISION_NEGATIVE: 'Decyzja negatywna',
        CLOSED: 'Sprawa zamknięta'
      },
      docTypes: {
        ZALACZNIK_1: 'Załącznik nr 1',
        UMOWA_PRACA: 'Umowa o pracę / zlecenia',
        UMOWA_NAJMU: 'Umowa najmu',
        ZUS_ZUA_ZZA: 'ZUS ZUA / ZZA',
        ZUS_RCA_DRA: 'ZUS RCA/DRA',
        POLISA: 'Polisa ubezpieczeniowa',
        ZASWIADCZENIE_US: 'Zaświadczenie z Urzędu Skarbowego',
        ZASWIADCZENIA_ZUS: 'Zaświadczenia ZUS pracodawcy',
        PIT_37: 'PIT 37',
        BADANIE_LEKARSKIE: 'Badanie lekarskie',
        BADANIE_MEDYCZNE: 'Badanie medyczne',
        SWIADECTWO_KIEROWCY: 'Świadectwo kierowcy'
      }
    },
    lang: { label: 'Język', ru: 'Rosyjski', pl: 'Polski' }
    ,notifications: {
      title: 'Powiadomienia',
      loading: 'Ładowanie...',
      refresh: 'Odśwież',
      markAll: 'Oznacz wszystkie jako przeczytane',
      unreadCount: 'Nieprzeczytane: {count}',
      marking: 'Oznaczanie...',
      markOne: 'Przeczytane',
      unread: 'Nieprzeczytane: {n}',
      empty: 'Brak powiadomień.',
      loadError: 'Nie udało się wczytać powiadomień.',
      sourceReminder: 'Przypomnienie',
      sourceSystem: 'System',
      selectAll: 'Zaznacz wszystkie',
      deselectAll: 'Odznacz wszystkie'
      ,confirmDeleteOne: 'Usunąć to powiadomienie?'
      ,confirmDeleteMany: 'Usunąć zaznaczone powiadomienia ({n})?'
      ,deletedOne: 'Powiadomienie usunięte'
      ,deletedMany: 'Usunięto powiadomień: {n}'
    }
    ,faq: {
      title: 'FAQ — Najczęstsze pytania',
      lead: 'Poniżej zebraliśmy odpowiedzi na najpopularniejsze pytania dotyczące pracy z systemem.',
      footer: 'Nie znaleźliście odpowiedzi? Napiszcie do nas na',
      prompt: {
        title: 'Chcesz szybciej poznać system?',
        subtitle: 'Zajrzyj do działu FAQ — krótkie odpowiedzi pomogą szybko odnaleźć się w naszym CRM.',
        go: 'Przejdź do FAQ',
        later: 'Później'
      },
      items: [
        {
          anchor: 'invite-users',
          q: 'Jak zaprosić pracownika do firmy?',
          a: `<div>
      <p><strong>Zaproszenie tworzysz w zakładce „Zaproszenia”</strong> w sekcji „Ustawienia”.</p>
      <ul>
        <li>Wybierz rolę, którą otrzyma zapraszana osoba (np. Menedżer, Prawnik/Konsultant, Asystent).</li>
        <li>Kliknij „Utwórz zaproszenie” — system wygeneruje link zaproszenia.</li>
        <li>Skopiuj i wyślij link koledze — po rejestracji automatycznie pojawi się na liście „Użytkownicy”.</li>
      </ul>
      <p>Zapraszać pracowników może tylko Kierownik firmy.</p>
    </div>`
        },
        {
          anchor: 'roles-rights',
          q: 'Jakie role są w systemie?',
          a: `<ul class="faq-roles">
      <li><strong>Kierownik</strong> — pełny dostęp do klientów, zadań i spraw firmy, ustawień oraz użytkowników.</li>
      <li><strong>Menedżer</strong> — praca z klientami i sprawami firmy, zadania i kalendarz, dostęp do sekcji „Finanse”.</li>
        <li><strong>Prawnik/Konsultant</strong> — praca z klientami i sprawami, zadania i kalendarz, dostęp do sekcji „Finanse”.</li>
        <li><strong>Asystent</strong> — brak dostępu do sekcji „Finanse”; pomaga przy zadaniach i kalendarzu.</li>
    </ul>
    <div class="faq-matrix">
      <p><strong>Dostęp i widoczność:</strong></p>
      <ul>
        <li>Finanse: dostępne dla ról <strong>Kierownik</strong>, <strong>Menedżer</strong>, <strong>Prawnik/Konsultant</strong>; <strong>Asystent</strong> nie ma dostępu.</li>
        <li>Klienci i sprawy: <strong>Kierownik</strong> widzi wszystkich klientów firmy; <strong>Menedżer</strong> — tylko swoich (przypisanych) klientów i ich sprawy; <strong>Prawnik/Konsultant</strong> i <strong>Asystent</strong> — widzą wszystkich klientów.</li>
        <li>Użytkownicy i ustawienia firmy: tylko <strong>Kierownik</strong>.</li>
        <li>Zadania i kalendarz: dostępne dla wszystkich ról.</li>
        <li>Powiadomienia: dostępne dla wszystkich ról.</li>
      </ul>
    </div>`
        },
        {
          anchor: 'create-client',
          q: 'Jak utworzyć klienta?',
          a: `<div>
      <p><strong>Gdzie:</strong> sekcja „Klienci”.</p>
      <ol>
        <li>Kliknij przycisk „Dodaj klienta”.</li>
        <li>Uzupełnij pola: Imię, Nazwisko, Email, Telefon.</li>
        <li>Jeśli masz rolę Kierownik/Administrator — możesz wskazać odpowiedzialnego menedżera.</li>
        <li>Zapisz. Nowy klient pojawi się na liście. Menedżer widzi tylko przypisanych do niego klientów.</li>
      </ol>
    </div>`
        },
        {
          anchor: 'create-case',
          q: 'Jak utworzyć sprawę i dodać dokumenty?',
          a: `<div>
      <p><strong>Gdzie:</strong> w karcie klienta (otwierasz klikając w wiersz klienta na liście).</p>
      <ol>
        <li>Otwórz Klienci → kliknij odpowiedniego klienta.</li>
        <li>Na dole karty kliknij „Dodaj nową sprawę”.</li>
        <li>Wskaż Rodzaj sprawy, daty złożenia/decyzji oraz Status sprawy.</li>
        <li>Zmiany w karcie zapisywane są automatycznie po wyborze wartości.</li>
        <li>W razie potrzeby dodaj przypomnienia dla klienta w sekcji „Przypomnienia dla klienta” — wiadomość e‑mail zostanie wysłana w wybranym czasie.</li>
      </ol>
      <p style="margin-top:8px"><strong>Dokumenty w sprawie (checklista):</strong></p>
      <ul>
        <li>Rozwiń sprawę i przejdź do „Lista złożonych dokumentów”.</li>
        <li>Odhaczaj dokumenty, które zostały już złożone.</li>
        <li>Aby dołączyć pliki, kliknij „Prześlij” przy dokumencie i wybierz pliki — pojawią się jako etykiety i będą dostępne do podglądu.</li>
        <li>Jeśli potrzebny jest inny typ dokumentu, kliknij „Dodaj dokument”, wpisz nazwę i w razie potrzeby prześlij pliki.</li>
        <li>Niepotrzebny wiersz możesz usunąć krzyżykiem.</li>
      </ul>
    </div>`
        },
        {
          anchor: 'tasks-usage',
          q: 'Jak działają zadania (tworzenie, uprawnienia, statusy)?',
          a: `<ul>
      <li><strong>Gdzie utworzyć:</strong> sekcje „Kalendarz” i „Zadania” — przycisk „Utwórz zadanie”.</li>
      <li><strong>Co można zmieniać:</strong> tytuł, daty, klienta, status, odpowiedzialnego.</li>
      <li><strong>Przypisywanie:</strong> Kierownik może przypisywać zadania menedżerowi i innym użytkownikom firmy.</li>
      <li><strong>Statusy:</strong> Zaplanowano, Wykonano, Anulowano. Na stronie głównej jest przycisk „Gotowe” do szybkiego zamykania zadań.</li>
      <li><strong>Uprawnienia do zadań:</strong> zadania i kalendarz są dostępne dla wszystkich ról. Kierownik — widzi wszystkie zadania firmy; Menedżer — widzi tylko zadania, gdzie jest odpowiedzialnym; Prawnik/Konsultant i Asystent — widzą wszystkie zadania.</li>
      <li><strong>Powiadomienia:</strong> przychodzące alerty widoczne są w sekcji „Powiadomienia”; można je oznaczać jako przeczytane.</li>
    </ul>`
        },
        {
          anchor: 'notifications-how',
          q: 'Jak działają powiadomienia?',
          a: `<ul>
      <li><strong>Co przychodzi:</strong> powiadomienia o przypisanych zadaniach oraz o fakcie wysłania przypomnienia do klienta.</li>
      <li><strong>Przypomnienia dla klienta:</strong> tworzysz przypomnienie w karcie klienta; w wybranym dniu i (jeśli podano) czasie system automatycznie wyśle wiadomość na e‑mail klienta. Po wysyłce w systemie pojawia się wewnętrzne powiadomienie dla odpowiedzialnego pracownika z adnotacją „wysłano” (lub „błąd wysyłki”, jeśli wiadomość nie została dostarczona).</li>
      <li><strong>Gdzie trafia:</strong> wiadomość — na e‑mail z karty klienta; wewnętrzne powiadomienie — do widżetu i sekcji „Powiadomienia”.</li>
      <li><strong>Gdzie sprawdzić:</strong> widżet „Powiadomienia” na stronie głównej oraz sekcja „Powiadomienia” w panelu. W pasku bocznym wyświetlany jest licznik nieprzeczytanych.</li>
      <li><strong>Jak czytać:</strong> kliknięcie powiadomienia otwiera kartę klienta, jeśli został wskazany w zadaniu lub przypomnieniu. Można oznaczyć jedno lub wszystkie powiadomienia jako przeczytane.</li>
      <li><strong>Etykiety:</strong> w powiadomieniu widoczni są klient, użytkownik, typ przypomnienia i źródło (Przypomnienie/System).</li>
    </ul>`
        }
      ]
    }
    ,help: {
      title: 'Potrzebujesz pomocy?',
      subtitle: 'Odpowiedzi na najczęstsze pytania i krótkie wskazówki dotyczące pracy z systemem.',
      openFaq: 'Otwórz FAQ',
      contactSupport: 'Napisz do wsparcia'
    }
    ,billing: {
      title: 'Mój plan',
      error: 'Błąd',
      usageLimits: 'Wykorzystanie i limity',
      resource: 'Zasób',
      current: 'Bieżące',
      limit: 'Limit',
      rows: {
        users: 'Użytkownicy',
        clients: 'Klienci',
        cases: 'Sprawy',
        files: 'Pliki',
        storageMb: 'Magazyn (MB)',
        tasksMonth: 'Zadania / miesiąc',
        remindersActive: 'Aktywne przypomnienia',
        emailsMonth: 'Email / miesiąc'
      },
      trial: {
        remaining: 'Pozostało {days} {dayWord} okresu Trial.',
        until: 'Do: {date}',
        expired: 'Okres wygasł — zaktualizuj plan, aby kontynuować bez ograniczeń.',
        upgradeStarter: 'Przejdź na Starter'
      },
      upgrade: { toPro: 'Przejdź na Pro' },
      plan: {
        currentStarter: 'Plan Starter jest aktywny.',
        proActive: 'Plan Pro aktywny. Maksymalne limity.',
        active: 'Aktywny'
      },
      toast: {
        upgradeSoon: 'Funkcja ulepszenia wkrótce będzie dostępna.',
        upgraded: 'Plan został zaktualizowany do {plan}',
        upgradeFailed: 'Nie udało się zaktualizować planu'
      }
    }
  }
}

const i18n = createI18n({
  // Keep legacy mode for existing this.$t usage, but allow Composition API in setup()
  legacy: true,
  allowComposition: true,
  globalInjection: true,
  locale: saved,
  fallbackLocale: 'ru',
  messages
})

// Ensure <html lang> matches the current locale on startup
try {
  document.documentElement.setAttribute('lang', saved)
} catch (e) { /* no-op */ void e }

export default i18n