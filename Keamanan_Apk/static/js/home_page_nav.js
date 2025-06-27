// static/home_page_nav.js

document.addEventListener('DOMContentLoaded', function() {
    const navbarHome = document.querySelector('.navbar-custom-home'); // Navbar khusus Home
    if (!navbarHome) return; // Keluar jika navbarHome tidak ada di halaman ini

    const allHomeNavLinks = navbarHome.querySelectorAll('.navbar-nav .nav-link');
    const homeActiveIndicator = document.getElementById('active-indicator'); // Untuk navbar Home
    const sections = document.querySelectorAll('section[id]'); // Semua section Home (top, services-section, about-section, faq-section)
    const scrollThreshold = 200; // Jarak scroll untuk mengaktifkan efek solid navbar (Home)

    let isScrollingByClick = false; // Flag untuk mendeteksi scroll akibat klik navbar
    let isProgrammaticScroll = false; // Flag untuk mendeteksi scroll yang dipicu JS
    let currentSectionIndex = 0; // Index section yang sedang aktif (Home)
    const scrollCooldown = 800; // Cooldown antara scroll snaps (ms)
    let lastScrollTime = 0; // Waktu terakhir scroll wheel

    // --- Fungsi untuk Menggerakkan Indikator Aktif pada Navbar Home ---
    function updateHomeActiveIndicator(targetLink = null) {
        if (isProgrammaticScroll || (isScrollingByClick && targetLink === null)) {
            return;
        }

        let linkToActivate = null;

        // Reset semua gaya inline dari link nav (penting untuk menghapus "jejak")
        allHomeNavLinks.forEach(link => {
            link.classList.remove('active');
            link.style.backgroundColor = '';
            link.style.borderColor = '';
            link.style.boxShadow = '';
            link.style.transform = '';
            link.style.color = '';
        });

        if (targetLink) { // Jika targetLink diberikan (dari klik atau hover)
            linkToActivate = targetLink;
        } else { // Jika tidak ada targetLink, tentukan berdasarkan posisi scroll/URL
            const currentPath = window.location.pathname;

            if (currentPath === '/' || currentPath === '/home') {
                let foundActiveSection = false;
                for (let i = 0; i < sections.length; i++) {
                    const section = sections[i];
                    const rect = section.getBoundingClientRect();
                    if (rect.top <= window.innerHeight / 2 && rect.bottom >= window.innerHeight / 2) {
                        linkToActivate = document.querySelector(`.navbar-nav .nav-link[href*="#${section.id}"]`);
                        currentSectionIndex = i;
                        foundActiveSection = true;
                        break;
                    }
                }
                if (!foundActiveSection) {
                    const hash = window.location.hash.substring(1);
                    if (hash) {
                        linkToActivate = document.querySelector(`.navbar-nav .nav-link[href*="#${hash}"]`);
                        sections.forEach((s, idx) => { if (s.id === hash) currentSectionIndex = idx; });
                    } else {
                        linkToActivate = document.querySelector(`.navbar-nav .nav-link[href*="#top"]`); // Default ke Home
                        currentSectionIndex = 0;
                    }
                }
            } else {
                // Untuk halaman non-Home (Login, Register, Services, About)
                allHomeNavLinks.forEach(link => {
                    const linkHref = link.getAttribute('href').split('?')[0];
                    if (currentPath.includes(linkHref) && linkHref !== '/' && linkHref !== '/home' && linkHref !== url_for_js('logout').split('?')[0]) { // Exclude logout, it's special
                        linkToActivate = link;
                    }
                });
                // Handle Login/Register active state specifically if currentPath is login or register
                if (currentPath === url_for_js('login') || currentPath === url_for_js('register')) {
                    linkToActivate = document.querySelector(`.navbar-nav .nav-link[href*="${currentPath}"]`);
                }
            }
        }

        if (linkToActivate) {
            const navRect = linkToActivate.closest('.navbar-nav').getBoundingClientRect();
            const linkRect = linkToActivate.getBoundingClientRect();

            homeActiveIndicator.style.left = `${linkRect.left - navRect.left}px`;
            homeActiveIndicator.style.width = `${linkRect.width}px`;
            homeActiveIndicator.classList.add('visible');
            homeActiveIndicator.style.opacity = '1';
            
            linkToActivate.classList.add('active'); // Aktifkan link untuk warnanya (JS mengontrol)
        } else {
            homeActiveIndicator.classList.remove('visible');
            homeActiveIndicator.style.opacity = '0';
        }
    }

    // --- Efek Navbar Home Transparan/Solid Berdasarkan Scroll ---
    function handleScrollNavbarHome() {
        if (window.scrollY > scrollThreshold) {
            navbarHome.classList.add('navbar-scrolled');
        } else {
            navbarHome.classList.remove('navbar-scrolled');
        }
    }

    // --- Logika Section Snapping / Scroll Per Bagian (Hanya di Halaman Home) ---
    function scrollToHomeSection(index) {
        if (!(window.location.pathname === '/' || window.location.pathname === '/home')) return; // Pastikan di Home
        if (index >= 0 && index < sections.length) {
            isProgrammaticScroll = true;
            const targetElement = sections[index];
            const navbarHeight = navbarHome.offsetHeight;
            const topOffset = navbarHeight + 20;

            window.scrollTo({
                top: targetElement.offsetTop - topOffset,
                behavior: 'smooth'
            });

            // Update indikator segera
            setNavLinkActiveState(allHomeNavLinks, homeActiveIndicator, 'horizontal', document.querySelector(`.navbar-nav .nav-link[href*="#${targetElement.id}"]`));

            const scrollEndHandler = () => {
                isProgrammaticScroll = false;
                setNavLinkActiveState(allHomeNavLinks, homeActiveIndicator, 'horizontal');
                window.removeEventListener('scrollend', scrollEndHandler);
            };
            window.addEventListener('scrollend', scrollEndHandler);
            setTimeout(() => {
                if (isProgrammaticScroll) {
                    isProgrammaticScroll = false;
                    setNavLinkActiveState(allHomeNavLinks, homeActiveIndicator, 'horizontal');
                }
            }, 800);
        }
    }

    function handleHomeWheel(event) {
        if (!(window.location.pathname === '/' || window.location.pathname === '/home')) {
            return;
        }

        const now = new Date().getTime();
        if (now - lastScrollTime < scrollCooldown || isProgrammaticScroll || isScrollingByClick) {
            event.preventDefault();
            return;
        }
        lastScrollTime = now;

        event.preventDefault();

        if (event.deltaY > 0) { // Scroll down
            if (currentSectionIndex < sections.length - 1) {
                currentSectionIndex++;
                scrollToHomeSection(currentSectionIndex);
            }
        } else if (event.deltaY < 0) { // Scroll up
            if (currentSectionIndex > 0) {
                currentSectionIndex--;
                scrollToHomeSection(currentSectionIndex);
            }
        }
    }

    // === Event Listeners untuk Navbar Home ===
    if (navbarHome) { // Hanya jalankan logika ini jika elemen navbarHome ada
        window.addEventListener('scroll', handleScrollNavbarHome);
        window.addEventListener('wheel', handleHomeWheel, { passive: false });

        allHomeNavLinks.forEach(link => {
            link.addEventListener('click', function(event) {
                if (this.hash && (window.location.pathname === '/' || window.location.pathname === '/home')) {
                    event.preventDefault();
                    isScrollingByClick = true;
                    
                    const targetId = this.hash.substring(1);
                    const targetElement = document.getElementById(targetId);
                    
                    if (targetElement) {
                        sections.forEach((section, index) => {
                            if (section.id === targetId) {
                                currentSectionIndex = index;
                            }
                        });

                        setNavLinkActiveState(allHomeNavLinks, homeActiveIndicator, 'horizontal', this); // Geser indikator
                        
                        window.scrollTo({
                            top: targetElement.offsetTop - 80,
                            behavior: 'smooth'
                        });

                        const scrollEndHandler = () => {
                            isScrollingByClick = false;
                            setNavLinkActiveState(allHomeNavLinks, homeActiveIndicator, 'horizontal');
                            window.removeEventListener('scrollend', scrollEndHandler);
                        };
                        window.addEventListener('scrollend', scrollEndHandler);
                        setTimeout(() => {
                            if (isScrollingByClick) {
                                isScrollingByClick = false;
                                setNavLinkActiveState(allHomeNavLinks, homeActiveIndicator, 'horizontal');
                            }
                        }, 800);
                    }
                } else if (!this.hash) {
                    setNavLinkActiveState(allHomeNavLinks, homeActiveIndicator, 'horizontal', this);
                }
            });

            // Handle Hover pada Link Navbar Home (hanya outline, tanpa background indicator)
            link.addEventListener('mouseenter', function() {
                if (!isScrollingByClick && !isProgrammaticScroll && !this.classList.contains('active')) {
                    this.style.color = 'var(--dm-white)';
                    this.style.borderColor = 'var(--dm-accent-blue)';
                    this.style.boxShadow = '0 0 15px rgba(0, 123, 255, 0.6), inset 0 0 5px rgba(0, 123, 255, 0.3)';
                    this.style.transform = 'translateY(-1px)';
                }
            });

            link.addEventListener('mouseleave', function() {
                if (!isScrollingByClick && !isProgrammaticScroll && !this.classList.contains('active')) {
                    this.style.color = '';
                    this.style.borderColor = '';
                    this.style.boxShadow = '';
                    this.style.transform = '';
                }
                setNavLinkActiveState(allHomeNavLinks, homeActiveIndicator, 'horizontal');
            });
        });

        // Inisialisasi Active State Navbar Home saat Halaman Dimuat
        setTimeout(() => {
            if (window.location.pathname === '/' || window.location.pathname === '/home') {
                const hash = window.location.hash.substring(1);
                if (hash) {
                     sections.forEach((section, index) => {
                        if (section.id === hash) {
                            currentSectionIndex = index;
                        }
                    });
                } else {
                    for (let i = 0; i < sections.length; i++) {
                        const section = sections[i];
                        const rect = section.getBoundingClientRect();
                        if (rect.top <= window.innerHeight / 2 && rect.bottom >= window.innerHeight / 2) {
                            currentSectionIndex = i;
                            break;
                        }
                    }
                }
            }
            setNavLinkActiveState(allHomeNavLinks, homeActiveIndicator, 'horizontal');
            handleScrollNavbarHome();
        }, 200);

        // Resize listener untuk Navbar Home
        window.addEventListener('resize', () => {
            setNavLinkActiveState(allHomeNavLinks, homeActiveIndicator, 'horizontal');
            handleScrollNavbarHome();
        });
    }

    // Helper function (placeholder untuk Flask url_for di JS)
    // Dalam aplikasi nyata, ini bisa di-generate oleh Flask ke dalam JS global object.
    function url_for_js(endpoint) {
        if (endpoint === 'home') return '/';
        if (endpoint === 'dashboard') return '/dashboard';
        if (endpoint === 'admin_panel') return '/admin_panel';
        if (endpoint === 'services') return '/services';
        if (endpoint === 'about') return '/about';
        if (endpoint === 'login') return '/login';
        if (endpoint === 'register') return '/register';
        if (endpoint === 'logout') return '/logout';
        return `/${endpoint}`; // Generic fallback
    }
});