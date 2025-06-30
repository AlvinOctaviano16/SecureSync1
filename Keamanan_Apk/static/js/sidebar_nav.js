// static/js/sidebar_nav.js

document.addEventListener('DOMContentLoaded', function() {
    // #1: Mengambil elemen sidebar dengan ID yang benar dari HTML
    const sidebar = document.getElementById('sidebar');
    // Hanya jalankan logika ini jika elemen sidebar ada di halaman
    if (!sidebar) return; 

    const sidebarToggleBtn = document.getElementById('sidebar-toggle');
    // #2: Mengambil semua link dengan kelas yang benar
    const sidebarNavLinks = sidebar.querySelectorAll('.nav-link');
    // #3: Mengambil indikator yang sudah ditambahkan di HTML
    const sidebarActiveIndicator = document.getElementById('sidebar-active-indicator');
    
    // #6: Status awal sidebar adalah meluas (expanded) sesuai dengan CSS default-nya.
    let isSidebarExpanded = true;

    // --- Fungsi untuk Menggerakkan Indikator Aktif pada Sidebar ---
    function updateSidebarActiveIndicator(targetLink = null) {
        // #3: Tambahkan pengecekan null untuk indikator untuk menghindari error jika elemen tidak ditemukan.
        if (!sidebarActiveIndicator) {
            console.warn('Sidebar active indicator element not found.');
            return; 
        }

        let linkToActivate = null;
        let foundMatch = false;

        // Reset semua gaya inline dari link sidebar
        sidebarNavLinks.forEach(link => {
            link.classList.remove('active');
            link.style.backgroundColor = '';
            link.style.borderColor = '';
            link.style.boxShadow = '';
            link.style.transform = '';
            link.style.color = '';
        });

        if (targetLink) { // Jika targetLink diberikan (dari klik/hover)
            linkToActivate = targetLink;
        } else { // Jika tidak ada target, tentukan dari URL pathname
            const currentPathname = window.location.pathname;

            // #8: LOGIKA BARU untuk halaman detail dan dinamis
            // Jika pathname dimulai dengan /todo/detail, aktifkan link "To-Do List Saya"
            if (currentPathname.startsWith('/todo/detail/')) {
                linkToActivate = document.querySelector('.nav-link[href*="/my_todo_lists"]');
                foundMatch = true;
            } 
            // Jika pathname dimulai dengan /share, aktifkan link "Dibagikan ke Saya"
            else if (currentPathname.startsWith('/share/')) {
                linkToActivate = document.querySelector('.nav-link[href*="/shared_todo_lists"]');
                foundMatch = true;
            }
            // Jika pathname dimulai dengan /admin/reset, aktifkan link "Admin Panel"
            else if (currentPathname.startsWith('/admin/reset')) {
                linkToActivate = document.querySelector('.nav-link[href*="/admin_panel"]');
                foundMatch = true;
            }
            // #2: LOGIKA LAMA untuk halaman statis
            if (!foundMatch) {
                sidebarNavLinks.forEach(link => {
                    const linkHref = link.getAttribute('href').split('?')[0];
                    if (currentPathname.includes(linkHref) && linkHref !== '/') {
                        linkToActivate = link;
                    }
                });
            }

            // Fallback untuk dashboard jika tidak ada link lain yang cocok
            if (!linkToActivate && currentPathname === url_for_js('dashboard')) {
                linkToActivate = document.querySelector('.nav-link[href*="/dashboard"]');
            }
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
    if (sidebarToggleBtn) {
        sidebarToggleBtn.addEventListener('click', function() {
            isSidebarExpanded = !isSidebarExpanded;
            // #7: Ganti 'expanded' menjadi 'collapsed' untuk menyesuaikan dengan CSS, dan balikkan logikanya
            sidebar.classList.toggle('collapsed', !isSidebarExpanded);
            sidebar.classList.remove('hover-expanded'); // Hapus kelas hover
            updateMainContentMargin();
            updateSidebarActiveIndicator(null); // Recalculate indicator position after expand/collapse
        });
    }

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
        link.addEventListener('click', function(event) {
            // #4: Ganti panggilan fungsi yang hilang (setNavLinkActiveState) dengan fungsi yang ada
            updateSidebarActiveIndicator(this);
        });

        // Handle hover untuk indikator sidebar
        link.addEventListener('mouseenter', function() {
            // Indikator bergerak saat hover hanya jika sidebar tidak dikunci expanded
            if (!isSidebarExpanded) {
                // #4: Ganti panggilan fungsi yang hilang dengan fungsi yang ada
                updateSidebarActiveIndicator(this);
            }
        });
        link.addEventListener('mouseleave', function() {
            // Kembali ke aktif by URL saat mouse leave
            if (!isSidebarExpanded) {
                // #4: Ganti panggilan fungsi yang hilang dengan fungsi yang ada
                updateSidebarActiveIndicator(null);
            }
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

    // Helper function (placeholder untuk Flask url_for di JS)
    // #9: Hapus endpoint home, dashboard, services, dan about
    function url_for_js(endpoint) {
        if (endpoint === 'admin_panel') return '/admin_panel';
        if (endpoint === 'login') return '/login';
        if (endpoint === 'register') return '/register';
        if (endpoint === 'logout') return '/logout';
        // Tambahkan endpoint lain jika diperlukan
        if (endpoint === 'my_todo_lists') return '/my_todo_lists';
        if (endpoint === 'shared_todo_lists') return '/shared_todo_lists';
        if (endpoint === 'create_todo') return '/create_todo';
        return `/${endpoint}`; // Generic fallback
    }
});