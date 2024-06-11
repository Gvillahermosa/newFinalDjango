document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelectorAll('.message');
    messages.forEach((message, index) => {
        setTimeout(() => {
            message.classList.add('show');
        }, index * 500);  // Adjust the delay as needed
    });
});