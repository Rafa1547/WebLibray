// ===== MAIN JAVASCRIPT FILE =====

// Inicialização quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Função principal de inicialização
function initializeApp() {
    initializeAnimations();
    initializeFormValidations();
    initializeTooltips();
    initializeSearchFeatures();
    initializeCharts();
    initializeAjaxForms();
}

// ===== ANIMAÇÕES =====
function initializeAnimations() {
    // Adicionar animações aos elementos quando entram na viewport
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observar cards, widgets e seções
    document.querySelectorAll('.card, .dashboard-widget, .stats-card, .book-card').forEach(el => {
        observer.observe(el);
    });

    // Animação de contadores para estatísticas
    animateCounters();
}

function animateCounters() {
    const counters = document.querySelectorAll('.stats-number');
    
    counters.forEach(counter => {
        const target = parseInt(counter.textContent);
        const duration = 2000; // 2 segundos
        const step = target / (duration / 16); // 60 FPS
        let current = 0;
        
        const timer = setInterval(() => {
            current += step;
            if (current >= target) {
                counter.textContent = target;
                clearInterval(timer);
            } else {
                counter.textContent = Math.floor(current);
            }
        }, 16);
    });
}

// ===== VALIDAÇÕES DE FORMULÁRIO =====
function initializeFormValidations() {
    // Validação em tempo real para email
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(input => {
        input.addEventListener('blur', validateEmail);
        input.addEventListener('input', debounce(checkEmailExists, 500));
    });

    // Validação de passwords
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(input => {
        input.addEventListener('input', validatePassword);
    });

    // Validação de confirmação de password
    const confirmPasswordInputs = document.querySelectorAll('input[name="confirm_password"]');
    confirmPasswordInputs.forEach(input => {
        input.addEventListener('input', validatePasswordConfirmation);
    });

    // Validação de ISBN
    const isbnInputs = document.querySelectorAll('input[name="isbn"]');
    isbnInputs.forEach(input => {
        input.addEventListener('blur', validateISBN);
        input.addEventListener('input', debounce(checkISBNExists, 500));
    });

    // Validação de formulários antes do submit
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
    });
}

function validateEmail(event) {
    const input = event.target;
    const email = input.value.trim();
    const emailRegex = /^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$/;
    
    clearValidationMessage(input);
    
    if (email && !emailRegex.test(email)) {
        showValidationError(input, 'Formato de email inválido.');
        return false;
    }
    
    if (email) {
        showValidationSuccess(input, 'Email válido.');
    }
    
    return true;
}

function validatePassword(event) {
    const input = event.target;
    const password = input.value;
    
    clearValidationMessage(input);
    
    if (password.length > 0 && password.length < 6) {
        showValidationError(input, 'Password deve ter pelo menos 6 caracteres.');
        return false;
    }
    
    if (password.length >= 6) {
        showValidationSuccess(input, 'Password válida.');
    }
    
    return true;
}

function validatePasswordConfirmation(event) {
    const input = event.target;
    const confirmPassword = input.value;
    const passwordInput = document.querySelector('input[name="password"], input[name="new_password"]');
    
    if (!passwordInput) return true;
    
    const password = passwordInput.value;
    
    clearValidationMessage(input);
    
    if (confirmPassword && password !== confirmPassword) {
        showValidationError(input, 'As passwords não coincidem.');
        return false;
    }
    
    if (confirmPassword && password === confirmPassword) {
        showValidationSuccess(input, 'Passwords coincidem.');
    }
    
    return true;
}

function validateISBN(event) {
    const input = event.target;
    const isbn = input.value.trim();
    
    clearValidationMessage(input);
    
    // ISBN é opcional, apenas validar se foi preenchido
    if (isbn && isbn.length > 0) {
        if (isValidISBN(isbn)) {
            showValidationSuccess(input, 'ISBN válido.');
            return true;
        } else {
            // Apenas aviso, não bloqueia o envio
            showValidationWarning(input, 'Formato de ISBN pode estar incorreto (opcional).');
            return true; // Permite continuar mesmo com formato incorreto
        }
    }
    
    // Campo vazio é válido
    input.classList.remove('is-invalid', 'is-valid');
    return true;
}

function isValidISBN(isbn) {
    // Remove hífens e espaços
    isbn = isbn.replace(/[-\s]/g, '');
    
    // Verificar se é ISBN-10 ou ISBN-13
    if (isbn.length === 10) {
        return isValidISBN10(isbn);
    } else if (isbn.length === 13) {
        return isValidISBN13(isbn);
    }
    
    return false;
}

function isValidISBN10(isbn) {
    if (!/^\d{9}[\dX]$/.test(isbn)) return false;
    
    let sum = 0;
    for (let i = 0; i < 9; i++) {
        sum += parseInt(isbn[i]) * (10 - i);
    }
    
    const checkDigit = isbn[9] === 'X' ? 10 : parseInt(isbn[9]);
    return (sum + checkDigit) % 11 === 0;
}

function isValidISBN13(isbn) {
    if (!/^\d{13}$/.test(isbn)) return false;
    
    let sum = 0;
    for (let i = 0; i < 12; i++) {
        sum += parseInt(isbn[i]) * (i % 2 === 0 ? 1 : 3);
    }
    
    const checkDigit = parseInt(isbn[12]);
    return (sum + checkDigit) % 10 === 0;
}

function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            showValidationError(input, 'Este campo é obrigatório.');
            isValid = false;
        }
    });
    
    return isValid;
}

// ===== FUNÇÕES DE VALIDAÇÃO VISUAL =====
function showValidationError(input, message) {
    input.classList.remove('is-valid');
    input.classList.add('is-invalid');
    
    let feedback = input.parentNode.querySelector('.invalid-feedback');
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        input.parentNode.appendChild(feedback);
    }
    feedback.textContent = message;
}

function showValidationSuccess(input, message) {
    input.classList.remove('is-invalid', 'is-warning');
    input.classList.add('is-valid');
    
    let feedback = input.parentNode.querySelector('.valid-feedback');
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.className = 'valid-feedback';
        input.parentNode.appendChild(feedback);
    }
    feedback.textContent = message;
}

function showValidationWarning(input, message) {
    input.classList.remove('is-invalid', 'is-valid');
    input.classList.add('is-warning');
    
    let feedback = input.parentNode.querySelector('.warning-feedback');
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.className = 'warning-feedback text-warning';
        feedback.style.fontSize = '0.875em';
        feedback.style.marginTop = '0.25rem';
        input.parentNode.appendChild(feedback);
    }
    feedback.textContent = message;
}

function clearValidationMessage(input) {
    input.classList.remove('is-valid', 'is-invalid', 'is-warning');
    
    const invalidFeedback = input.parentNode.querySelector('.invalid-feedback');
    const validFeedback = input.parentNode.querySelector('.valid-feedback');
    const warningFeedback = input.parentNode.querySelector('.warning-feedback');
    
    if (invalidFeedback) invalidFeedback.remove();
    if (validFeedback) validFeedback.remove();
    if (warningFeedback) warningFeedback.remove();
}

// ===== VERIFICAÇÕES AJAX =====
function checkEmailExists(event) {
    const input = event.target;
    const email = input.value.trim().toLowerCase();
    
    if (!email || !validateEmail(event)) return;
    
    fetch('/check-email', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: email })
    })
    .then(response => response.json())
    .then(data => {
        if (data.exists) {
            showValidationError(input, 'Este email já está registado.');
        } else {
            showValidationSuccess(input, 'Email disponível.');
        }
    })
    .catch(error => {
        console.error('Erro ao verificar email:', error);
    });
}

function checkISBNExists(event) {
    const input = event.target;
    const isbn = input.value.trim();
    
    // ISBN é opcional, não verificar se vazio
    if (!isbn) return;
    
    // Validar primeiro, mas não bloquear
    validateISBN(event);
    
    fetch('/check-isbn', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ isbn: isbn })
    })
    .then(response => response.json())
    .then(data => {
        if (data.exists) {
            showValidationWarning(input, 'Este ISBN já está registado (opcional).');
        } else if (isValidISBN(isbn)) {
            showValidationSuccess(input, 'ISBN disponível.');
        }
    })
    .catch(error => {
        console.error('Erro ao verificar ISBN:', error);
    });
}

// ===== TOOLTIPS E POPOVERS =====
function initializeTooltips() {
    // Inicializar tooltips do Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Inicializar popovers do Bootstrap
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// ===== FUNCIONALIDADES DE PESQUISA =====
function initializeSearchFeatures() {
    // Auto-submit do formulário de pesquisa após delay
    const searchInputs = document.querySelectorAll('input[name="search"]');
    searchInputs.forEach(input => {
        input.addEventListener('input', debounce(function() {
            if (input.value.length >= 3 || input.value.length === 0) {
                input.closest('form').submit();
            }
        }, 1000));
    });
    
    // Limpar pesquisa
    const clearSearchButtons = document.querySelectorAll('.clear-search');
    clearSearchButtons.forEach(button => {
        button.addEventListener('click', function() {
            const form = this.closest('form');
            const searchInput = form.querySelector('input[name="search"]');
            if (searchInput) {
                searchInput.value = '';
                form.submit();
            }
        });
    });
}

// ===== GRÁFICOS (CHART.JS) =====
function initializeCharts() {
    // Gráfico de empréstimos mensais
    const monthlyChartCanvas = document.getElementById('monthlyChart');
    if (monthlyChartCanvas && typeof Chart !== 'undefined') {
        createMonthlyChart(monthlyChartCanvas);
    }
    
    // Gráfico de categorias
    const categoriesChartCanvas = document.getElementById('categoriesChart');
    if (categoriesChartCanvas && typeof Chart !== 'undefined') {
        createCategoriesChart(categoriesChartCanvas);
    }
}

function createMonthlyChart(canvas) {
    const ctx = canvas.getContext('2d');
    
    // Dados do gráfico (serão passados do template)
    const chartData = window.chartData || { labels: [], emprestimos: [], devolucoes: [], atrasos: [] };
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Empréstimos',
                data: chartData.emprestimos,
                borderColor: '#2E4032',
                backgroundColor: 'rgba(46, 64, 50, 0.1)',
                tension: 0.4
            }, {
                label: 'Devoluções',
                data: chartData.devolucoes,
                borderColor: '#28A745',
                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                tension: 0.4
            }, {
                label: 'Atrasos',
                data: chartData.atrasos,
                borderColor: '#DC3545',
                backgroundColor: 'rgba(220, 53, 69, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Estatísticas Mensais de Empréstimos'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function createCategoriesChart(canvas) {
    const ctx = canvas.getContext('2d');
    
    // Dados do gráfico (serão passados do template)
    const categoriesData = window.categoriesChart || { labels: [], data: [] };
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: categoriesData.labels,
            datasets: [{
                data: categoriesData.data,
                backgroundColor: [
                    '#2E4032',
                    '#D4AF37',
                    '#28A745',
                    '#17A2B8',
                    '#FFC107',
                    '#DC3545',
                    '#6C757D',
                    '#6F42C1'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Categorias Mais Populares'
                },
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// ===== FORMULÁRIOS AJAX =====
function initializeAjaxForms() {
    // Formulários de empréstimo/devolução via AJAX
    const loanForms = document.querySelectorAll('.loan-form');
    loanForms.forEach(form => {
        form.addEventListener('submit', handleLoanFormSubmit);
    });
}

function handleLoanFormSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const button = form.querySelector('button[type="submit"]');
    
    // Mostrar loading
    button.disabled = true;
    button.innerHTML = '<span class="spinner-custom me-2"></span>Processando...';
    
    fetch(form.action, {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.ok) {
            location.reload(); // Recarregar página para mostrar mudanças
        } else {
            throw new Error('Erro na requisição');
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao processar solicitação. Tente novamente.');
    })
    .finally(() => {
        button.disabled = false;
        button.innerHTML = button.dataset.originalText || 'Submeter';
    });
}

// ===== UTILITÁRIOS =====
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.container');
    if (!alertContainer) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        <i class="fas fa-info-circle me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.insertBefore(alert, alertContainer.firstChild);
    
    // Auto-remover após 5 segundos
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

// ===== CONFIRMAÇÕES =====
function confirmDelete(message = 'Tem certeza que deseja eliminar este item?') {
    return confirm(message);
}

// Adicionar confirmação a links/botões de eliminação
document.addEventListener('click', function(event) {
    if (event.target.matches('.btn-delete, .delete-link')) {
        if (!confirmDelete()) {
            event.preventDefault();
        }
    }
});

// ===== EXPORTAR FUNÇÕES GLOBAIS =====
window.WebLibrary = {
    showAlert,
    confirmDelete,
    validateEmail,
    validatePassword,
    isValidISBN
};

