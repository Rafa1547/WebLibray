// ===== UX IMPROVEMENTS - BIBLIOTECA FLORBELA ESPANCA =====

// Initialize all UX improvements when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initTooltips();
    initLoadingStates();
    initFormValidations();
    initAnimations();
    initKeyboardShortcuts();
    initSearchEnhancements();
    initProgressIndicators();
    initConfirmationModals();
    initBackToTop();
    initAutoSave();
});

// ===== TOOLTIPS EXPLICATIVOS =====
function initTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Add helpful tooltips to common elements
    const helpfulTooltips = {
        '.btn-danger': 'Esta ação não pode ser desfeita',
        '.badge': 'Clique para filtrar por esta categoria',
        '.card-header': 'Clique para expandir/colapsar',
        '.form-control[required]': 'Campo obrigatório',
        '.pagination .page-link': 'Navegar para esta página'
    };

    Object.entries(helpfulTooltips).forEach(([selector, title]) => {
        const elements = document.querySelectorAll(selector + ':not([data-bs-original-title])');
        elements.forEach(el => {
            el.setAttribute('data-bs-toggle', 'tooltip');
            el.setAttribute('data-bs-placement', 'top');
            el.setAttribute('title', title);
            new bootstrap.Tooltip(el);
        });
    });
}

// ===== LOADING STATES =====
function initLoadingStates() {
    // Show loading for form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !form.classList.contains('no-loading')) {
                showLoadingButton(submitBtn);
            }
        });
    });

    // Show loading for AJAX requests
    const ajaxLinks = document.querySelectorAll('[data-ajax="true"]');
    ajaxLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            showLoadingSpinner();
        });
    });
}

function showLoadingButton(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>A processar...';
    button.disabled = true;
    
    // Restore button after 5 seconds (fallback)
    setTimeout(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    }, 5000);
}

function showLoadingSpinner() {
    // Create loading overlay
    const loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'loading-overlay';
    loadingOverlay.innerHTML = `
        <div class="loading-content">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">A carregar...</span>
            </div>
            <p class="mt-3 text-muted">A processar pedido...</p>
        </div>
    `;
    document.body.appendChild(loadingOverlay);
    
    // Remove after 3 seconds (fallback)
    setTimeout(() => {
        if (loadingOverlay.parentNode) {
            loadingOverlay.remove();
        }
    }, 3000);
}

// ===== VALIDAÇÕES EM TEMPO REAL =====
function initFormValidations() {
    const inputs = document.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
        // Real-time validation
        input.addEventListener('blur', function() {
            validateField(this);
        });

        // Live character count for textareas
        if (input.tagName === 'TEXTAREA' && input.hasAttribute('maxlength')) {
            addCharacterCounter(input);
        }

        // Auto-format inputs
        if (input.type === 'email') {
            input.addEventListener('input', function() {
                this.value = this.value.toLowerCase().trim();
            });
        }
    });

    // Password strength indicator
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(input => {
        if (input.name === 'password' || input.name === 'new_password') {
            addPasswordStrengthIndicator(input);
        }
    });
}

function validateField(field) {
    const value = field.value.trim();
    const fieldName = field.name;
    let isValid = true;
    let message = '';

    // Remove previous validation states
    field.classList.remove('is-valid', 'is-invalid');
    const feedback = field.parentNode.querySelector('.invalid-feedback, .valid-feedback');
    if (feedback) feedback.remove();

    // Skip validation if field is empty and not required
    if (!value && !field.required) {
        return;
    }

    // Email validation
    if (field.type === 'email') {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            message = 'Por favor, introduza um email válido.';
        }
    }

    // Password validation
    if (field.type === 'password' && fieldName === 'password') {
        if (value.length < 6) {
            isValid = false;
            message = 'A password deve ter pelo menos 6 caracteres.';
        }
    }

    // Required field validation
    if (field.required && !value) {
        isValid = false;
        message = 'Este campo é obrigatório.';
    }

    // Apply validation styles
    field.classList.add(isValid ? 'is-valid' : 'is-invalid');
    
    // Add feedback message
    const feedbackDiv = document.createElement('div');
    feedbackDiv.className = isValid ? 'valid-feedback' : 'invalid-feedback';
    feedbackDiv.textContent = isValid ? 'Válido!' : message;
    field.parentNode.appendChild(feedbackDiv);

    return isValid;
}

function addCharacterCounter(textarea) {
    const maxLength = parseInt(textarea.getAttribute('maxlength'));
    const counter = document.createElement('small');
    counter.className = 'form-text text-muted character-counter';
    textarea.parentNode.appendChild(counter);

    function updateCounter() {
        const remaining = maxLength - textarea.value.length;
        counter.textContent = `${textarea.value.length}/${maxLength} caracteres`;
        counter.className = `form-text character-counter ${remaining < 50 ? 'text-warning' : remaining < 20 ? 'text-danger' : 'text-muted'}`;
    }

    textarea.addEventListener('input', updateCounter);
    updateCounter();
}

function addPasswordStrengthIndicator(input) {
    const indicator = document.createElement('div');
    indicator.className = 'password-strength-indicator mt-2';
    indicator.innerHTML = `
        <div class="progress" style="height: 5px;">
            <div class="progress-bar" role="progressbar" style="width: 0%"></div>
        </div>
        <small class="form-text text-muted mt-1">Força da password: <span class="strength-text">-</span></small>
    `;
    input.parentNode.appendChild(indicator);

    input.addEventListener('input', function() {
        const strength = calculatePasswordStrength(this.value);
        const progressBar = indicator.querySelector('.progress-bar');
        const strengthText = indicator.querySelector('.strength-text');

        progressBar.style.width = strength.percentage + '%';
        progressBar.className = `progress-bar bg-${strength.color}`;
        strengthText.textContent = strength.text;
    });
}

function calculatePasswordStrength(password) {
    let score = 0;
    if (password.length >= 6) score += 20;
    if (password.length >= 10) score += 20;
    if (/[a-z]/.test(password)) score += 20;
    if (/[A-Z]/.test(password)) score += 20;
    if (/[0-9]/.test(password)) score += 10;
    if (/[^A-Za-z0-9]/.test(password)) score += 10;

    if (score < 30) return { percentage: score, color: 'danger', text: 'Fraca' };
    if (score < 60) return { percentage: score, color: 'warning', text: 'Média' };
    if (score < 80) return { percentage: score, color: 'info', text: 'Boa' };
    return { percentage: score, color: 'success', text: 'Forte' };
}

// ===== ANIMAÇÕES SUAVES =====
function initAnimations() {
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);

    // Observe elements for animation
    const animatedElements = document.querySelectorAll('.card, .stats-card, .feature-item');
    animatedElements.forEach(el => {
        el.classList.add('animate-on-scroll');
        observer.observe(el);
    });

    // Smooth hover effects
    const hoverElements = document.querySelectorAll('.card, .btn, .nav-link');
    hoverElements.forEach(el => {
        el.style.transition = 'all 0.3s ease';
    });
}

// ===== ATALHOS DE TECLADO =====
function initKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[type="search"], input[name="search"]');
            if (searchInput) {
                searchInput.focus();
                showNotification('Pressione Esc para cancelar a pesquisa', 'info');
            }
        }

        // Escape to clear search
        if (e.key === 'Escape') {
            const searchInput = document.querySelector('input[type="search"], input[name="search"]');
            if (searchInput && searchInput === document.activeElement) {
                searchInput.value = '';
                searchInput.blur();
            }
        }

        // Alt + D for dashboard
        if (e.altKey && e.key === 'd') {
            e.preventDefault();
            const dashboardLink = document.querySelector('a[href*="dashboard"]');
            if (dashboardLink) {
                window.location.href = dashboardLink.href;
            }
        }
    });

    // Show keyboard shortcuts help
    const helpIcon = document.createElement('button');
    helpIcon.innerHTML = '<i class="fas fa-keyboard"></i>';
    helpIcon.className = 'btn btn-outline-secondary btn-sm position-fixed';
    helpIcon.style.cssText = 'bottom: 20px; right: 20px; z-index: 1000; opacity: 0.7;';
    helpIcon.title = 'Atalhos de teclado';
    helpIcon.onclick = showKeyboardShortcuts;
    document.body.appendChild(helpIcon);
}

function showKeyboardShortcuts() {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title"><i class="fas fa-keyboard me-2"></i>Atalhos de Teclado</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="row">
                        <div class="col-6"><kbd>Ctrl</kbd> + <kbd>K</kbd></div>
                        <div class="col-6">Pesquisar</div>
                    </div>
                    <div class="row mt-2">
                        <div class="col-6"><kbd>Esc</kbd></div>
                        <div class="col-6">Limpar pesquisa</div>
                    </div>
                    <div class="row mt-2">
                        <div class="col-6"><kbd>Alt</kbd> + <kbd>D</kbd></div>
                        <div class="col-6">Ir para Dashboard</div>
                    </div>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    modal.addEventListener('hidden.bs.modal', () => modal.remove());
}

// ===== MELHORIAS DE PESQUISA =====
function initSearchEnhancements() {
    const searchInputs = document.querySelectorAll('input[type="search"], input[name="search"]');
    
    searchInputs.forEach(input => {
        // Add search icon
        if (!input.parentNode.querySelector('.search-icon')) {
            const icon = document.createElement('i');
            icon.className = 'fas fa-search search-icon position-absolute';
            icon.style.cssText = 'right: 10px; top: 50%; transform: translateY(-50%); pointer-events: none; opacity: 0.5;';
            input.parentNode.style.position = 'relative';
            input.parentNode.appendChild(icon);
            input.style.paddingRight = '35px';
        }

        // Auto-search delay
        let searchTimeout;
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                if (this.value.length >= 2) {
                    // Could trigger auto-search here
                    showNotification('A pesquisar...', 'info', 1000);
                }
            }, 500);
        });

        // Search suggestions (placeholder for future implementation)
        input.addEventListener('focus', function() {
            // Could show search history or suggestions
        });
    });
}

// ===== INDICADORES DE PROGRESSO =====
function initProgressIndicators() {
    // File upload progress
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            if (this.files.length > 0) {
                showFilePreview(this);
            }
        });
    });

    // Form completion progress
    const forms = document.querySelectorAll('form:not(.no-progress)');
    forms.forEach(form => {
        if (form.querySelectorAll('input, textarea, select').length > 3) {
            addFormProgressIndicator(form);
        }
    });
}

function showFilePreview(input) {
    const file = input.files[0];
    const preview = document.createElement('div');
    preview.className = 'file-preview alert alert-info mt-2';
    preview.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-file me-2"></i>
            <div class="flex-grow-1">
                <strong>${file.name}</strong><br>
                <small class="text-muted">${(file.size / 1024 / 1024).toFixed(2)} MB</small>
            </div>
            <button type="button" class="btn btn-sm btn-outline-danger" onclick="this.parentNode.parentNode.remove(); document.querySelector('input[type=file]').value='';">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;

    // Remove existing preview
    const existingPreview = input.parentNode.querySelector('.file-preview');
    if (existingPreview) existingPreview.remove();

    input.parentNode.appendChild(preview);
}

function addFormProgressIndicator(form) {
    const fields = form.querySelectorAll('input:not([type="hidden"]), textarea, select');
    const progress = document.createElement('div');
    progress.className = 'form-progress mb-3';
    progress.innerHTML = `
        <div class="d-flex justify-content-between mb-1">
            <small class="text-muted">Progresso do formulário</small>
            <small class="text-muted"><span class="progress-text">0%</span></small>
        </div>
        <div class="progress" style="height: 5px;">
            <div class="progress-bar bg-success" style="width: 0%"></div>
        </div>
    `;

    form.insertBefore(progress, form.firstChild);

    function updateProgress() {
        const filled = Array.from(fields).filter(field => {
            if (field.type === 'checkbox' || field.type === 'radio') {
                return field.checked;
            }
            return field.value.trim() !== '';
        }).length;

        const percentage = Math.round((filled / fields.length) * 100);
        progress.querySelector('.progress-bar').style.width = percentage + '%';
        progress.querySelector('.progress-text').textContent = percentage + '%';
    }

    fields.forEach(field => {
        field.addEventListener('input', updateProgress);
        field.addEventListener('change', updateProgress);
    });

    updateProgress();
}

// ===== CONFIRMAÇÕES AMIGÁVEIS =====
function initConfirmationModals() {
    const dangerousActions = document.querySelectorAll('[onclick*="confirm"], .btn-danger[type="submit"]');
    
    dangerousActions.forEach(element => {
        element.addEventListener('click', function(e) {
            if (!this.hasAttribute('data-confirmed')) {
                e.preventDefault();
                showFriendlyConfirmation(this);
            }
        });
    });
}

function showFriendlyConfirmation(element) {
    const action = element.textContent.toLowerCase();
    const isDelete = action.includes('eliminar') || action.includes('apagar') || action.includes('remover');
    
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header border-0">
                    <h5 class="modal-title">
                        <i class="fas fa-${isDelete ? 'exclamation-triangle text-warning' : 'question-circle text-info'} me-2"></i>
                        Confirmar ${isDelete ? 'Eliminação' : 'Ação'}
                    </h5>
                </div>
                <div class="modal-body text-center">
                    <p class="mb-3">
                        ${isDelete ? 
                            'Esta ação irá eliminar permanentemente este item. Esta operação não pode ser desfeita.' :
                            'Tem certeza que pretende executar esta ação?'
                        }
                    </p>
                    <div class="d-flex gap-2 justify-content-center">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                            <i class="fas fa-times me-1"></i>Cancelar
                        </button>
                        <button type="button" class="btn btn-${isDelete ? 'danger' : 'primary'} confirm-action">
                            <i class="fas fa-check me-1"></i>Confirmar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();

    modal.querySelector('.confirm-action').onclick = function() {
        element.setAttribute('data-confirmed', 'true');
        bsModal.hide();
        setTimeout(() => {
            if (element.tagName === 'BUTTON' && element.form) {
                element.form.submit();
            } else {
                element.click();
            }
        }, 300);
    };

    modal.addEventListener('hidden.bs.modal', () => modal.remove());
}

// ===== VOLTAR AO TOPO =====
function initBackToTop() {
    const backToTop = document.createElement('button');
    backToTop.innerHTML = '<i class="fas fa-chevron-up"></i>';
    backToTop.className = 'btn btn-primary btn-back-to-top';
    backToTop.style.cssText = `
        position: fixed;
        bottom: 80px;
        right: 20px;
        z-index: 1000;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        opacity: 0;
        visibility: hidden;
        transition: all 0.3s ease;
    `;

    document.body.appendChild(backToTop);

    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTop.style.opacity = '1';
            backToTop.style.visibility = 'visible';
        } else {
            backToTop.style.opacity = '0';
            backToTop.style.visibility = 'hidden';
        }
    });

    backToTop.addEventListener('click', function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

// ===== AUTO-SAVE =====
function initAutoSave() {
    const textareas = document.querySelectorAll('textarea[data-autosave="true"]');
    
    textareas.forEach(textarea => {
        const key = 'autosave_' + (textarea.name || textarea.id);
        
        // Load saved content
        const saved = localStorage.getItem(key);
        if (saved && !textarea.value) {
            textarea.value = saved;
            showNotification('Conteúdo restaurado automaticamente', 'info', 3000);
        }

        // Auto-save on input
        let saveTimeout;
        textarea.addEventListener('input', function() {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
                localStorage.setItem(key, this.value);
                showAutoSaveIndicator();
            }, 2000);
        });

        // Clear auto-save on form submit
        const form = textarea.closest('form');
        if (form) {
            form.addEventListener('submit', function() {
                localStorage.removeItem(key);
            });
        }
    });
}

function showAutoSaveIndicator() {
    let indicator = document.querySelector('.autosave-indicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.className = 'autosave-indicator alert alert-success position-fixed';
        indicator.style.cssText = 'top: 20px; right: 20px; z-index: 1050; padding: 0.5rem 1rem; opacity: 0; transition: opacity 0.3s;';
        indicator.innerHTML = '<i class="fas fa-save me-1"></i>Guardado automaticamente';
        document.body.appendChild(indicator);
    }

    indicator.style.opacity = '1';
    setTimeout(() => {
        indicator.style.opacity = '0';
    }, 2000);
}

// ===== NOTIFICAÇÕES AMIGÁVEIS =====
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} notification-toast position-fixed`;
    notification.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 1060;
        min-width: 300px;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
    `;
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'warning' ? 'exclamation-triangle' : type === 'danger' ? 'times-circle' : 'info-circle'} me-2"></i>
            <span>${message}</span>
            <button type="button" class="btn-close ms-auto" onclick="this.parentNode.parentNode.remove()"></button>
        </div>
    `;

    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 100);

    // Auto remove
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

// ===== CSS PARA MELHORIAS =====
const uxStyles = `
<style>
.animate-on-scroll {
    opacity: 0;
    transform: translateY(20px);
    transition: all 0.6s ease;
}

.animate-in {
    opacity: 1;
    transform: translateY(0);
}

.loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(255, 255, 255, 0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
}

.character-counter {
    font-size: 0.8rem;
}

.password-strength-indicator .progress {
    margin-bottom: 0.5rem;
}

.form-progress {
    background: rgba(var(--primary-rgb), 0.05);
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid var(--primary-color);
}

.btn-back-to-top:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.notification-toast {
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    border-radius: 0.5rem;
    border: none;
}

.file-preview {
    border-left: 4px solid var(--info-color);
}

kbd {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 3px;
    padding: 2px 6px;
    font-size: 0.85em;
}
</style>
`;

// Inject styles
document.head.insertAdjacentHTML('beforeend', uxStyles); 