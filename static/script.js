document.addEventListener('DOMContentLoaded', () => {

    // ── Navbar Scroll Effect ──
    const navbar = document.getElementById('main-navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            navbar.classList.toggle('scrolled', window.scrollY > 60);
        });
    }

    // ── Mobile Menu ──
    const hamburger = document.getElementById('hamburger');
    const mobileMenu = document.getElementById('mobile-menu');
    const mobileOverlay = document.getElementById('mobile-overlay');

    if (hamburger && mobileMenu && mobileOverlay) {
        function toggleMenu() {
            hamburger.classList.toggle('open');
            mobileMenu.classList.toggle('active');
            mobileOverlay.classList.toggle('active');
            document.body.style.overflow = mobileMenu.classList.contains('active') ? 'hidden' : '';
        }

        hamburger.addEventListener('click', toggleMenu);
        mobileOverlay.addEventListener('click', toggleMenu);

        // Close mobile menu on link click
        document.querySelectorAll('.mobile-menu a').forEach(link => {
            link.addEventListener('click', () => {
                if (mobileMenu.classList.contains('active')) toggleMenu();
            });
        });
    }

    // ── Smooth Scroll ──
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href === '#' || !href) return; // Ignorar enlaces vacíos

            e.preventDefault();
            try {
                const target = document.querySelector(href);
                if (target) {
                    const offset = 80;
                    const top = target.getBoundingClientRect().top + window.scrollY - offset;
                    window.scrollTo({ top, behavior: 'smooth' });

                    // Update active state for nav links
                    document.querySelectorAll('.nav-links a').forEach(l => l.classList.remove('active'));
                    const navLink = document.querySelector(`.nav-links a[href="${href}"]`);
                    if (navLink) navLink.classList.add('active');
                }
            } catch (err) { console.warn("Invalid selector:", href); }
        });
    });

    // ── Scroll Reveal (Intersection Observer) ──
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

    // ── Floating Particles in Hero ──
    const particlesContainer = document.getElementById('particles');
    if (particlesContainer) {
        for (let i = 0; i < 30; i++) {
            const particle = document.createElement('div');
            particle.style.cssText = `
                position: absolute;
                width: ${Math.random() * 3 + 1}px;
                height: ${Math.random() * 3 + 1}px;
                background: rgba(201, 168, 76, ${Math.random() * 0.3 + 0.05});
                border-radius: 50%;
                left: ${Math.random() * 100}%;
                top: ${Math.random() * 100}%;
                animation: floatParticle ${Math.random() * 10 + 8}s ease-in-out infinite;
                animation-delay: ${Math.random() * -10}s;
                pointer-events: none;
            `;
            particlesContainer.appendChild(particle);
        }
    }

    // Add particle keyframes dynamically
    const style = document.createElement('style');
    style.textContent = `
        @keyframes floatParticle {
            0%, 100% { transform: translate(0, 0) scale(1); opacity: 0; }
            10% { opacity: 1; }
            90% { opacity: 1; }
            50% { transform: translate(${Math.random() > 0.5 ? '' : '-'}${Math.random() * 80 + 20}px, -${Math.random() * 120 + 40}px) scale(1.5); }
        }
    `;
    document.head.appendChild(style);

    // ── Active Section Highlight on Scroll ──
    const sections = document.querySelectorAll('section[id]');
    window.addEventListener('scroll', () => {
        const scrollY = window.scrollY + 120;
        sections.forEach(section => {
            const top = section.offsetTop;
            const height = section.offsetHeight;
            const id = section.getAttribute('id');
            const link = document.querySelector(`.nav-links a[href="#${id}"]`);
            if (link) {
                if (scrollY >= top && scrollY < top + height) {
                    document.querySelectorAll('.nav-links a').forEach(l => l.classList.remove('active'));
                    link.classList.add('active');
                }
            }
        });
    });

    // ── Check Session ──
    const session = JSON.parse(localStorage.getItem('sspc_session'));
    if (session && session.isVerified) {
        // Desktop
        const navActions = document.querySelector('.nav-actions');
        const loginBtn = document.getElementById('btn-login');
        if (loginBtn && navActions) {
            const profileCtn = document.createElement('div');
            profileCtn.className = 'nav-profile';
            profileCtn.innerHTML = `
                <img src="${session.avatar}" class="nav-avatar" alt="Avatar">
                <span class="nav-username">${session.username}</span>
                <div class="profile-dropdown">
                    <a href="dashboard.html" class="dropdown-link">Panel de Mando</a>
                    <a href="#" class="dropdown-link logout" id="logout-desktop">Cerrar Sesión</a>
                </div>
            `;
            navActions.replaceChild(profileCtn, loginBtn);
            
            document.getElementById('logout-desktop').addEventListener('click', (e) => {
                e.preventDefault();
                localStorage.removeItem('sspc_session');
                window.location.href = 'index.html';
            });
        }

        // Mobile
        const mobileLinks = document.querySelector('.mobile-menu ul');
        const mobileLogin = document.querySelector('.mobile-login');
        if (mobileLogin) {
            const mobileProfile = document.createElement('li');
            mobileProfile.innerHTML = `
                <a href="dashboard.html" class="mobile-profile-item">
                    <img src="${session.avatar}" class="nav-avatar" alt="Avatar">
                    <span>${session.username} (Oficial)</span>
                </a>
            `;
            mobileLogin.parentElement.replaceWith(mobileProfile);
            
            // Add Logout to mobile
            const logoutLi = document.createElement('li');
            logoutLi.className = 'mobile-logout-li';
            logoutLi.innerHTML = '<a href="#" id="btn-logout-mobile" style="color: #ff6b6b">Cerrar Sesión</a>';
            mobileLinks.appendChild(logoutLi);
            
            document.getElementById('btn-logout-mobile').addEventListener('click', (e) => {
                e.preventDefault();
                localStorage.removeItem('sspc_session');
                window.location.href = 'index.html';
            });
        }
    }

    // ── Login Button (Discord OAuth2) ──
    const btnLogin = document.getElementById('btn-login');
    if (btnLogin) {
        btnLogin.addEventListener('click', () => {
            const CLIENT_ID = '1496760858599096440';
            const REDIRECT_URI = window.location.origin + '/verificacion.html'; 
            const oauth2Url = `https://discord.com/api/oauth2/authorize?client_id=${CLIENT_ID}&redirect_uri=${encodeURIComponent(REDIRECT_URI)}&response_type=token&scope=identify%20guilds%20guilds.members.read`;
            window.location.href = oauth2Url;
        });
    }

    // ── Manual Module Tabs ──
    const modTabs = document.querySelectorAll('.mod-tab');
    const modules = document.querySelectorAll('.module');

    if (modTabs.length) {
        modTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const target = tab.dataset.module;
                modTabs.forEach(t => t.classList.remove('active'));
                modules.forEach(m => m.classList.remove('active'));
                tab.classList.add('active');
                const targetModule = document.getElementById('mod-' + target);
                if (targetModule) targetModule.classList.add('active');

                // Clear search when switching tabs
                const si = document.getElementById('manual-search');
                const sr = document.getElementById('search-results');
                const sc = document.getElementById('search-clear');
                if (si) { si.value = ''; }
                if (sr) sr.textContent = '';
                if (sc) sc.classList.remove('visible');

                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
        });
    }

    // ── Manual Search ──
    const searchInput = document.getElementById('manual-search');
    const searchClear = document.getElementById('search-clear');
    const searchResults = document.getElementById('search-results');

    if (searchInput) {
        let debounceTimer;

        searchInput.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => performSearch(), 200);
        });

        searchClear.addEventListener('click', () => {
            searchInput.value = '';
            searchClear.classList.remove('visible');
            searchResults.textContent = '';
            // Go back to first tab
            if (modTabs[0]) modTabs[0].click();
        });

        function performSearch() {
            const query = searchInput.value.trim().toLowerCase();
            searchClear.classList.toggle('visible', query.length > 0);

            if (query.length < 2) {
                searchResults.textContent = '';
                return;
            }

            let firstMatchModule = null;
            let matchCount = 0;

            modules.forEach(mod => {
                const text = mod.textContent.toLowerCase();
                if (text.includes(query)) {
                    matchCount++;
                    if (!firstMatchModule) firstMatchModule = mod;
                }
            });

            if (firstMatchModule) {
                const modId = firstMatchModule.id.replace('mod-', '');
                const tab = document.querySelector(`.mod-tab[data-module="${modId}"]`);
                if (tab) {
                    modTabs.forEach(t => t.classList.remove('active'));
                    modules.forEach(m => m.classList.remove('active'));
                    tab.classList.add('active');
                    firstMatchModule.classList.add('active');
                }
                searchResults.textContent = `${matchCount} módulo${matchCount !== 1 ? 's' : ''} con resultados`;
                window.scrollTo({ top: 0, behavior: 'smooth' });
            } else {
                searchResults.textContent = `Sin resultados para "${query}"`;
            }
        }
    }

});

