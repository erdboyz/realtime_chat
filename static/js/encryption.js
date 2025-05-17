/**
 * Client-side encryption helper
 * Note: This is for demonstration purposes only.
 * The real encryption happens on the server in this implementation.
 */
class MessageEncryption {
    constructor() {
        console.log("Message encryption initialized");
        this.encryptionEnabled = true;
    }

    /**
     * Check if a message is encrypted
     * @param {Object} messageData - The message data object
     * @returns {Boolean} - True if the message is encrypted
     */
    isEncrypted(messageData) {
        return messageData && messageData.is_encrypted === true;
    }

    /**
     * Display encryption status in the UI
     * @param {HTMLElement} messageElement - The message element to update
     * @param {Boolean} isEncrypted - Whether the message is encrypted
     */
    updateEncryptionStatus(messageElement, isEncrypted) {
        if (!messageElement) return;
        
        const encryptionIndicator = document.createElement('div');
        encryptionIndicator.className = 'encryption-indicator';
        encryptionIndicator.innerHTML = isEncrypted 
            ? '<i class="fas fa-lock" title="Зашифровано"></i>' 
            : '<i class="fas fa-lock-open" title="Не зашифровано"></i>';
        
        // Add to the message element
        const footer = messageElement.querySelector('.message-footer');
        if (footer) {
            footer.appendChild(encryptionIndicator);
        }
    }

    /**
     * Format a message with encryption information
     * @param {String} message - The message text
     * @param {Boolean} isEncrypted - Whether the message is encrypted
     * @returns {String} - Formatted message
     */
    formatMessage(message, isEncrypted) {
        if (!message) return '';
        
        // Handle error messages from the server
        if (message === "[Зашифрованное сообщение]") {
            return "🔒 [Зашифрованное сообщение]";
        }
        
        return message;
    }
    
    /**
     * Pre-process a received message before displaying
     * @param {Object} data - Message data
     * @returns {Object} - Processed message data
     */
    processReceivedMessage(data) {
        // Messages are now sent pre-decrypted from the server
        return data;
    }
}

// Initialize encryption when document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Create global encryption helper
    window.messageEncryption = new MessageEncryption();
}); 