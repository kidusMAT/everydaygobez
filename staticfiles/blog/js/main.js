/**
 * Everyday Gobez Client-Side Core Engine
 * Manages premium animations, scroll metrics, and asynchronous interactions.
 */

document.addEventListener('DOMContentLoaded', () => {
    // --- 1. Toast Notification Self-Dismissal ---
    const toasts = document.querySelectorAll('.toast-card');
    toasts.forEach(toast => {
        // Setup manual dismiss on X click
        const closeBtn = toast.querySelector('.toast-close-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                dismissToast(toast);
            });
        }

        // Automatic dismiss after 4.5 seconds
        setTimeout(() => {
            dismissToast(toast);
        }, 4500);
    });

    function dismissToast(toast) {
        toast.style.transform = 'translateX(50px)';
        toast.style.opacity = '0';
        setTimeout(() => {
            toast.remove();
        }, 350);
    }

    // --- 2. Scroll Progress Metrics (Reading Screen) ---
    const progressBar = document.getElementById('scroll-progress');
    if (progressBar) {
        window.addEventListener('scroll', () => {
            const windowScroll = document.documentElement.scrollTop || document.body.scrollTop;
            const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const scrolled = height > 0 ? (windowScroll / height) * 100 : 0;
            progressBar.style.width = scrolled + '%';
        });
    }

    // --- 3. Mobile Navigation Drawer Controls ---
    const mobileMenuTrigger = document.querySelector('.mobile-menu-toggle');
    const drawerCloseBtn = document.querySelector('.drawer-close');
    const navDrawer = document.querySelector('.mobile-nav-drawer');

    if (mobileMenuTrigger && navDrawer) {
        mobileMenuTrigger.addEventListener('click', () => {
            navDrawer.classList.add('open');
        });
    }

    if (drawerCloseBtn && navDrawer) {
        drawerCloseBtn.addEventListener('click', () => {
            navDrawer.classList.remove('open');
        });
    }

    // Close mobile drawer on clicking backdrop or clicking outside the drawer
    document.addEventListener('click', (e) => {
        if (navDrawer && navDrawer.classList.contains('open')) {
            if (!navDrawer.contains(e.target) && !mobileMenuTrigger.contains(e.target)) {
                navDrawer.classList.remove('open');
            }
        }
    });

    // --- 4. Mobile Dropdown Toggle Support ---
    const profileDropdown = document.querySelector('.nav-profile-dropdown');
    if (profileDropdown) {
        const trigger = profileDropdown.querySelector('.nav-profile-trigger');
        trigger.addEventListener('click', (e) => {
            e.stopPropagation();
            const menu = profileDropdown.querySelector('.dropdown-menu');
            const isVisible = window.getComputedStyle(menu).visibility === 'visible';
            
            if (isVisible) {
                menu.style.opacity = '0';
                menu.style.visibility = 'hidden';
                menu.style.transform = 'translateY(10px)';
            } else {
                menu.style.opacity = '1';
                menu.style.visibility = 'visible';
                menu.style.transform = 'translateY(0)';
            }
        });

        // Close dropdown when clicking anywhere else
        document.addEventListener('click', () => {
            const menu = profileDropdown.querySelector('.dropdown-menu');
            if (menu) {
                menu.style.opacity = '';
                menu.style.visibility = '';
                menu.style.transform = '';
            }
        });
    }
});
