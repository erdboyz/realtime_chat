document.addEventListener('DOMContentLoaded', function() {
    // Connect to socket.io
    const socket = io();
    
    // Track online users
    const onlineUsers = new Set();
    
    // Get all user status indicators
    const userStatusIndicators = document.querySelectorAll('.user-status-indicator');
    
    // Listen for online users updates
    socket.on('online_users', function(data) {
        // Clear current set and update with new data
        onlineUsers.clear();
        if (data.user_ids && data.user_ids.length > 0) {
            data.user_ids.forEach(id => onlineUsers.add(parseInt(id)));
        }
        
        // Update status indicators
        updateOnlineStatus();
    });
    
    // Request current online users when connecting
    socket.on('connect', function() {
        socket.emit('request_online_users');
    });
    
    // Listen for user connection events
    socket.on('user_connected', function(data) {
        if (data.user_id) {
            onlineUsers.add(parseInt(data.user_id));
            updateOnlineStatus();
        }
    });
    
    // Listen for user disconnection events
    socket.on('user_disconnected', function(data) {
        if (data.user_id) {
            onlineUsers.delete(parseInt(data.user_id));
            updateOnlineStatus();
        }
    });
    
    // Listen for new private messages
    socket.on('new_private_message', function(data) {
        if (data.sender_id) {
            updateConversationUnreadCount(parseInt(data.sender_id));
            updateNavbarCounter();
        }
    });
    
    // Function to update message counter for a specific conversation
    function updateConversationUnreadCount(userId) {
        // Find the conversation item
        const conversationItem = document.querySelector(`.conversation-item[data-conversation-id="${userId}"]`);
        if (!conversationItem) return;
        
        // Find conversation preview element
        const conversationPreview = conversationItem.querySelector('.conversation-preview');
        if (!conversationPreview) return;
        
        // Find or create the message counter
        let counterBadge = conversationItem.querySelector(`.message-counter[data-user-id="${userId}"]`);
        
        if (!counterBadge) {
            // No existing counter - clear the preview and add counter
            conversationPreview.innerHTML = '';
            
            // Create new badge
            counterBadge = document.createElement('span');
            counterBadge.className = 'badge rounded-pill bg-primary message-counter';
            counterBadge.setAttribute('data-user-id', userId);
            counterBadge.textContent = '1';
            
            // Add to preview
            conversationPreview.appendChild(counterBadge);
            
            // Add unread class to conversation item
            conversationItem.classList.add('unread');
        } else {
            // Increment existing counter
            let count = parseInt(counterBadge.textContent) || 0;
            count++;
            
            // Limit display to "9+" for counts greater than 9
            counterBadge.textContent = count > 9 ? '9+' : count.toString();
        }
        
        // Move conversation to top of list
        const parentList = conversationItem.parentNode;
        if (parentList) {
            parentList.insertBefore(conversationItem, parentList.firstChild);
        }
    }
    
    // Function to update the counter in the navbar
    function updateNavbarCounter() {
        const messagesNavLink = document.querySelector('.nav-link[href*="conversations"]');
        if (!messagesNavLink) return;
        
        // Add the 'has-new-messages' class to animate the icon
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
    
    // Function to update all online status indicators
    function updateOnlineStatus() {
        // Update status indicators
        userStatusIndicators.forEach(indicator => {
            const userId = parseInt(indicator.getAttribute('data-user-id'));
            if (onlineUsers.has(userId)) {
                indicator.classList.add('user-status-online');
                indicator.classList.remove('user-status-offline');
            } else {
                indicator.classList.remove('user-status-online');
                indicator.classList.add('user-status-offline');
            }
        });
    }
    
    // Initialize all status indicators as offline
    userStatusIndicators.forEach(indicator => {
        indicator.classList.add('user-status-offline');
    });
}); 