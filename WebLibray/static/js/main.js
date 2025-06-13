// ========== BIBLIOTECA MAIN JS ==========

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Initialize application
function initializeApp() {
    initializeNavigation();
    initializeFlashMessages();
    initializeForms();
    initializeCards();
    initializeTooltips();
    initializeMobileMenu();
    initializeSearchFilters();
    initializeDataTables();
    initializeCharts();
}

// ========== NAVIGATION ==========
function initializeNavigation() {
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navToggle.classList.toggle('active');
            navMenu.classList.toggle('active');
        });
    }
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', function(e) {
        if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {
            navToggle.classList.remove('active');
            navMenu.classList.remove('active');
        }
    });
    
    // Handle dropdown menus
    const dropdowns = document.querySelectorAll('.nav-dropdown');
    dropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        const menu = dropdown.querySelector('.dropdown-menu');
        
        if (toggle && menu) {
            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Close other dropdowns
                dropdowns.forEach(otherDropdown => {
                    if (otherDropdown !== dropdown) {
                        otherDropdown.querySelector('.dropdown-menu').style.opacity = '0';
                        otherDropdown.querySelector('.dropdown-menu').style.visibility = 'hidden';
                    }
                });
                
                // Toggle current dropdown
                const isVisible = menu.style.opacity === '1';
                menu.style.opacity = isVisible ? '0' : '1';
                menu.style.visibility = isVisible ? 'hidden' : 'visible';
            });
        }
    });
}

// ========== FLASH MESSAGES ==========
function initializeFlashMessages() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
        const closeBtn = alert.querySelector('.alert-close');
        
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                alert.style.animation = 'slideOutRight 0.3s ease';
                setTimeout(() => {
                    alert.remove();
                }, 300);
            });
        }
        
        // Auto close after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.style.animation = 'slideOutRight 0.3s ease';
                setTimeout(() => {
                    alert.remove();
                }, 300);
            }
        }, 5000);
    });
}

// ========== FORMS ==========
function initializeForms() {
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(form)) {
                e.preventDefault();
            }
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(input);
            });
            
            input.addEventListener('input', function() {
                clearFieldError(input);
            });
        });
    });
    
    // File input preview
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            handleFilePreview(input);
        });
    });
    
    // Confirm delete buttons
    const deleteButtons = document.querySelectorAll('.btn-danger[data-confirm]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = button.dataset.confirm || 'Tem certeza de que deseja eliminar?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    
    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });
    
    return isValid;
}

function validateField(field) {
    let isValid = true;
    let errorMessage = '';
    
    // Required validation
    if (field.hasAttribute('required') && !field.value.trim()) {
        isValid = false;
        errorMessage = 'Este campo é obrigatório.';
    }
    
    // Email validation
    if (field.type === 'email' && field.value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(field.value)) {
            isValid = false;
            errorMessage = 'Por favor, insira um email válido.';
        }
    }
    
    // Password validation
    if (field.type === 'password' && field.value) {
        if (field.value.length < 6) {
            isValid = false;
            errorMessage = 'A password deve ter pelo menos 6 caracteres.';
        }
    }
    
    // Confirm password validation
    if (field.name === 'confirm_password' && field.value) {
        const passwordField = document.querySelector('input[name="password"]');
        if (passwordField && field.value !== passwordField.value) {
            isValid = false;
            errorMessage = 'As passwords não coincidem.';
        }
    }
    
    // Show/hide error
    if (isValid) {
        clearFieldError(field);
    } else {
        showFieldError(field, errorMessage);
    }
    
    return isValid;
}

function showFieldError(field, message) {
    clearFieldError(field);
    
    field.classList.add('is-invalid');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.classList.remove('is-invalid');
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

function handleFilePreview(input) {
    const file = input.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            // Find existing preview or create new one
            let preview = input.parentNode.querySelector('.file-preview');
            if (!preview) {
                preview = document.createElement('div');
                preview.className = 'file-preview mt-2';
                input.parentNode.appendChild(preview);
            }
            
            if (file.type.startsWith('image/')) {
                preview.innerHTML = `
                    <img src="${e.target.result}" alt="Preview" style="max-width: 200px; max-height: 200px; border-radius: 0.5rem;">
                    <p class="mt-1 text-sm text-gray-600">${file.name}</p>
                `;
            } else {
                preview.innerHTML = `
                    <div class="d-flex align-items-center gap-2">
                        <i class="fas fa-file"></i>
                        <span>${file.name}</span>
                    </div>
                `;
            }
        };
        reader.readAsDataURL(file);
    }
}

// ========== CARDS ==========
function initializeCards() {
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
    
    // Interactive card hover effects
    const interactiveCards = document.querySelectorAll('.card[data-href]');
    interactiveCards.forEach(card => {
        card.style.cursor = 'pointer';
        card.addEventListener('click', function() {
            window.location.href = card.dataset.href;
        });
    });
}

// ========== TOOLTIPS ==========
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(e) {
    const element = e.target;
    const text = element.dataset.tooltip;
    
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = text;
    tooltip.style.cssText = `
        position: absolute;
        background: #333;
        color: white;
        padding: 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
        z-index: 1000;
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    
    document.body.appendChild(tooltip);
    
    const rect = element.getBoundingClientRect();
    tooltip.style.left = `${rect.left + rect.width / 2 - tooltip.offsetWidth / 2}px`;
    tooltip.style.top = `${rect.top - tooltip.offsetHeight - 5}px`;
    
    setTimeout(() => {
        tooltip.style.opacity = '1';
    }, 10);
    
    element._tooltip = tooltip;
}

function hideTooltip(e) {
    const element = e.target;
    if (element._tooltip) {
        element._tooltip.remove();
        element._tooltip = null;
    }
}

// ========== MOBILE MENU ==========
function initializeMobileMenu() {
    // Close mobile menu when clicking on a link
    const mobileLinks = document.querySelectorAll('.nav-menu .nav-link');
    mobileLinks.forEach(link => {
        link.addEventListener('click', function() {
            const navToggle = document.getElementById('navToggle');
            const navMenu = document.getElementById('navMenu');
            
            if (navToggle && navMenu) {
                navToggle.classList.remove('active');
                navMenu.classList.remove('active');
            }
        });
    });
}

// ========== SEARCH AND FILTERS ==========
function initializeSearchFilters() {
    const searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(input => {
        input.addEventListener('input', debounce(function() {
            const searchTerm = input.value.toLowerCase();
            const targetSelector = input.dataset.target;
            
            if (targetSelector) {
                const items = document.querySelectorAll(targetSelector);
                items.forEach(item => {
                    const text = item.textContent.toLowerCase();
                    item.style.display = text.includes(searchTerm) ? 'block' : 'none';
                });
            }
        }, 300));
    });
    
    // Filter dropdowns
    const filterSelects = document.querySelectorAll('.filter-select');
    filterSelects.forEach(select => {
        select.addEventListener('change', function() {
            const filterValue = select.value;
            const targetSelector = select.dataset.target;
            const filterAttribute = select.dataset.filter;
            
            if (targetSelector && filterAttribute) {
                const items = document.querySelectorAll(targetSelector);
                items.forEach(item => {
                    const itemValue = item.dataset[filterAttribute];
                    item.style.display = (!filterValue || itemValue === filterValue) ? 'block' : 'none';
                });
            }
        });
    });
}

// ========== DATA TABLES ==========
function initializeDataTables() {
    const tables = document.querySelectorAll('.data-table');
    tables.forEach(table => {
        makeTableSortable(table);
        addTableSearch(table);
    });
}

function makeTableSortable(table) {
    const headers = table.querySelectorAll('th[data-sort]');
    headers.forEach(header => {
        header.style.cursor = 'pointer';
        header.innerHTML += ' <i class="fas fa-sort"></i>';
        
        header.addEventListener('click', function() {
            const column = header.dataset.sort;
            const isAsc = header.classList.contains('sort-asc');
            
            // Remove sort classes from all headers
            headers.forEach(h => h.classList.remove('sort-asc', 'sort-desc'));
            
            // Add sort class to current header
            header.classList.add(isAsc ? 'sort-desc' : 'sort-asc');
            
            // Sort table
            sortTable(table, column, !isAsc);
        });
    });
}

function sortTable(table, column, ascending) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        const aValue = a.querySelector(`[data-value="${column}"]`)?.textContent || '';
        const bValue = b.querySelector(`[data-value="${column}"]`)?.textContent || '';
        
        if (ascending) {
            return aValue.localeCompare(bValue);
        } else {
            return bValue.localeCompare(aValue);
        }
    });
    
    rows.forEach(row => tbody.appendChild(row));
}

function addTableSearch(table) {
    const searchInput = table.parentNode.querySelector('.table-search');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            const searchTerm = searchInput.value.toLowerCase();
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? 'table-row' : 'none';
            });
        }, 300));
    }
}

// ========== CHARTS ==========
function initializeCharts() {
    // Simple chart implementation (can be replaced with Chart.js)
    const chartElements = document.querySelectorAll('.simple-chart');
    chartElements.forEach(element => {
        const data = JSON.parse(element.dataset.data || '[]');
        createSimpleChart(element, data);
    });
}

function createSimpleChart(element, data) {
    const maxValue = Math.max(...data.map(item => item.value));
    
    element.innerHTML = data.map(item => `
        <div class="chart-bar">
            <div class="bar-fill" style="height: ${(item.value / maxValue) * 100}%"></div>
            <div class="bar-label">${item.label}</div>
            <div class="bar-value">${item.value}</div>
        </div>
    `).join('');
}

// ========== UTILITY FUNCTIONS ==========
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

function showLoading(element) {
    const loader = document.createElement('div');
    loader.className = 'loading-spinner';
    loader.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    element.appendChild(loader);
}

function hideLoading(element) {
    const loader = element.querySelector('.loading-spinner');
    if (loader) {
        loader.remove();
    }
}

// ========== API HELPERS ==========
async function fetchData(url, options = {}) {
    try {
        showLoading(document.body);
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Fetch error:', error);
        showAlert('Erro ao carregar dados', 'error');
        return null;
    } finally {
        hideLoading(document.body);
    }
}

function showAlert(message, type = 'info') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <div class="alert-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
        <button class="alert-close">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    const container = document.querySelector('.flash-container') || document.body;
    container.appendChild(alert);
    
    // Initialize close button
    const closeBtn = alert.querySelector('.alert-close');
    closeBtn.addEventListener('click', function() {
        alert.remove();
    });
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

// ========== ANIMATIONS ==========
const animationCSS = `
    @keyframes slideOutRight {
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .loading-spinner {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 9999;
        color: var(--primary-color);
        font-size: 2rem;
    }
    
    .chart-bar {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin: 0.5rem;
        min-height: 100px;
    }
    
    .bar-fill {
        width: 30px;
        background: linear-gradient(135deg, var(--primary-color), var(--accent-3));
        border-radius: 0.25rem;
        transition: height 0.3s ease;
    }
    
    .bar-label {
        font-size: 0.875rem;
        margin-top: 0.25rem;
    }
    
    .bar-value {
        font-weight: 600;
        color: var(--accent-1);
    }
    
    .is-invalid {
        border-color: var(--danger) !important;
    }
    
    .invalid-feedback {
        color: var(--danger);
        font-size: 0.875rem;
        margin-top: 0.25rem;
    }
`;

// Inject animation CSS
const style = document.createElement('style');
style.textContent = animationCSS;
document.head.appendChild(style);

// ========== EXPORT ==========
window.BibliotecaApp = {
    showAlert,
    fetchData,
    showLoading,
    hideLoading,
    debounce
}; 