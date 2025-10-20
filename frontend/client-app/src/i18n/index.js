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
      createTask: 'Создать задачу',
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
      editTask: 'Редактировать задачу',
      client: 'Клиент',
      chooseClient: 'Выберите клиента',
      type: 'Тип',
      titleLabel: 'Заголовок',
      titlePH: 'Короткое описание',
      start: 'Начало',
      end: 'Окончание',
      allDay: 'Весь день',
      assignee: 'Ответственный',
      unassigned: '— не назначен —',
      assigneeFallback: 'Показан только ваш аккаунт (нужны права Лид/Админ для списка пользователей).',
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
      createTask: 'Utwórz zadanie',
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
      editTask: 'Edytuj zadanie',
      client: 'Klient',
      chooseClient: 'Wybierz klienta',
      type: 'Typ',
      titleLabel: 'Tytuł',
      titlePH: 'Krótki opis',
      start: 'Początek',
      end: 'Koniec',
      allDay: 'Cały dzień',
      assignee: 'Odpowiedzialny',
      unassigned: '— nieprzypisane —',
      assigneeFallback: 'Wyświetlono tylko Twoje konto (wymagane uprawnienia Lider/Admin do listy użytkowników).',
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