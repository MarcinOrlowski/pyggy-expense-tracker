/**
 * Flash messages functionality
 * Handles close button functionality for Django messages
 */
document.addEventListener('DOMContentLoaded', function() {
    // Add click event listeners to all message close buttons
    const closeButtons = document.querySelectorAll('.message-close');
    
    closeButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const messageElement = this.closest('.message');
            if (messageElement) {
                // Add fade-out animation
                messageElement.style.opacity = '0';
                messageElement.style.transform = 'translateY(-10px)';
                
                // Remove the message after animation completes
                setTimeout(function() {
                    messageElement.remove();
                    
                    // If this was the last message, remove the messages container
                    const messagesContainer = document.querySelector('.messages');
                    if (messagesContainer && messagesContainer.children.length === 0) {
                        messagesContainer.remove();
                    }
                }, 300);
            }
        });
    });
    
    // Add keyboard support for accessibility
    closeButtons.forEach(function(button) {
        button.addEventListener('keydown', function(event) {
            // Trigger close on Enter or Space
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                this.click();
            }
        });
    });
});