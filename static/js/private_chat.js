document.addEventListener('DOMContentLoaded', function() {
    // Connect to socket.io
    const socket = io();
    
    // DOM elements
    const messageForm = document.getElementById('private-message-form');
    const messageInput = document.getElementById('private-message-input');
    const messagesContainer = document.getElementById('private-messages');
    const recipientIdInput = document.getElementById('recipient-id');
    const otherUserAvatarContainer = document.getElementById('other-user-avatar-container');
    
    // Get recipient ID from the hidden input
    const recipientId = recipientIdInput ? recipientIdInput.value : null;
    
    // Track online status of the other user
    let isOtherUserOnline = false;
    
    // Initialize the chat
    if (messageForm && messageInput && messagesContainer && recipientId) {
        // Scroll to bottom of chat
        scrollToBottom();
        
        // Listen for online users updates
        socket.on('online_users', function(data) {
            if (data.user_ids && data.user_ids.length > 0) {
                const onlineUserIds = data.user_ids.map(id => parseInt(id));
                isOtherUserOnline = onlineUserIds.includes(parseInt(recipientId));
                updateOtherUserOnlineStatus();
            }
        });
        
        // Request current online users when connecting
        socket.on('connect', function() {
            socket.emit('request_online_users');
        });
        
        // Listen for user connection events
        socket.on('user_connected', function(data) {
            if (data.user_id && parseInt(data.user_id) === parseInt(recipientId)) {
                isOtherUserOnline = true;
                updateOtherUserOnlineStatus();
            }
        });
        
        // Listen for user disconnection events
        socket.on('user_disconnected', function(data) {
            if (data.user_id && parseInt(data.user_id) === parseInt(recipientId)) {
                isOtherUserOnline = false;
                updateOtherUserOnlineStatus();
            }
        });
        
        // Handle form submission
        messageForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const message = messageInput.value.trim();
            if (message) {
                socket.emit('send_private_message', { 
                    message: message, 
                    recipient_id: recipientId 
                });
                messageInput.value = '';
                messageInput.focus();
            }
        });
        
        // Listen for private messages
        socket.on('receive_private_message', function(data) {
            // Only add message if it's part of this conversation
            if (data.sender_id == recipientId || 
               (data.recipient_id == recipientId && data.sender_id != recipientId)) {
                
                // Process the message first if it's encrypted
                if (window.messageEncryption && window.messageEncryption.isEncrypted(data)) {
                    data = window.messageEncryption.processReceivedMessage(data);
                }
                
                addMessage(data);
                
                // Mark as read if we are the recipient
                if (data.sender_id == recipientId) {
                    socket.emit('mark_message_read', { message_id: data.message_id });
                }
                
                // Scroll to bottom
                setTimeout(scrollToBottom, 0);
            }
        });
        
        // Listen for message read status updates
        socket.on('message_read_status', function(data) {
            if (data.message_ids && data.message_ids.length > 0) {
                // Update all messages that have been read
                data.message_ids.forEach(function(messageId) {
                    const messageEl = document.querySelector(`.message[data-message-id="${messageId}"]`);
                    if (messageEl) {
                        const statusEl = messageEl.querySelector('.message-status');
                        if (statusEl) {
                            statusEl.classList.remove('message-status-delivered');
                            statusEl.classList.add('message-status-read');
                            statusEl.innerHTML = '<i class="fas fa-check"></i><i class="fas fa-check"></i>';
                        }
                    }
                });
            }
        });
    } else {
        // If we're not on the chat page, listen for new messages to show notifications
        socket.on('receive_private_message', function(data) {
            updateMessageNotification();
            
            // Emit event for conversations page to update counters in real-time
            if (data.sender_id) {
                // Use a delay to ensure event propagation
                setTimeout(function() {
                    socket.emit('new_private_message', { sender_id: data.sender_id });
                }, 100);
            }
        });
    }
    
    // Function to update the other user's online status display
    function updateOtherUserOnlineStatus() {
        if (otherUserAvatarContainer) {
            if (isOtherUserOnline) {
                otherUserAvatarContainer.classList.add('online');
            } else {
                otherUserAvatarContainer.classList.remove('online');
            }
        }
    }
    
    // Update the messages tab notification if we have any unread messages
    function updateMessageNotification() {
        const messagesNavLink = document.querySelector('.nav-link[href*="conversations"]');
        if (messagesNavLink) {
            // Add animation class
            messagesNavLink.classList.add('has-new-messages');
            
            // Find or create the badge
            let badge = messagesNavLink.querySelector('.badge');
            if (!badge) {
                // Create a new badge
                badge = document.createElement('span');
                badge.className = 'badge rounded-pill bg-danger ms-1';
                badge.textContent = '1';
                messagesNavLink.appendChild(badge);
            } else {
                // Increment existing badge
                let count = parseInt(badge.textContent.replace('+', '')) || 0;
                count++;
                
                // Limit display to "9+" for counts greater than 9
                badge.textContent = count > 9 ? '9+' : count.toString();
            }
        }
    }
    
    // Function to add a message to the chat
    function addMessage(data) {
        const isOwnMessage = data.sender_id != recipientId;
        
        const messageElement = document.createElement('div');
        messageElement.className = `message ${isOwnMessage ? 'message-own' : 'message-other'}`;
        messageElement.setAttribute('data-message-id', data.message_id);
        
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
        
        // Create message bubble
        const messageBubble = document.createElement('div');
        messageBubble.className = 'message-bubble';
        
        // Format message text with encryption information if enabled
        const isEncrypted = window.messageEncryption && window.messageEncryption.isEncrypted(data);
        const messageContent = window.messageEncryption && isEncrypted 
            ? window.messageEncryption.formatMessage(data.message, isEncrypted)
            : data.message;
        
        // Add message text
        const messageText = document.createElement('div');
        messageText.className = 'message-text';
        messageText.textContent = messageContent;
        messageBubble.appendChild(messageText);
        
        // Create message footer for time and status
        const messageFooter = document.createElement('div');
        messageFooter.className = 'message-footer';
        
        // Add time
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = data.display_time || getCurrentTime();
        messageFooter.appendChild(timeDiv);
        
        // Add message status if it's our own message
        if (isOwnMessage) {
            const statusDiv = document.createElement('div');
            statusDiv.className = `message-status ${data.is_read ? 'message-status-read' : 'message-status-delivered'}`;
            
            if (data.is_read) {
                statusDiv.innerHTML = '<i class="fas fa-check"></i><i class="fas fa-check"></i>';
            } else {
                statusDiv.innerHTML = '<i class="fas fa-check"></i>';
            }
            
            messageFooter.appendChild(statusDiv);
        }
        
        // Add encryption indicator if encryption helper is available
        if (window.messageEncryption) {
            window.messageEncryption.updateEncryptionStatus(messageElement, isEncrypted);
        }
        
        messageBubble.appendChild(messageFooter);
        contentWrapper.appendChild(messageBubble);
        messageElement.appendChild(contentWrapper);
        
        messagesContainer.appendChild(messageElement);
    }
    
    // Function to get current time in HH:MM format
    function getCurrentTime() {
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        return `${hours}:${minutes}`;
    }
    
    // Function to scroll to the bottom of the chat
    function scrollToBottom() {
        if (messagesContainer) {
            // Force a reflow to ensure scrollHeight is accurate
            void messagesContainer.offsetHeight;
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }
}); 