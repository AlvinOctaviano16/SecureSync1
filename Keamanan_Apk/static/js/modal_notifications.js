// static/js/modal_notifications.js

document.addEventListener('DOMContentLoaded', function() {
    // Cari container flash messages yang disembunyikan
    const flashMessagesContainer = document.getElementById('flash-messages-data');

    if (flashMessagesContainer) {
        const flashMessages = flashMessagesContainer.querySelectorAll('.flash-message');

        // Jika ada pesan flash
        if (flashMessages.length > 0) {
            // Ambil modal element
            const notificationModal = document.getElementById('notificationModal');
            const notificationMessage = document.getElementById('notificationMessage');
            const modalContent = notificationModal.querySelector('.custom-modal-content');

            // Ambil pesan pertama (biasanya hanya ada satu pesan flash pada satu waktu)
            const messageElement = flashMessages[0];
            const messageText = messageElement.dataset.message;
            const messageCategory = messageElement.dataset.category;

            // Setel pesan ke dalam modal body
            notificationMessage.textContent = messageText;

            // Tambahkan kelas kategori ke modal content untuk styling berdasarkan jenis notifikasi (sukses, error, dll.)
            // Hapus kelas kategori sebelumnya jika ada
            modalContent.classList.remove('success', 'error', 'info', 'warning');
            if (messageCategory) {
                modalContent.classList.add(messageCategory);
            }

            // Tampilkan modal
            const myModal = new bootstrap.Modal(notificationModal);
            myModal.show();
        }
    }
});
