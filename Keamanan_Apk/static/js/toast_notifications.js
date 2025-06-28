// static/js/toast_notifications.js

document.addEventListener('DOMContentLoaded', function() {
    const flashMessagesContainer = document.getElementById('flash-messages-data');
    const toastContainer = document.getElementById('toast-notification-container');

    if (flashMessagesContainer && toastContainer) {
        const flashMessages = flashMessagesContainer.querySelectorAll('.flash-message');

        flashMessages.forEach(messageElement => {
            const messageText = messageElement.dataset.message;
            const messageCategory = messageElement.dataset.category;

            if (messageText) {
                // Buat elemen toast baru
                const toastDiv = document.createElement('div');
                toastDiv.classList.add('custom-toast-notification');
                if (messageCategory) {
                    toastDiv.classList.add(messageCategory); // Tambah kelas untuk styling kategori
                }

                // Tambahkan ikon berdasarkan kategori
                let iconHtml = '';
                switch (messageCategory) {
                    case 'success':
                        iconHtml = '<i class="fas fa-check-circle toast-icon" style="color:#008000;"></i>';
                        break;
                    case 'error':
                        iconHtml = '<i class="fas fa-times-circle toast-icon" style="color:#8B0000;"></i>';
                        break;
                    case 'info':
                        iconHtml = '<i class="fas fa-info-circle toast-icon" style="color:#0056b3;"></i>';
                        break;
                    case 'warning':
                        iconHtml = '<i class="fas fa-exclamation-triangle toast-icon" style="color:#8B4513;"></i>';
                        break;
                    default:
                        iconHtml = '<i class="fas fa-bell toast-icon" style="color:var(--dm-light-gray);"></i>'; // Default bell icon
                }

                toastDiv.innerHTML = `${iconHtml}<span>${messageText}</span>`;
                
                // Tambahkan toast ke container
                toastContainer.appendChild(toastDiv);

                // Hapus toast setelah 3 detik (total animasi 3 detik, fadeOut dimulai di 2.5s)
                setTimeout(() => {
                    toastDiv.remove(); // Hapus elemen dari DOM
                }, 5000); // 3000ms = 3 detik
            }
        });
    }
});
