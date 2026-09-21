# SanaLab — Диагностика болезней растений по фото

Веб-приложение на Django, определяющее болезни томата, картофеля и перца по фотографии листа (компьютерное зрение) и подсказывающее, чем и как лечить. Хакатон, Трек 3: «Компьютерное зрение в агрономии».

## Технологии

- **Backend:** Django, Django REST Framework
- **ML:** TensorFlow/Keras (MobileNetV3, transfer learning), обучена на датасете PlantVillage
- **Frontend:** Django-шаблоны, Tailwind CSS (через CDN)
- **База данных:** SQLite (по умолчанию)

## Требования

- Python 3.11–3.13
- Git
- ~2 ГБ свободного места (в основном под TensorFlow)

## Установка и запуск локально

### 1. Клонировать репозиторий

```bash
git clone <ссылка-на-репозиторий>
cd agritech-computer-vision-project
```

### 2. Создать и активировать виртуальное окружение

**Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Windows (Git Bash):**
```bash
python -m venv venv
source venv/Scripts/activate
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

После активации в начале строки терминала должно появиться `(venv)`.

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

Установка может занять несколько минут — `tensorflow-cpu` весит несколько сотен МБ.

Если `requirements.txt` в репозитории нет или устарел, эти пакеты обязательны:
```bash
pip install django djangorestframework tensorflow-cpu pillow gunicorn whitenoise python-dotenv
```

### 4. Создать файл `.env`

В корне проекта (рядом с `manage.py`) создать файл `.env`:

```
DEBUG=True
SECRET_KEY=django-insecure-вставь-сюда-свой-ключ
```

`SECRET_KEY` можно сгенерировать так:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Файл `.env` не должен попадать в git** — проверь, что он указан в `.gitignore`.

### 5. Проверить, что файлы ML-модели на месте

Убедиться, что в проекте присутствуют:
```
diagnosis/ml/plant_disease_model.keras
diagnosis/ml/class_names.json
```

Это обученные веса модели и список классов — без них диагностика не заработает (`FileNotFoundError` при первом запросе к `/diagnose/`). Если файлов нет в репозитории (например, исключены из git из-за размера) — их нужно получить отдельно и положить в `diagnosis/ml/`.

### 6. Применить миграции базы данных

```bash
python manage.py migrate
```

### 7. Загрузить справочник болезней и лечения (fixture)

```bash
python manage.py loaddata diagnosis/fixtures/treatments.json
```

Без этого шага диагностика будет возвращать `class_name`, но без описания болезни и рекомендаций по лечению.

### 8. (Опционально) Создать администратора

Нужен для входа в `/admin/` и редактирования справочника лечения:

```bash
python manage.py createsuperuser
```

### 9. Запустить сервер разработки

```bash
python manage.py runserver
```

Открыть в браузере: **http://127.0.0.1:8000/**

## Проверка, что всё работает

1. Открой главную страницу — должен отобразиться баннер с фото и текстом.
2. Зарегистрируй аккаунт (`/register/`) и войди (`/login/`).
3. Перейди на страницу диагностики (`/diagnose-page/`), загрузи фото листа томата/картофеля/перца.
4. Нажми «Диагностировать» — должен появиться результат с названием болезни, уверенностью модели, описанием и рекомендацией по лечению.

## Структура проекта

```
agritech-computer-vision-project/
├── manage.py
├── requirements.txt
├── build.sh                     # скрипт сборки для деплоя (Render)
├── .env                         # переменные окружения (не в git)
├── config/                      # настройки Django-проекта
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── diagnosis/                   # основное приложение
    ├── models.py                # модель TreatmentRecommendation
    ├── views.py                 # views + API-эндпоинт /diagnose/
    ├── urls.py
    ├── admin.py
    ├── ml/
    │   ├── predictor.py         # загрузка модели и инференс
    │   ├── plant_disease_model.keras
    │   └── class_names.json
    ├── fixtures/
    │   └── treatments.json      # справочник болезней/лечения
    ├── templates/diagnosis/     # HTML-шаблоны (Tailwind)
    └── static/diagnosis/        # статика (изображения)
```

## Основной API-эндпоинт

**`POST /diagnose/`**

Тип запроса: `multipart/form-data`, поле `image` — файл изображения.

Пример через curl:
```bash
curl -X POST http://127.0.0.1:8000/diagnose/ -F "image=@путь/к/фото.jpg"
```

Пример ответа:
```json
{
  "class_name": "Tomato_Late_blight",
  "confidence": 0.5691567063331604,
  "disease_name": "Фитофтороз томата (поздняя гниль)",
  "description": "...",
  "treatment": "...",
  "duration": "10-14 дней"
}
```

## Известные ограничения модели

- Модель обучена на **PlantVillage** — фото в лабораторных условиях (чистый фон, ровный свет). На проверке на независимом наборе «живых» фото (**PlantDoc**) точность заметно ниже (96% → ~21%) — так называемый *domain gap*. Подробнее и с графиком — в презентации проекта.
- Поддерживаются только 3 культуры: томат, картофель, перец (15 классов болезней/здоровых состояний).
- При низкой уверенности предсказания (`confidence` < ~0.5–0.6) стоит относиться к результату с осторожностью.

## Частые проблемы при локальном запуске

**`TemplateDoesNotExist`**
Проверь, что HTML-шаблоны лежат по пути `diagnosis/templates/diagnosis/<имя>.html` (папка `diagnosis` внутри `templates` — обязательна, это соглашение Django).

**`ModuleNotFoundError: No module named 'rest_framework'` (или другой пакет)**
Значит, команда запущена не из активированного `venv`. Проверь, что в начале строки терминала есть `(venv)`, и при необходимости активируй его заново (см. шаг 2).

**`TypeError: path should be path-like or io.BytesIO`**
Если этот код меняли — `predictor.py` должен приводить загруженный файл (`InMemoryUploadedFile`) к `io.BytesIO` перед передачей в `load_img()`.

**`UnicodeDecodeError` при `loaddata`**
Файл `fixtures/treatments.json` сохранён не в кодировке UTF-8. Пересоздать его через `dumpdata` с явным указанием `encoding="utf-8"` при записи.

**Долгая первая загрузка модели**
Это нормально — TensorFlow и веса модели загружаются в память при первом запросе к `/diagnose/` после старта сервера.

## Деплой

Проект настроен для деплоя на [Render](https://render.com) (`build.sh`, `gunicorn`, `whitenoise` для статики). 

---

**Команда:** SanaLab
