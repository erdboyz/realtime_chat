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