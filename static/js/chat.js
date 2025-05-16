document.addEventListener('DOMContentLoaded', function() {
    // Подключение к Socket.IO серверу
    const socket = io();
    
    // DOM элементы
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const messagesContainer = document.getElementById('messages');
    const onlineUsers = document.getElementById('online-users');
    
    // Find the username using multiple methods to ensure it works
    let currentUsername = '';
    
    // Method 1: From the avatar alt attribute
    const navAvatar = document.querySelector('.nav-avatar');
    if (navAvatar) {
        currentUsername = navAvatar.alt;
    }
    
    // Method 2: From any existing messages
    if (!currentUsername && messagesContainer) {
        const ownMessages = messagesContainer.querySelectorAll('.message-own');
        if (ownMessages.length > 0) {
            const usernameElement = ownMessages[0].querySelector('.message-username');
            if (usernameElement) {
                currentUsername = usernameElement.textContent.trim();
            }
        }
    }
    
    console.log('Current username detected:', currentUsername);
    
    // Проверка на существование элементов (только на странице чата)
    if (messageForm && messageInput && messagesContainer) {
        // Прокрутка чата вниз при загрузке
        scrollToBottom();
        
        // Make existing usernames clickable
        makeUsernamesClickable();
        
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
            setTimeout(function() {
                scrollToBottom();
                makeUsernamesClickable();
            }, 0);
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
        
        // Create avatar element
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        
        const avatarImg = document.createElement('img');
        avatarImg.src = `/static/avatars/${data.avatar || 'default_avatar.png'}`;
        avatarImg.alt = data.username;
        
        avatarDiv.appendChild(avatarImg);
        messageElement.appendChild(avatarDiv);
        
        // Create message content wrapper
        const contentWrapper = document.createElement('div');
        contentWrapper.className = 'message-content-wrapper';
        
        // Create the message bubble that contains all message elements
        const messageBubble = document.createElement('div');
        messageBubble.className = 'message-bubble';
        
        // Add username at the top
        const usernameDiv = document.createElement('div');
        usernameDiv.className = 'message-username';
        usernameDiv.textContent = data.username;
        usernameDiv.setAttribute('data-username', data.username);
        messageBubble.appendChild(usernameDiv);
        
        // Add message text
        const messageText = document.createElement('div');
        messageText.className = 'message-text';
        messageText.textContent = data.message;
        messageBubble.appendChild(messageText);
        
        // Add timestamp at the bottom
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = data.display_time || getCurrentTime();
        messageBubble.appendChild(timeDiv);
        
        // Add the bubble to the content wrapper
        contentWrapper.appendChild(messageBubble);
        
        // Add the content wrapper to the message element
        messageElement.appendChild(contentWrapper);
        
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
    
    // Make usernames clickable to view profiles
    function makeUsernamesClickable() {
        const usernameElements = document.querySelectorAll('.message-username');
        
        usernameElements.forEach(element => {
            // Skip if already processed
            if (element.getAttribute('data-processed') === 'true') {
                return;
            }
            
            const username = element.textContent.trim();
            
            // Skip making own username clickable
            if (username === currentUsername) {
                element.classList.add('message-username-own');
                element.setAttribute('data-processed', 'true');
                return;
            }
            
            element.classList.add('message-username-clickable');
            element.setAttribute('data-processed', 'true');
            
            element.addEventListener('click', function(e) {
                e.preventDefault();
                window.location.href = `/user/${username}`;
            });
        });
    }
});