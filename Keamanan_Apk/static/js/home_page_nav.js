// static/js/home_page_nav.js















document.addEventListener('DOMContentLoaded', function() {



    let isScrolling = false;



    const navbarNav = document.querySelector('.navbar-nav');



    // Cek apakah elemen navbar ada di halaman ini



    if (!navbarNav) {



        console.log('Navbar container not found. Skipping navbar script.');



        return; // Hentikan eksekusi script jika navbar tidak ada



    }







    const navbarLinks = navbarNav.querySelectorAll('.nav-link');



    const sections = document.querySelectorAll('section[id]');



    const navSlider = document.getElementById('nav-slider');







    // Fungsi untuk menggerakkan slider ke posisi link tertentu



    function updateSlider(linkElement) {



        if (!linkElement || !navSlider || !navbarNav) return;







        const navRect = navbarNav.getBoundingClientRect();



        const linkRect = linkElement.getBoundingClientRect();



       



        const leftPos = linkRect.left - navRect.left;



        const width = linkRect.width;







        navSlider.style.width = `${width}px`;



        navSlider.style.transform = `translateX(${leftPos}px)`;



        navSlider.style.opacity = 1;



    }







    // Fungsi untuk menghapus kelas 'active' dari semua link



    function removeActiveClass() {



        navbarLinks.forEach(link => {



            link.classList.remove('active');



        });



    }







    // Fungsi untuk menambahkan kelas 'active' ke link yang sesuai



    function addActiveClass(id) {



        removeActiveClass();



        const activeLink = document.querySelector(`.navbar-nav .nav-link[href*="#${id}"]`);



        if (activeLink) {



            activeLink.classList.add('active');



            updateSlider(activeLink);



        } else {



            // Jika tidak ada link aktif, sembunyikan slider



            if (navSlider) {



                navSlider.style.opacity = 0;



            }



        }



    }







    // Intersection Observer



    const observerOptions = {



        root: null,



        rootMargin: '-50% 0px -50% 0px',



        threshold: 0



    };







    const observer = new IntersectionObserver((entries, observer) => {



        if(isScrolling)return;      



        entries.forEach(entry => {



            if (entry.isIntersecting) {



                addActiveClass(entry.target.id);



            }



        });



    }, observerOptions);







    sections.forEach(section => {



        observer.observe(section);



    });







    // Event Listeners untuk hover



    navbarLinks.forEach(link => {



        link.addEventListener('mouseover', function() {



            this.classList.add('hover-outline');



        });







        link.addEventListener('mouseout', function() {



           this.classList.remove('hover-outline');



        });



    });







    // Event Listener untuk klik



    navbarLinks.forEach(link => {



        link.addEventListener('click', function(event) {



            const href = this.getAttribute('href');



            const linkPath = href.split('#')[0];



            const currentPath = window.location.pathname;



           



            if (href.includes('#') && (linkPath === currentPath || linkPath === '')) {



                event.preventDefault();



                const targetId = href.split('#')[1];



                const targetElement = document.getElementById(targetId);



               



                if (targetElement) {



                    removeActiveClass();



                    this.classList.add('active');



                    updateSlider(this);



                   



                    isScrolling=true;



                    window.scrollTo({



                        top: targetElement.offsetTop - 120,



                        behavior: 'smooth'



                    });







                    setTimeout(() => {



                    isScrolling = false;



                    }, 800);



                }



            }



        });



    });







    // Logika untuk mengaktifkan link saat halaman dimuat



    window.addEventListener('load', function() {



        const initialHash = window.location.hash.substring(1);



        if (initialHash) {



            addActiveClass(initialHash);



        } else {



            const currentPath = window.location.pathname;



            let foundActiveLink = false;



           



            navbarLinks.forEach(link => {



                if (link.getAttribute('href') === currentPath) {



                     removeActiveClass();



                     link.classList.add('active');



                     updateSlider(link);



                     foundActiveLink = true;



                }



            });



           



            if (!foundActiveLink) {



                if (currentPath === '/' || currentPath.endsWith('/home')) {



                     addActiveClass('top');



                } else {



                    if (navSlider) {



                        navSlider.style.opacity = 0;



                    }



                }



            }



        }



    });



});