// static/sidebar.js

document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('main-sidebar');
    if (!sidebar) return; // Keluar jika elemen sidebar tidak ada di halaman ini

    const sidebarToggleBtn = document.getElementById('sidebar-toggle');
    const sidebarNavLinks = sidebar.querySelectorAll('.sidebar-nav-link');
    const sidebarActiveIndicator = document.getElementById('sidebar-active-indicator');
    
    let isSidebarExpanded = false; // Status sidebar: true = meluas, false = menyusut

    // --- Fungsi untuk Menggerakkan Indikator Aktif pada Sidebar ---
    function updateSidebarActiveIndicator(targetLink = null) {
        let linkToActivate = null;

        // Reset semua gaya inline dari link sidebar
        sidebarNavLinks.forEach(link => {
            link.classList.remove('active');
            link.style.backgroundColor = '';
            link.style.borderColor = '';
            link.style.boxShadow = '';
            link.style.transform = '';
            link.style.color = '';
        });

        if (targetLink) {
            linkToActivate = targetLink;
        } else {
            // Tentukan link aktif berdasarkan pathname saat ini
            const currentPathname = window.location.pathname;
            sidebarNavLinks.forEach(link => {
                const linkHref = link.getAttribute('href').split('?')[0]; // Hapus query params

                // Aktifkan link jika pathname saat ini mengandung href dari link sidebar
                // Contoh: /dashboard cocok dengan /dashboard
                // Handle khusus untuk link Home di sidebar jika dia menuju '/'
                if (linkHref === url_for_js('home').split('?')[0] && (currentPathname === '/' || currentPathname === '/home')) {
                    linkToActivate = link;
                } else if (currentPathname.includes(linkHref) && linkHref !== url_for_js('home').split('?')[0]) {
                    linkToActivate = link;
                }
            });
        }

        // Pindahkan indikator jika ada link aktif yang teridentifikasi
        if (linkToActivate) {
            const navRect = linkToActivate.closest('.sidebar-nav').getBoundingClientRect();
            const linkRect = linkToActivate.getBoundingClientRect();

            sidebarActiveIndicator.style.left = `${linkRect.left - navRect.left}px`;
            sidebarActiveIndicator.style.top = `${linkRect.top - navRect.top}px`;
            sidebarActiveIndicator.style.width = `${linkRect.width}px`;
            sidebarActiveIndicator.style.height = `${linkRect.height}px`;

            sidebarActiveIndicator.classList.add('visible');
            sidebarActiveIndicator.style.opacity = '1';

            linkToActivate.classList.add('active'); // Set active class pada link
        } else {
            sidebarActiveIndicator.classList.remove('visible');
            sidebarActiveIndicator.style.opacity = '0';
        }
    }

    // Fungsi untuk mengelola lebar konten utama saat sidebar berubah
    function updateMainContentMargin() {
        const mainContentArea = document.querySelector('.main-content-area');
        if (mainContentArea) {
            // Periksa apakah sidebar sedang dalam mode 'expanded' (diklik) atau 'hover-expanded' (hover)
            if (sidebar.classList.contains('expanded') || sidebar.classList.contains('hover-expanded')) {
                document.body.classList.add('body-sidebar-expanded');
            } else {
                document.body.classList.remove('body-sidebar-expanded');
            }
        }
    }

    // === Event Listeners Sidebar ===
    // Toggle sidebar saat tombol diklik
    sidebarToggleBtn.addEventListener('click', function() {
        isSidebarExpanded = !isSidebarExpanded;
        sidebar.classList.toggle('expanded', isSidebarExpanded);
        sidebar.classList.remove('hover-expanded'); // Hapus hover jika diklik
        updateMainContentMargin();
        updateSidebarActiveIndicator(null); // Recalculate indicator position after expand/collapse
    });

    // Event listener untuk hover pada sidebar
    sidebar.addEventListener('mouseenter', function() {
        if (!isSidebarExpanded) { // Hanya meluas saat hover jika tidak dikunci expand
            sidebar.classList.add('hover-expanded');
            updateMainContentMargin();
            updateSidebarActiveIndicator(null); // Recalculate indicator position
        }
    });

    sidebar.addEventListener('mouseleave', function() {
        if (!isSidebarExpanded) { // Hanya menyusut saat mouse leave jika tidak dikunci expand
            sidebar.classList.remove('hover-expanded');
            updateMainContentMargin();
            updateSidebarActiveIndicator(null); // Recalculate indicator position
        }
    });
    
    // Handle klik pada link sidebar
    sidebarNavLinks.forEach(link => {
        link.addEventListener('click', function() {
            updateSidebarActiveIndicator(this); // Langsung update indicator saat link sidebar diklik
            // Tidak perlu delay untuk navigasi halaman, biarkan browser menavigasi
        });

        // Handle hover untuk indikator sidebar
        link.addEventListener('mouseenter', function() {
            updateSidebarActiveIndicator(this);
        });
        link.addEventListener('mouseleave', function() {
            updateSidebarActiveIndicator(null); // Kembali ke aktif by URL
        });
    });

    // === Inisialisasi Sidebar Saat Halaman Dimuat ===
    setTimeout(() => {
        updateMainContentMargin();
        updateSidebarActiveIndicator(null); // Set indikator aktif saat load
    }, 100);

    // === Resize Listener ===
    window.addEventListener('resize', () => {
        updateMainContentMargin();
        updateSidebarActiveIndicator(null);
    });

    // Helper function (must be defined or globally available if not imported)
    // This is a simplified version; in a real Flask app, you'd generate URLs via Jinja or a global JS object
    function url_for_js(endpoint) {
        // This is a placeholder. In a real app, you'd pass a JS object with Flask URLs.
        // For current setup, we assume it's like Flask's url_for for simplicity.
        if (endpoint === 'home') return '/';
        if (endpoint === 'dashboard') return '/dashboard';
        if (endpoint === 'admin_panel') return '/admin_panel';
        if (endpoint === 'services') return '/services';
        if (endpoint === 'about') return '/about';
        if (endpoint === 'login') return '/login';
        if (endpoint === 'register') return '/register';
        if (endpoint === 'logout') return '/logout';
        // Add more endpoints as needed for sidebar links
        return `/${endpoint}`; // Generic fallback
    }
});