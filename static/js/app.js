// State management
let state = {
    productos: [],
    categorias: [],
    areas: [],
    transacciones: [],
    selectedProduct: null
};

// --- DOM ELEMENTS ---
const elements = {
    body: document.body,
    themeToggle: document.getElementById('theme-toggle'),
    themeToggleText: document.querySelector('.theme-toggle-text'),
    btnLogout: document.getElementById('btn-logout'),
    btnOpenChangePw: document.getElementById('btn-open-change-pw'),
    btnCloseChangePw: document.getElementById('btn-close-change-pw'),
    changePwModal: document.getElementById('change-pw-modal'),
    changePwForm: document.getElementById('change-pw-form'),
    userDisplayName: document.getElementById('user-display-name'),
    
    // Nav Items
    navItems: document.querySelectorAll('.menu-item'),
    sections: document.querySelectorAll('.page-section'),
    pageTitle: document.getElementById('page-title'),
    pageSubtitle: document.getElementById('page-subtitle'),
    
    // Dashboard
    kpiTotalProducts: document.getElementById('kpi-total-products'),
    kpiTotalStock: document.getElementById('kpi-total-stock'),
    kpiLowStock: document.getElementById('kpi-low-stock'),
    lowStockBadge: document.getElementById('low-stock-count-badge'),
    dashboardLowStockList: document.getElementById('dashboard-low-stock-list'),
    dashboardRecentActivity: document.getElementById('dashboard-recent-activity'),
    
    // Inventory
    inventorySearch: document.getElementById('inventory-search'),
    inventoryCategoryFilter: document.getElementById('inventory-category-filter'),
    inventoryTableBody: document.getElementById('inventory-table-body'),
    btnOpenAddProduct: document.getElementById('btn-open-add-product'),
    btnCloseAddProduct: document.getElementById('btn-close-add-product'),
    addProductModal: document.getElementById('add-product-modal'),
    addProductForm: document.getElementById('add-product-form'),
    categoriesDatalist: document.getElementById('categories-datalist'),
    
    // Transactions
    transactionForm: document.getElementById('transaction-form'),
    transTypeRadios: document.querySelectorAll('input[name="trans-type"]'),
    transProductSearch: document.getElementById('trans-product-search'),
    transProductId: document.getElementById('trans-product-id'),
    transAutocompleteList: document.getElementById('trans-autocomplete-list'),
    transQuantity: document.getElementById('trans-quantity'),
    targetAreaGroup: document.getElementById('target-area-group'),
    transArea: document.getElementById('trans-area'),
    areasDatalist: document.getElementById('areas-datalist'),
    stockPreview: document.getElementById('selected-product-stock-preview'),
    
    // History
    historySearch: document.getElementById('history-search'),
    historyTypeFilter: document.getElementById('history-type-filter'),
    historyTableBody: document.getElementById('history-table-body'),
    
    // Report Filters
    repFilterProduct: document.getElementById('rep-filter-product'),
    repFilterArea: document.getElementById('rep-filter-area'),
    repFilterType: document.getElementById('rep-filter-type'),
    repFilterDateStart: document.getElementById('rep-filter-date-start'),
    repFilterDateEnd: document.getElementById('rep-filter-date-end'),
    btnClearRepFilters: document.getElementById('btn-clear-rep-filters'),
    btnStockPdf: document.getElementById('btn-download-stock-pdf'),
    btnStockExcel: document.getElementById('btn-download-stock-excel'),
    btnMovsPdf: document.getElementById('btn-download-movs-pdf'),
    btnMovsExcel: document.getElementById('btn-download-movs-excel'),
    btnRefreshInventory: document.getElementById('btn-refresh-inventory'),
    btnRefreshHistory: document.getElementById('btn-refresh-history'),
    
    // Toast Container
    toastContainer: document.getElementById('toast-container')
};

// --- INITIALIZATION ---
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    setupEventListeners();
    handleRouting();
    loadAppData();
});

// --- THEME MANAGEMENT ---
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    if (savedTheme === 'light') {
        elements.body.classList.remove('dark-theme');
        elements.body.classList.add('light-theme');
        elements.themeToggleText.textContent = 'Modo Oscuro';
    } else {
        elements.body.classList.remove('light-theme');
        elements.body.classList.add('dark-theme');
        elements.themeToggleText.textContent = 'Modo Claro';
    }
}

function toggleTheme() {
    if (elements.body.classList.contains('dark-theme')) {
        elements.body.classList.remove('dark-theme');
        elements.body.classList.add('light-theme');
        elements.themeToggleText.textContent = 'Modo Oscuro';
        localStorage.setItem('theme', 'light');
        showToast('Modo claro activado', 'success');
    } else {
        elements.body.classList.remove('light-theme');
        elements.body.classList.add('dark-theme');
        elements.themeToggleText.textContent = 'Modo Claro';
        localStorage.setItem('theme', 'dark');
        showToast('Modo oscuro activado', 'success');
    }
}

// --- TOAST NOTIFICATIONS ---
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    toast.innerHTML = `
        <span class="toast-message">${message}</span>
        <button class="toast-close">&times;</button>
    `;
    
    elements.toastContainer.appendChild(toast);
    
    // Close on button click
    toast.querySelector('.toast-close').addEventListener('click', () => {
        toast.remove();
    });
    
    // Auto remove
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.2s reverse forwards';
        setTimeout(() => toast.remove(), 200);
    }, 4000);
}

// --- NAVIGATION & ROUTING ---
function handleRouting() {
    let hash = window.location.hash.substring(1);
    if (!hash || !['dashboard', 'inventario', 'movimientos', 'historial', 'reportes'].includes(hash)) {
        hash = 'dashboard';
        window.location.hash = '#dashboard';
    }
    switchTab(hash);
}

function switchTab(tabId) {
    // Update Sidebar links
    elements.navItems.forEach(item => {
        if (item.getAttribute('href') === `#${tabId}`) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });

    // Update visible section
    elements.sections.forEach(sec => {
        if (sec.id === `section-${tabId}`) {
            sec.classList.add('active');
        } else {
            sec.classList.remove('active');
        }
    });

    // Update titles
    const titles = {
        dashboard: { title: 'Dashboard', subtitle: 'Información general y alertas del depósito' },
        inventario: { title: 'Inventario', subtitle: 'Listado completo y control de stock' },
        movimientos: { title: 'Registrar Movimiento', subtitle: 'Carga ingresos y despachos a áreas' },
        historial: { title: 'Historial', subtitle: 'Registro cronológico de movimientos' },
        reportes: { title: 'Generación de Reportes', subtitle: 'Exportar a formatos de hojas de cálculo o impresión' }
    };

    if (titles[tabId]) {
        elements.pageTitle.textContent = titles[tabId].title;
        elements.pageSubtitle.textContent = titles[tabId].subtitle;
    }

    // Refresh tab-specific data
    if (tabId === 'dashboard') {
        renderDashboard();
    } else if (tabId === 'inventario') {
        renderInventoryTable();
    } else if (tabId === 'historial') {
        renderHistoryTable();
    }
}

// --- EVENT LISTENERS ---
function setupEventListeners() {
    // Theme toggle
    elements.themeToggle.addEventListener('click', toggleTheme);

    // Hash routing
    window.addEventListener('hashchange', handleRouting);

    // Modal Control
    elements.btnOpenAddProduct.addEventListener('click', () => {
        elements.addProductModal.classList.add('active');
        document.getElementById('prod-name').focus();
    });

    elements.btnCloseAddProduct.addEventListener('click', () => {
        elements.addProductModal.classList.remove('active');
        elements.addProductForm.reset();
    });

    // Close modal on click outside
    elements.addProductModal.addEventListener('click', (e) => {
        if (e.target === elements.addProductModal) {
            elements.addProductModal.classList.remove('active');
            elements.addProductForm.reset();
        }
    });

    // Form Add Product Submit
    elements.addProductForm.addEventListener('submit', handleAddProduct);

    // Search and Filter Inventory
    let inventoryDebounce;
    elements.inventorySearch.addEventListener('input', () => {
        clearTimeout(inventoryDebounce);
        inventoryDebounce = setTimeout(() => {
            renderInventoryTable();
        }, 200);
    });

    elements.inventoryCategoryFilter.addEventListener('change', renderInventoryTable);

    // Search and Filter History
    let historyDebounce;
    elements.historySearch.addEventListener('input', () => {
        clearTimeout(historyDebounce);
        historyDebounce = setTimeout(() => {
            renderHistoryTable();
        }, 200);
    });

    elements.historyTypeFilter.addEventListener('change', renderHistoryTable);

    // Transaction Form type toggle
    elements.transTypeRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            const container = e.target.closest('.operation-type-toggle');
            container.querySelectorAll('.toggle-option').forEach(opt => opt.classList.remove('active'));
            e.target.closest('.toggle-option').classList.add('active');

            if (e.target.value === 'salida') {
                elements.targetAreaGroup.classList.remove('hidden');
                elements.transArea.setAttribute('required', 'required');
            } else {
                elements.targetAreaGroup.classList.add('hidden');
                elements.transArea.removeAttribute('required');
                elements.transArea.value = '';
            }
        });
    });

    // Autocomplete Product Search in Transactions (optimized to run 100% locally from client-side cache)
    elements.transProductSearch.addEventListener('input', (e) => {
        const val = e.target.value.trim().toLowerCase();
        
        // Reset selected product if they edit search
        if (state.selectedProduct && e.target.value !== state.selectedProduct.nombre) {
            resetSelectedProduct();
        }

        if (val.length < 1) {
            elements.transAutocompleteList.classList.remove('active');
            return;
        }

        // Filter local products list instantaneously
        const matches = state.productos.filter(p => 
            p.nombre.toLowerCase().includes(val) || 
            p.id.toString() === val
        );
        renderAutocompleteDropdown(matches);
    });

    // Refresh Inventory List Button
    if (elements.btnRefreshInventory) {
        elements.btnRefreshInventory.addEventListener('click', async () => {
            try {
                const btn = elements.btnRefreshInventory;
                btn.style.opacity = '0.7';
                btn.querySelector('span').textContent = 'Cargando...';
                await fetchProducts();
                await fetchCategories();
                renderInventoryTable();
                btn.style.opacity = '1';
                btn.querySelector('span').textContent = 'Actualizar';
                showToast('Inventario de stock sincronizado', 'success');
            } catch (err) {
                showToast('Error al actualizar inventario', 'error');
            }
        });
    }

    // Refresh History List Button
    if (elements.btnRefreshHistory) {
        elements.btnRefreshHistory.addEventListener('click', async () => {
            try {
                const btn = elements.btnRefreshHistory;
                btn.style.opacity = '0.7';
                btn.querySelector('span').textContent = 'Cargando...';
                await fetchTransactions();
                renderHistoryTable();
                btn.style.opacity = '1';
                btn.querySelector('span').textContent = 'Actualizar';
                showToast('Historial de movimientos sincronizado', 'success');
            } catch (err) {
                showToast('Error al actualizar historial', 'error');
            }
        });
    }

    // Close autocomplete when clicking outside
    document.addEventListener('click', (e) => {
        if (e.target !== elements.transProductSearch && e.target !== elements.transAutocompleteList) {
            elements.transAutocompleteList.classList.remove('active');
        }
    });

    // Submit transaction
    elements.transactionForm.addEventListener('submit', handleTransactionSubmit);

    // Logout button handler
    if (elements.btnLogout) {
        elements.btnLogout.addEventListener('click', async () => {
            try {
                const response = await fetch('/api/logout', { method: 'POST' });
                if (response.ok) {
                    window.location.href = '/login';
                } else {
                    showToast('Error al cerrar sesión', 'error');
                }
            } catch (err) {
                showToast('Error de conexión', 'error');
            }
        });
    }

    // Modal Change Password Control
    if (elements.btnOpenChangePw) {
        elements.btnOpenChangePw.addEventListener('click', () => {
            elements.changePwModal.classList.add('active');
            document.getElementById('pw-actual').focus();
        });
    }

    if (elements.btnCloseChangePw) {
        elements.btnCloseChangePw.addEventListener('click', () => {
            elements.changePwModal.classList.remove('active');
            elements.changePwForm.reset();
        });
    }

    if (elements.changePwModal) {
        elements.changePwModal.addEventListener('click', (e) => {
            if (e.target === elements.changePwModal) {
                elements.changePwModal.classList.remove('active');
                elements.changePwForm.reset();
            }
        });
    }

    if (elements.changePwForm) {
        elements.changePwForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const password_actual = document.getElementById('pw-actual').value;
            const password_nuevo = document.getElementById('pw-nuevo').value;

            try {
                const response = await fetch('/api/cambiar-password', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ password_actual, password_nuevo })
                });
                const result = await response.json();
                if (response.ok) {
                    showToast(result.message, 'success');
                    elements.changePwModal.classList.remove('active');
                    elements.changePwForm.reset();
                } else {
                    showToast(result.error || 'Error al cambiar contraseña', 'error');
                }
            } catch (err) {
                showToast('Error de conexión', 'error');
            }
        });
    }

    // Intercept Report Downloads to add query parameters and separate stock / movements
    if (elements.btnStockPdf) {
        elements.btnStockPdf.addEventListener('click', (e) => {
            e.preventDefault();
            window.location.href = `/api/reportes/pdf?tipo=stock`;
        });
    }

    if (elements.btnStockExcel) {
        elements.btnStockExcel.addEventListener('click', (e) => {
            e.preventDefault();
            window.location.href = `/api/reportes/excel?tipo=stock`;
        });
    }

    if (elements.btnMovsPdf) {
        elements.btnMovsPdf.addEventListener('click', (e) => {
            e.preventDefault();
            const prodId = elements.repFilterProduct.value;
            const area = elements.repFilterArea.value;
            const movType = elements.repFilterType.value;
            const dateStart = elements.repFilterDateStart.value;
            const dateEnd = elements.repFilterDateEnd.value;
            
            const params = new URLSearchParams();
            params.append('tipo', 'movimientos');
            if (prodId) params.append('producto_id', prodId);
            if (area) params.append('area', area);
            if (movType) params.append('tipo_movimiento', movType);
            if (dateStart) params.append('fecha_inicio', dateStart);
            if (dateEnd) params.append('fecha_fin', dateEnd);
            
            window.location.href = `/api/reportes/pdf?${params.toString()}`;
        });
    }

    if (elements.btnMovsExcel) {
        elements.btnMovsExcel.addEventListener('click', (e) => {
            e.preventDefault();
            const prodId = elements.repFilterProduct.value;
            const area = elements.repFilterArea.value;
            const movType = elements.repFilterType.value;
            const dateStart = elements.repFilterDateStart.value;
            const dateEnd = elements.repFilterDateEnd.value;
            
            const params = new URLSearchParams();
            params.append('tipo', 'movimientos');
            if (prodId) params.append('producto_id', prodId);
            if (area) params.append('area', area);
            if (movType) params.append('tipo_movimiento', movType);
            if (dateStart) params.append('fecha_inicio', dateStart);
            if (dateEnd) params.append('fecha_fin', dateEnd);
            
            window.location.href = `/api/reportes/excel?${params.toString()}`;
        });
    }

    // Clear Report Filters
    if (elements.btnClearRepFilters) {
        elements.btnClearRepFilters.addEventListener('click', () => {
            elements.repFilterProduct.value = '';
            elements.repFilterArea.value = '';
            elements.repFilterType.value = '';
            elements.repFilterDateStart.value = '';
            elements.repFilterDateEnd.value = '';
            showToast('Filtros de reporte limpiados', 'success');
        });
    }
}

// --- DATA FETCHING & APP LOADING ---
async function loadAppData() {
    try {
        await Promise.all([
            fetchProducts(),
            fetchCategories(),
            fetchAreas(),
            fetchTransactions()
        ]);
        populateReportFilters();
        
        // Fetch session status to show correct user name
        try {
            const sessRes = await fetch('/api/session-status');
            if (sessRes.ok) {
                const sessData = await sessRes.json();
                if (elements.userDisplayName && sessData.nombre) {
                    elements.userDisplayName.textContent = sessData.nombre;
                }
            }
        } catch (e) {
            console.error("Error fetching session status", e);
        }
        
        // Initial tab render
        handleRouting();
    } catch (err) {
        showToast('Error de conexión con el servidor', 'error');
        console.error(err);
    }
}

async function fetchProducts() {
    const response = await fetch('/api/productos');
    state.productos = await response.json();
    updateDatalists();
    populateReportFilters();
}

async function fetchCategories() {
    const response = await fetch('/api/categorias');
    state.categorias = await response.json();
    populateCategoryDropdowns();
}

async function fetchAreas() {
    const response = await fetch('/api/areas');
    state.areas = await response.json();
    populateAreasDatalist();
    populateReportFilters();
}

async function fetchTransactions() {
    const response = await fetch('/api/transacciones');
    state.transacciones = await response.json();
}

// --- DATA LIST POPULATION ---
function populateCategoryDropdowns() {
    // 1. Inventory Filter
    const currentVal = elements.inventoryCategoryFilter.value;
    elements.inventoryCategoryFilter.innerHTML = '<option value="">Todas las categorías</option>';
    state.categorias.forEach(cat => {
        const option = document.createElement('option');
        option.value = cat;
        option.textContent = cat;
        elements.inventoryCategoryFilter.appendChild(option);
    });
    elements.inventoryCategoryFilter.value = currentVal;

    // 2. Modal Suggestions Datalist
    elements.categoriesDatalist.innerHTML = '';
    state.categorias.forEach(cat => {
        const option = document.createElement('option');
        option.value = cat;
        elements.categoriesDatalist.appendChild(option);
    });
}

function populateAreasDatalist() {
    elements.areasDatalist.innerHTML = '';
    state.areas.forEach(area => {
        const option = document.createElement('option');
        option.value = area;
        elements.areasDatalist.appendChild(option);
    });
}

function populateReportFilters() {
    if (!elements.repFilterProduct || !elements.repFilterArea) return;
    
    // Populate Products
    const prodVal = elements.repFilterProduct.value;
    elements.repFilterProduct.innerHTML = '<option value="">Todos los productos</option>';
    state.productos.forEach(prod => {
        const option = document.createElement('option');
        option.value = prod.id;
        option.textContent = `[ID ${prod.id}] ${prod.nombre}`;
        elements.repFilterProduct.appendChild(option);
    });
    elements.repFilterProduct.value = prodVal;

    // Populate Areas
    const areaVal = elements.repFilterArea.value;
    elements.repFilterArea.innerHTML = '<option value="">Todas las áreas</option>';
    state.areas.forEach(area => {
        const option = document.createElement('option');
        option.value = area;
        option.textContent = area;
        elements.repFilterArea.appendChild(option);
    });
    elements.repFilterArea.value = areaVal;
}

function updateDatalists() {
    // Dynamic updates if needed, e.g. for products autocompletes
}

// --- AUTOCOMPLETE RENDER ---
function renderAutocompleteDropdown(matches) {
    if (matches.length === 0) {
        elements.transAutocompleteList.innerHTML = '<div style="padding: 10px 16px; color: var(--text-muted); font-style: italic;">No se encontraron productos</div>';
    } else {
        elements.transAutocompleteList.innerHTML = '';
        matches.forEach(item => {
            const div = document.createElement('div');
            div.className = 'autocomplete-item';
            div.innerHTML = `
                <span class="autocomplete-item-name">${item.nombre} </span>
                <span class="autocomplete-item-category">Stock: ${item.cantidad} • ${item.categoria}</span>
            `;
            div.addEventListener('click', () => {
                selectProductForTransaction(item);
            });
            elements.transAutocompleteList.appendChild(div);
        });
    }
    elements.transAutocompleteList.classList.add('active');
}

function selectProductForTransaction(product) {
    state.selectedProduct = product;
    elements.transProductSearch.value = product.nombre;
    elements.transProductId.value = product.id;
    elements.transAutocompleteList.classList.remove('active');
    
    // Show current stock preview
    elements.stockPreview.textContent = `Stock disponible: ${product.cantidad} unidades (Stock Mínimo: ${product.stock_minimo}).`;
    
    // Set max quantity if it's a delivery
    const isSalida = document.querySelector('input[name="trans-type"]:checked').value === 'salida';
    if (isSalida) {
        elements.transQuantity.setAttribute('max', product.cantidad);
    } else {
        elements.transQuantity.removeAttribute('max');
    }
}

function resetSelectedProduct() {
    state.selectedProduct = null;
    elements.transProductId.value = '';
    elements.stockPreview.textContent = '';
    elements.transQuantity.removeAttribute('max');
}

// --- FORM HANDLERS ---
async function handleAddProduct(e) {
    e.preventDefault();
    const formData = new FormData(elements.addProductForm);
    const body = {
        nombre: formData.get('nombre'),
        categoria: formData.get('categoria'),
        cantidad_inicial: formData.get('cantidad_inicial'),
        stock_minimo: formData.get('stock_minimo')
    };

    try {
        const response = await fetch('/api/productos', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        const result = await response.json();
        
        if (response.ok) {
            showToast(result.message, 'success');
            elements.addProductModal.classList.remove('active');
            elements.addProductForm.reset();
            
            // Reload all structures
            await loadAppData();
        } else {
            showToast(result.error || 'Ocurrió un error', 'error');
        }
    } catch (err) {
        showToast('Error de conexión', 'error');
        console.error(err);
    }
}

async function handleTransactionSubmit(e) {
    e.preventDefault();
    
    const producto_id = elements.transProductId.value;
    if (!producto_id) {
        showToast('Debes seleccionar un producto válido de la lista de autocompletado.', 'error');
        elements.transProductSearch.focus();
        return;
    }

    const tipo = document.querySelector('input[name="trans-type"]:checked').value;
    const cantidad = parseInt(elements.transQuantity.value);
    const area_destino = elements.transArea.value;

    // Frontend validation for stock shortage
    if (tipo === 'salida' && state.selectedProduct && cantidad > state.selectedProduct.cantidad) {
        showToast(`Stock insuficiente. Solo hay ${state.selectedProduct.cantidad} unidades disponibles.`, 'error');
        elements.transQuantity.focus();
        return;
    }

    const body = {
        producto_id,
        tipo,
        cantidad,
        area_destino: tipo === 'salida' ? area_destino : ''
    };

    try {
        const response = await fetch('/api/transacciones', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        const result = await response.json();

        if (response.ok) {
            showToast(result.message, 'success');
            elements.transactionForm.reset();
            resetSelectedProduct();
            
            // Reset radio toggles to 'entrada' default view
            document.querySelector('input[name="trans-type"][value="entrada"]').click();
            
            // Reload all
            await loadAppData();
        } else {
            showToast(result.error || 'Error al procesar el movimiento', 'error');
        }
    } catch (err) {
        showToast('Error de conexión', 'error');
        console.error(err);
    }
}

// --- RENDER FUNCTIONS ---

// 1. Dashboard View
function renderDashboard() {
    const totalProd = state.productos.length;
    const totalStock = state.productos.reduce((acc, p) => acc + p.cantidad, 0);
    
    // Filter items with low or empty stock
    const lowStockItems = state.productos.filter(p => p.cantidad <= p.stock_minimo);
    const lowStockCount = lowStockItems.length;

    // Populate KPIs
    elements.kpiTotalProducts.textContent = totalProd;
    elements.kpiTotalStock.textContent = totalStock;
    elements.kpiLowStock.textContent = lowStockCount;
    
    elements.lowStockBadge.textContent = lowStockCount;
    if (lowStockCount > 0) {
        elements.lowStockBadge.classList.remove('hidden');
    } else {
        elements.lowStockBadge.classList.add('hidden');
    }

    // Populate Low Stock Critical Panel
    elements.dashboardLowStockList.innerHTML = '';
    if (lowStockItems.length === 0) {
        elements.dashboardLowStockList.innerHTML = '<li class="empty-state">No hay alertas de stock bajo. ¡Buen trabajo!</li>';
    } else {
        lowStockItems.forEach(p => {
            const li = document.createElement('li');
            li.className = p.cantidad === 0 ? 'alert-item' : 'alert-item alert-item-orange';
            
            const badgeClass = p.cantidad === 0 ? 'alert-badge-red' : 'alert-badge-orange';
            const badgeText = p.cantidad === 0 ? 'Sin Stock' : 'Stock Bajo';
            
            li.innerHTML = `
                <div class="alert-info">
                    <span class="alert-name">${p.nombre}</span>
                    <span class="alert-meta">Categoría: ${p.categoria} • ID: ${p.id}</span>
                </div>
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-weight: 500; font-size: 0.9rem;">Disponibles: <b>${p.cantidad}</b> (Mín: ${p.stock_minimo})</span>
                    <span class="alert-badge ${badgeClass}">${badgeText}</span>
                </div>
            `;
            elements.dashboardLowStockList.appendChild(li);
        });
    }

    // Populate Recent Activity Panel (last 6 items)
    elements.dashboardRecentActivity.innerHTML = '';
    const recent = state.transacciones.slice(0, 6);
    if (recent.length === 0) {
        elements.dashboardRecentActivity.innerHTML = '<li class="empty-state">No se registran movimientos recientes.</li>';
    } else {
        recent.forEach(t => {
            const li = document.createElement('li');
            li.className = 'activity-item';
            
            const isEntrada = t.tipo === 'entrada';
            const actionText = isEntrada 
                ? `Ingresaron <span>${t.cantidad}</span> unid.`
                : `Se entregaron <span>${t.cantidad}</span> unid.`;
            
            const detailText = isEntrada
                ? `al stock general.`
                : `al área <b>${t.area_destino}</b>.`;

            const parsedDate = formatRelativeTime(t.fecha);

            li.innerHTML = `
                <div class="activity-info">
                    <span class="activity-text"><b>${t.producto_nombre}</b>: ${actionText} ${detailText}</span>
                    <span class="activity-time">${parsedDate}</span>
                </div>
                <span class="activity-tag tag-${t.tipo}">${t.tipo.toUpperCase()}</span>
            `;
            elements.dashboardRecentActivity.appendChild(li);
        });
    }
}

// Helper to format date cleanly
function formatRelativeTime(dateStr) {
    // dateStr in "YYYY-MM-DD HH:MM:SS" format
    try {
        const parts = dateStr.split(/[- :]/);
        // month is 0-indexed in JS Date
        const date = new Date(parts[0], parts[1]-1, parts[2], parts[3], parts[4], parts[5]);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / (1000 * 60));
        
        if (diffMins < 1) return 'Hace unos momentos';
        if (diffMins < 60) return `Hace ${diffMins} min`;
        
        const diffHrs = Math.floor(diffMins / 60);
        if (diffHrs < 24) return `Hace ${diffHrs} horas`;
        
        return date.toLocaleString('es-AR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch (e) {
        return dateStr;
    }
}

// 2. Inventory Table
function renderInventoryTable() {
    const searchVal = elements.inventorySearch.value.trim().toLowerCase();
    const catVal = elements.inventoryCategoryFilter.value;

    elements.inventoryTableBody.innerHTML = '';
    
    // Filter list
    const filtered = state.productos.filter(p => {
        const matchesSearch = p.nombre.toLowerCase().includes(searchVal) || p.id.toString() === searchVal;
        const matchesCategory = catVal === '' || p.categoria === catVal;
        return matchesSearch && matchesCategory;
    });

    if (filtered.length === 0) {
        elements.inventoryTableBody.innerHTML = `
            <tr>
                <td colspan="7" class="empty-state">No se encontraron productos coincidentes en el inventario.</td>
            </tr>
        `;
        return;
    }

    filtered.forEach(p => {
        let statusBadge = '';
        if (p.cantidad === 0) {
            statusBadge = '<span class="badge badge-vacio">Sin Stock</span>';
        } else if (p.cantidad <= p.stock_minimo) {
            statusBadge = '<span class="badge badge-bajo">Stock Bajo</span>';
        } else {
            statusBadge = '<span class="badge badge-suficiente">Suficiente</span>';
        }

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><b>#${p.id}</b></td>
            <td style="font-weight: 500; color: var(--text-primary);">${p.nombre}</td>
            <td><span style="font-size: 0.9rem; color: var(--text-secondary); background: var(--bg-input); padding: 4px 8px; border-radius: 4px; border: 1px solid var(--border-color);">${p.categoria}</span></td>
            <td style="text-align: right; font-weight: 600;">${p.cantidad}</td>
            <td style="text-align: right; color: var(--text-muted);">${p.stock_minimo}</td>
            <td style="text-align: center;">${statusBadge}</td>
            <td style="text-align: center;">
                <button class="btn btn-delete" style="background: none; border: 1px solid rgba(244,63,94,0.3); color: var(--color-rose-500); padding: 4px 10px; border-radius: 4px; font-size: 0.8rem; cursor: pointer; font-weight: 600; display: inline-flex; align-items: center; justify-content: center; gap: 4px;" data-id="${p.id}" data-name="${p.nombre}">
                    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
                    <span>Eliminar</span>
                </button>
            </td>
        `;

        // Add event listener to the delete button
        tr.querySelector('.btn-delete').addEventListener('click', (e) => {
            const btn = e.currentTarget;
            const prodId = btn.getAttribute('data-id');
            const prodName = btn.getAttribute('data-name');
            handleDeleteProduct(prodId, prodName);
        });

        elements.inventoryTableBody.appendChild(tr);
    });
}

// 3. History Table
function renderHistoryTable() {
    const searchVal = elements.historySearch.value.trim().toLowerCase();
    const typeVal = elements.historyTypeFilter.value;

    elements.historyTableBody.innerHTML = '';

    const filtered = state.transacciones.filter(t => {
        const matchesSearch = t.producto_nombre.toLowerCase().includes(searchVal) || 
                              (t.area_destino && t.area_destino.toLowerCase().includes(searchVal)) ||
                              t.producto_id.toString() === searchVal;
        const matchesType = typeVal === '' || t.tipo === typeVal;
        return matchesSearch && matchesType;
    });

    if (filtered.length === 0) {
        elements.historyTableBody.innerHTML = `
            <tr>
                <td colspan="7" class="empty-state">No se registraron movimientos con los filtros seleccionados.</td>
            </tr>
        `;
        return;
    }

    filtered.forEach(t => {
        const isEntrada = t.tipo === 'entrada';
        const typeBadge = isEntrada 
            ? '<span class="activity-tag tag-entrada" style="font-size: 0.75rem;">ENTRADA</span>' 
            : '<span class="activity-tag tag-salida" style="font-size: 0.75rem;">SALIDA</span>';
            
        // Formato de fecha
        const dateObj = new Date(t.fecha.replace(' ', 'T'));
        const formattedDate = dateObj.toLocaleString('es-AR', {
            day: '2-digit', month: '2-digit', year: 'numeric',
            hour: '2-digit', minute: '2-digit', second: '2-digit'
        });

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>#${t.id}</td>
            <td>#${t.producto_id}</td>
            <td style="font-weight: 500;">${t.producto_nombre}</td>
            <td style="text-align: center;">${typeBadge}</td>
            <td style="text-align: right; font-weight: 600; color: ${isEntrada ? 'var(--color-emerald-500)' : 'var(--color-indigo-500)'}">${t.cantidad}</td>
            <td style="font-weight: 500;">${t.area_destino ? t.area_destino : '<span style="color: var(--text-muted); font-weight: normal;">- (Stock General)</span>'}</td>
            <td style="color: var(--text-muted); font-size: 0.9rem;">${formattedDate}</td>
        `;
        elements.historyTableBody.appendChild(tr);
    });
}

async function handleDeleteProduct(id, name) {
    const confirmed = confirm(`¿Estás seguro de que deseas eliminar el producto "${name}" (ID: ${id}) del inventario?\n\n¡ATENCIÓN! Esto eliminará de forma permanente todo el historial de movimientos de este producto.`);
    if (!confirmed) return;

    try {
        const response = await fetch(`/api/productos/${id}`, {
            method: 'DELETE'
        });
        const result = await response.json();
        
        if (response.ok) {
            showToast(result.message, 'success');
            await loadAppData();
        } else {
            showToast(result.error || 'Error al eliminar el producto', 'error');
        }
    } catch (err) {
        showToast('Error de conexión', 'error');
    }
}

