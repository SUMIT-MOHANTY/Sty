document.addEventListener('DOMContentLoaded', function() {
    // Add date formatting for all elements with data-format="date"
    document.querySelectorAll('[data-format="date"]').forEach(function(element) {
        const timestamp = element.textContent.trim();
        if (timestamp) {
            const date = new Date(timestamp);
            element.textContent = date.toLocaleDateString();
        }
    });

    // Add date and time formatting for all elements with data-format="datetime"
    document.querySelectorAll('[data-format="datetime"]').forEach(function(element) {
        const timestamp = element.textContent.trim();
        if (timestamp) {
            const date = new Date(timestamp);
            element.textContent = date.toLocaleString();
        }
    });
});
