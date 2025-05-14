# Swagram - Real-time Chat Application | Приложение для чата в реальном времени

[English](#english) | [Русский](#russian)

<a name="english"></a>
## English

A real-time messaging web application developed using the Flask framework. This application allows users to communicate in real-time, create profiles with avatars, and engage in group chats.

### Features

- Real-time messaging with instant delivery
- User authentication system (registration/login)
- User profiles with customizable avatars
- Password management with secure hashing
- Drag-and-drop avatar uploads with preview
- Admin panel for user and chat management
- Responsive design that works on all devices
- Online user counter
- Message timestamps and history

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

5. Run the application:
   ```
   python app.py
   ```
   
6. Access the application at:
   ```
   http://localhost:5000
   ```

### Project Structure

- `app.py` - Application entry point
- `models.py` - Database models
- `routes.py` - Application routes and socket events
- `forms.py` - Form definitions and validation
- `config.py` - Configuration settings
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

### Screenshots

(Add screenshots of your application here)

### License

This project is licensed under the MIT License - see the LICENSE file for details.

---

<a name="russian"></a>
## Русский

Веб-приложение для обмена сообщениями в реальном времени, разработанное с использованием фреймворка Flask. Это приложение позволяет пользователям общаться в реальном времени, создавать профили с аватарами и участвовать в групповых чатах.

### Возможности

- Обмен сообщениями в реальном времени с мгновенной доставкой
- Система аутентификации пользователей (регистрация/вход)
- Пользовательские профили с настраиваемыми аватарами
- Управление паролями с безопасным хешированием
- Загрузка аватаров перетаскиванием с предпросмотром
- Панель администратора для управления пользователями и чатом
- Адаптивный дизайн, работающий на всех устройствах
- Счетчик пользователей онлайн
- Временные метки сообщений и история

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

5. Запустите приложение:
   ```
   python app.py
   ```
   
6. Доступ к приложению по адресу:
   ```
   http://localhost:5000
   ```

### Структура проекта

- `app.py` - Точка входа в приложение
- `models.py` - Модели базы данных
- `routes.py` - Маршруты приложения и события сокетов
- `forms.py` - Определения форм и валидация
- `config.py` - Настройки конфигурации
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

### Скриншоты

(Добавьте скриншоты вашего приложения здесь)

### Лицензия

Этот проект лицензирован под лицензией MIT - подробности см. в файле LICENSE. 