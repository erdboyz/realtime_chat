# Realtime Chat Application | Приложение для чата в реальном времени

[English](#english) | [Русский](#russian)

<a name="english"></a>
## English

A real-time messaging web application developed using the Flask framework. The application is at the final stage of development.

### Features

- Real-time messaging
- User authentication
- Chat rooms
- User profiles

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/your-username/realtime_chat.git
   cd realtime_chat
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

4. Configure environment variables(prodiction):
   Create a `.env` file in the root directory with the following variables:
   ```
   SECRET_KEY=your_secret_key
   DATABASE_URL=your_database
   ```

5. Run the application:
   ```
   python app.py
   ```

### Technologies Used

- Flask
- SQLAlchemy
- Flask-SocketIO
- HTML/CSS/JavaScript
- Bootstrap

### License

This project is licensed under the MIT License - see the LICENSE file for details.

---

<a name="russian"></a>
## Русский

Веб-приложение для обмена сообщениями в реальном времени, разработанное с использованием фреймворка Flask. Приложение находится на финальной стадии разработки.

### Возможности

- Обмен сообщениями в реальном времени
- Аутентификация пользователей
- Чат-комнаты
- Пользовательские профили

### Установка

1. Клонируйте репозиторий:
   ```
   git clone https://github.com/your-username/realtime_chat.git
   cd realtime_chat
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

4. Настройте переменные окружения(продакшн):
   Создайте файл `.env` в корневом каталоге со следующими переменными:
   ```
   SECRET_KEY=your_secret_key
   DATABASE_URL=your_database
   ```

5. Запустите приложение:
   ```
   python app.py
   ```

### Используемые технологии

- Flask
- SQLAlchemy
- Flask-SocketIO
- HTML/CSS/JavaScript
- Bootstrap

### Лицензия

Этот проект лицензирован под лицензией MIT - подробности см. в файле LICENSE. 