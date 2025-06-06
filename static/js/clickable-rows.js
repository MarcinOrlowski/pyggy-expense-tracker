document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.clickable-row').forEach(row => {
        row.addEventListener('click', function(e) {
            // Prevent row click when clicking action buttons, links, or form elements
            if (e.target.closest('.actions-column') || 
                e.target.closest('a') || 
                e.target.closest('button') ||
                e.target.closest('form')) {
                return;
            }
            
            const href = this.dataset.href;
            if (href) {
                window.location.href = href;
            }
        });
    });
});