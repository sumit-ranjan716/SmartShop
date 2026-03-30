/**
 * SmartShop — Main JavaScript
 * Handles UI interactions, alerts auto-dismiss, and dynamic behaviours.
 */

// ---- Apply theme instantly to prevent flash of white ----
const savedTheme = localStorage.getItem('smartshop_theme');
const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
const initialTheme = savedTheme || (systemDark ? 'dark' : 'light');
document.documentElement.setAttribute('data-bs-theme', initialTheme);

document.addEventListener('DOMContentLoaded', () => {
    // ---- Theme Toggle Logic ----
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const htmlEl = document.documentElement;

    const updateThemeIcon = (theme) => {
        if (theme === 'dark') {
            themeIcon.classList.remove('bi-moon-stars-fill');
            themeIcon.classList.add('bi-sun-fill');
            themeIcon.classList.add('text-warning');
        } else {
            themeIcon.classList.remove('bi-sun-fill', 'text-warning');
            themeIcon.classList.add('bi-moon-stars-fill');
        }
    };

    // Set initial icon
    updateThemeIcon(initialTheme);

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = htmlEl.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            htmlEl.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('smartshop_theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }
    // ---- Auto-dismiss alerts after 5 seconds ----
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                alert.classList.remove('show');
                setTimeout(() => alert.remove(), 300);
            }
        }, 5000);
    });

    // ---- Navbar shrink on scroll ----
    const navbar = document.getElementById('mainNav');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.classList.add('shadow-sm');
                navbar.style.padding = '0.3rem 0';
            } else {
                navbar.classList.remove('shadow-sm');
                navbar.style.padding = '0.6rem 0';
            }
        });
    }

    // ---- Smooth scroll for anchor links ----
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // ---- Add to cart animation (pulse the cart badge) ----
    const addToCartForms = document.querySelectorAll('form[action*="/cart/add/"]');
    addToCartForms.forEach(form => {
        form.addEventListener('submit', () => {
            const badge = document.querySelector('.cart-badge');
            if (badge) {
                badge.style.transform = 'translate(-30%, -30%) scale(1.5)';
                setTimeout(() => {
                    badge.style.transform = 'translate(-30%, -30%) scale(1)';
                }, 300);
            }
        });
    });

    // ---- Confirm before clearing cart ----
    const clearCartLink = document.querySelector('a[href*="/cart/clear/"]');
    if (clearCartLink) {
        clearCartLink.addEventListener('click', (e) => {
            if (!confirm('Are you sure you want to clear your cart?')) {
                e.preventDefault();
            }
        });
    }

    // ---- Quantity input validation ----
    document.querySelectorAll('input[type="number"][name="quantity"]').forEach(input => {
        input.addEventListener('change', () => {
            const min = parseInt(input.min) || 1;
            const max = parseInt(input.max) || 999;
            let val = parseInt(input.value);
            if (isNaN(val) || val < min) val = min;
            if (val > max) val = max;
            input.value = val;
        });
    });

    // ---- Back to top button (auto create if needed) ----
    const backToTop = document.createElement('button');
    backToTop.innerHTML = '<i class="bi bi-arrow-up"></i>';
    backToTop.className = 'btn btn-primary rounded-circle shadow';
    backToTop.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 45px;
        height: 45px;
        display: none;
        z-index: 1000;
        border: none;
        font-size: 1.2rem;
        transition: all 0.3s ease;
    `;
    document.body.appendChild(backToTop);

    window.addEventListener('scroll', () => {
        backToTop.style.display = window.scrollY > 300 ? 'block' : 'none';
    });

    backToTop.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
});
