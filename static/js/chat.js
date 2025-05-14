document.addEventListener('DOMContentLoaded', function() {
    // Подключение к Socket.IO серверу
    const socket = io();
    
    // DOM элементы
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const messagesContainer = document.getElementById('messages');
    const onlineUsers = document.getElementById('online-users');
    
    // Get current username from the navbar
    const currentUsername = document.querySelector('.nav-link i.fas.fa-user-circle')?.parentElement?.textContent.trim().replace('Привет, ', '').replace('!', '') || '';
    
    // Проверка на существование элементов (только на странице чата)
    if (messageForm && messageInput && messagesContainer) {
        // Прокрутка чата вниз при загрузке
        scrollToBottom();
        
        // Обработка отправки сообщения
        messageForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const message = messageInput.value.trim();
            if (message) {
                socket.emit('send_message', { message: message });
                messageInput.value = '';
                messageInput.focus();
            }
        });
        
        // Получение сообщения от сервера
        socket.on('receive_message', function(data) {
            addMessage(data);
            // Ensure scrolling happens after DOM update
            setTimeout(scrollToBottom, 0);
        });
        
        // Отслеживание подключенных пользователей
        socket.on('user_count', function(data) {
            if(onlineUsers) {
                onlineUsers.textContent = data.count;
            }
        });

        // Handle chat clearing from admin
        socket.on('clear_chat', function() {
            // Clear all messages from the container
            if (messagesContainer) {
                messagesContainer.innerHTML = '';
            }
        });

        // Request current user count when connecting
        socket.on('connect', function() {
            // The server will automatically send the user count 
            // when a new user connects
        });

        // Ensure scroll works when window is resized
        window.addEventListener('resize', scrollToBottom);
    }
    
    // Функция для добавления сообщения в чат
    function addMessage(data) {
        // Determine if this is the user's own message
        const isOwnMessage = data.username === currentUsername;
        
        const messageElement = document.createElement('div');
        messageElement.className = `message ${isOwnMessage ? 'message-own' : 'message-other'}`;
        
        const messageHeader = document.createElement('div');
        messageHeader.className = 'message-header';
        
        const usernameSpan = document.createElement('span');
        usernameSpan.className = 'message-username';
        usernameSpan.textContent = data.username;
        
        const timeSpan = document.createElement('span');
        timeSpan.className = 'message-time';
        timeSpan.textContent = data.display_time || getCurrentTime();
        
        messageHeader.appendChild(usernameSpan);
        messageHeader.appendChild(timeSpan);
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = data.message;
        
        messageElement.appendChild(messageHeader);
        messageElement.appendChild(messageContent);
        
        messagesContainer.appendChild(messageElement);
    }
    
    // Get current time in HH:MM format as fallback
    function getCurrentTime() {
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        return `${hours}:${minutes}`;
    }
    
    // Прокрутка до последнего сообщения
    function scrollToBottom() {
        if (messagesContainer) {
            // Force a reflow to ensure scrollHeight is accurate
            void messagesContainer.offsetHeight;
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }
});