// static/script.js

document.addEventListener('DOMContentLoaded', function() {
    const navbarLinks = document.querySelectorAll('.navbar-nav .nav-link'); // Semua link navigasi
    const sections = document.querySelectorAll('section[id]'); // Semua section yang punya ID (top, services-section, about-section)

    // Fungsi untuk menghapus kelas 'active' dari semua link
    function removeActiveClass() {
        navbarLinks.forEach(link => {
            link.classList.remove('active');
        });
    }

    // Fungsi untuk menambahkan kelas 'active' ke link yang sesuai
    function addActiveClass(id) {
        removeActiveClass(); // Hapus dulu semua yang aktif
        const activeLink = document.querySelector(`.navbar-nav .nav-link[href*="#${id}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
    }

    // Intersection Observer untuk mendeteksi section yang sedang terlihat
    // Ini akan mengaktifkan link navbar secara otomatis saat scroll
    const observerOptions = {
        root: null, // Mengamati viewport
        rootMargin: '0px',
        threshold: 0.3 // Mengaktifkan ketika 30% dari section terlihat
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Saat section masuk viewport, aktifkan link yang sesuai
                addActiveClass(entry.target.id);
            }
        });
    }, observerOptions);

    // Amati setiap section
    sections.forEach(section => {
        observer.observe(section);
    });

    // Event Listener untuk klik pada link navbar
    // Ini akan langsung mengaktifkan link dan melakukan smooth scroll
    navbarLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault(); // Mencegah perilaku default link (lompat cepat)

            const targetId = this.getAttribute('href').split('#')[1]; // Ambil ID dari href (misal: "top", "services-section")
            const targetElement = document.getElementById(targetId);

            if (targetElement) {
                // Aktifkan kelas 'active' di link yang diklik
                removeActiveClass();
                this.classList.add('active');

                // Lakukan smooth scroll
                window.scrollTo({
                    top: targetElement.offsetTop - 80, // Offset 80px agar tidak tertutup navbar fixed
                    behavior: 'smooth'
                });
            } else {
                // Jika ini link non-scroll (misal: Dashboard, Login, Register, Logout)
                // Biarkan Flask yang menanganinya, tapi tetap aktifkan link jika di halaman yang sama
                if (this.getAttribute('href').includes(window.location.pathname.split('/').pop())) {
                     removeActiveClass();
                     this.classList.add('active');
                }
                window.location.href = this.getAttribute('href'); // Lanjutkan ke halaman lain
            }
        });
    });

    // Logika untuk mengaktifkan link saat halaman dimuat atau di-refresh (berdasarkan URL hash)
    // Ini penting jika pengguna me-refresh halaman saat berada di #services-section misalnya
    const initialHash = window.location.hash.substring(1);
    if (initialHash) {
        addActiveClass(initialHash);
    } else {
        // Jika tidak ada hash, asumsikan di section 'top' atau paling atas
        addActiveClass('top');
    }
});