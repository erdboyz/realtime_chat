# Swagram - Real-time Chat Application | Приложение для чата в реальном времени

[English](#english) | [Русский](#russian)

<a name="english"></a>
## English

A real-time messaging web application developed using the Flask framework. This application allows users to communicate in real-time, create profiles with avatars, and engage in group chats. The app includes encrypted private messaging for secure communication.

### Features

- Real-time messaging with instant delivery
- Encrypted private messages for secure communication
- User authentication system (registration/login)
- User profiles with customizable avatars
- Password management with secure hashing
- Drag-and-drop avatar uploads with preview
- Admin panel for user and chat management
- Responsive design that works on all devices
- Online user counter and status indicators
- Message timestamps and history
- Private messaging with read receipts

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/your-username/swagram.git
   cd swagram
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Configure environment variables (development):
   The app uses a SQLite database by default. For development, you can run without additional configuration.
   
   For production, create a `.env` file in the root directory with:
   ```
   SECRET_KEY=your_secret_key
   DATABASE_URL=your_database_url
   ```

5. Run database migrations (if needed):
   ```
   python -m database.run_migration --method standard --check
   ```

6. Run the application:
   ```
   python app.py
   ```
   
7. Access the application at:
   ```
   http://localhost:5000
   ```

### Project Structure

- `app.py` - Application entry point
- `config.py` - Configuration settings
- `routes.py` - Application routes and socket events
- `forms.py` - Form definitions and validation
- `database/` - Database related files
  - `database/models.py` - Database models
  - `database/migration.py` - Standard migration script
  - `database/alt_migration.py` - Alternative migration approach
  - `database/direct_sql.py` - Direct SQL migration method
  - `database/check_db.py` - Database status verification tool
  - `database/run_migration.py` - CLI interface for migrations
- `templates/` - HTML templates
- `static/` - Static files (CSS, JS, images)
  - `static/avatars/` - User avatar storage
  - `static/css/` - Stylesheets
  - `static/js/` - JavaScript files

### User Roles

- **Regular users**: Can register, login, edit their profile, upload avatars, and send messages
- **Admin users**: Have all regular user capabilities plus access to admin panel with user management and chat moderation

### Technologies Used

- **Backend**: Flask, Flask-SocketIO, Flask-Login, Flask-WTF, SQLAlchemy
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Real-time communication**: Socket.IO
- **Image processing**: Pillow
- **Encryption**: Cryptography library (Fernet)
- **Security**: Flask-Talisman, Bleach (content sanitization)

### License

This project is licensed under the MIT License - see the LICENSE file for details.

---

<a name="russian"></a>
## Русский

Веб-приложение для обмена сообщениями в реальном времени, разработанное с использованием фреймворка Flask. Это приложение позволяет пользователям общаться в реальном времени, создавать профили с аватарами и участвовать в групповых чатах. Приложение включает шифрование приватных сообщений для безопасной коммуникации.

### Возможности

- Обмен сообщениями в реальном времени с мгновенной доставкой
- Шифрование личных сообщений для безопасной коммуникации
- Система аутентификации пользователей (регистрация/вход)
- Пользовательские профили с настраиваемыми аватарами
- Управление паролями с безопасным хешированием
- Загрузка аватаров перетаскиванием с предпросмотром
- Панель администратора для управления пользователями и чатом
- Адаптивный дизайн, работающий на всех устройствах
- Счетчик пользователей онлайн и индикаторы статуса
- Временные метки сообщений и история
- Приватные сообщения с подтверждениями прочтения

### Установка

1. Клонируйте репозиторий:
   ```
   git clone https://github.com/your-username/swagram.git
   cd swagram
   ```

2. Создайте и активируйте виртуальное окружение:
   ```
   python -m venv venv
   # На Windows
   venv\Scripts\activate
   # На macOS/Linux
   source venv/bin/activate
   ```

3. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```

4. Настройте переменные окружения (разработка):
   По умолчанию приложение использует базу данных SQLite. Для разработки вы можете запустить без дополнительной конфигурации.
   
   Для продакшн создайте файл `.env` в корневом каталоге с:
   ```
   SECRET_KEY=your_secret_key
   DATABASE_URL=your_database_url
   ```

5. Запустите миграции базы данных (при необходимости):
   ```
   python -m database.run_migration --method standard --check
   ```

6. Запустите приложение:
   ```
   python app.py
   ```
   
7. Доступ к приложению по адресу:
   ```
   http://localhost:5000
   ```

### Структура проекта

- `app.py` - Точка входа в приложение
- `config.py` - Настройки конфигурации
- `routes.py` - Маршруты приложения и события сокетов
- `forms.py` - Определения форм и валидация
- `database/` - Файлы, связанные с базой данных
  - `database/models.py` - Модели базы данных
  - `database/migration.py` - Стандартный скрипт миграции
  - `database/alt_migration.py` - Альтернативный подход к миграции
  - `database/direct_sql.py` - Метод прямой SQL миграции
  - `database/check_db.py` - Инструмент проверки статуса базы данных
  - `database/run_migration.py` - CLI интерфейс для миграций
- `templates/` - HTML шаблоны
- `static/` - Статические файлы (CSS, JS, изображения)
  - `static/avatars/` - Хранилище аватаров пользователей
  - `static/css/` - Таблицы стилей
  - `static/js/` - JavaScript файлы

### Роли пользователей

- **Обычные пользователи**: Могут регистрироваться, входить в систему, редактировать свой профиль, загружать аватары и отправлять сообщения
- **Администраторы**: Имеют все возможности обычных пользователей плюс доступ к панели администратора с управлением пользователями и модерацией чата

### Используемые технологии

- **Backend**: Flask, Flask-SocketIO, Flask-Login, Flask-WTF, SQLAlchemy
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **База данных**: SQLite (разработка), PostgreSQL (готово к продакшн)
- **Коммуникация в реальном времени**: Socket.IO
- **Обработка изображений**: Pillow
- **Шифрование**: Библиотека Cryptography (Fernet)
- **Безопасность**: Flask-Talisman, Bleach (санитизация контента)

### Лицензия

Этот проект лицензирован под лицензией MIT - подробности см. в файле LICENSE. 