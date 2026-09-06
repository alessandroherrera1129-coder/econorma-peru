/**
 * EcoNorma Perú - Frontend Application Engine
 * Plataforma de Consulta de Estándares Ambientales del Perú
 * Single Page Application, Búsqueda Reactiva, Comparador y Sistema CRUD Administrativo Integral.
 */

const EcoNorma = (function() {
  // Estado Centralizado
  const state = {
    query: '',
    instrument: 'TODOS',
    medium: 'TODOS',
    sector: 'TODOS',
    category: 'TODOS',
    subcategory: 'TODOS',
    status: 'TODOS',
    normCode: 'TODOS',
    entity: 'TODOS',
    year: '',
    page: 1,
    pageSize: 20,
    totalResults: 0,
    results: [],
    viewMode: 'cards', // 'cards' | 'table'
    filterOptions: {},
    systemInfo: {},
    systemStats: {},
    adminToken: localStorage.getItem('econorma_admin_token') || '',
    activeTab: 'inicio',
    adminSubTab: 'parametros', // 'parametros' | 'normas' | 'pendientes' | 'historial' | 'mensajes' | 'importar'
    adminParamPage: 1,
    adminParamPageSize: 25,
    adminParamTotal: 0,
    adminNormsList: [],
    selectedParamForDetail: null,
    interCategoryChart: null,
    autocompleteSelectedIndex: -1,
    autocompleteItems: []
  };

  const dom = {};

  async function init() {
    cacheDomElements();
    initTheme();
    bindEvents();
    
    await Promise.all([
      fetchSystemInfo(),
      fetchSystemStats(),
      fetchFilterOptions()
    ]);

    handleRoute();
    window.addEventListener('popstate', handleRoute);
  }

  function cacheDomElements() {
    dom.themeToggle = document.getElementById('themeToggle');
    dom.themeIcon = document.getElementById('themeIcon');
    dom.navLinks = document.querySelectorAll('.nav-link');
    dom.mobileMenuBtn = document.getElementById('mobileMenuBtn');
    dom.mobileMenu = document.getElementById('mobileMenu');
    
    dom.mainSearchInput = document.getElementById('mainSearchInput');
    dom.autocompleteDropdown = document.getElementById('autocompleteDropdown');
    dom.clearSearchBtn = document.getElementById('clearSearchBtn');
    dom.quickChips = document.querySelectorAll('.quick-chip');
    
    dom.views = {
      inicio: document.getElementById('view-inicio'),
      busqueda: document.getElementById('view-busqueda'),
      comparador: document.getElementById('view-comparador'),
      normas: document.getElementById('view-normas'),
      fuentes: document.getElementById('view-fuentes'),
      contacto: document.getElementById('view-contacto'),
      admin: document.getElementById('view-admin')
    };

    dom.filterInstrument = document.getElementById('filterInstrument');
    dom.filterMedium = document.getElementById('filterMedium');
    dom.filterSector = document.getElementById('filterSector');
    dom.filterCategory = document.getElementById('filterCategory');
    dom.filterEntity = document.getElementById('filterEntity');
    dom.filterStatus = document.getElementById('filterStatus');
    dom.resetFiltersBtn = document.getElementById('resetFiltersBtn');
    dom.viewCardsBtn = document.getElementById('viewCardsBtn');
    dom.viewTableBtn = document.getElementById('viewTableBtn');
    dom.exportCsvBtn = document.getElementById('exportCsvBtn');
    dom.shareQueryBtn = document.getElementById('shareQueryBtn');

    dom.resultsContainer = document.getElementById('resultsContainer');
    dom.resultsCount = document.getElementById('resultsCount');
    dom.activeFiltersTags = document.getElementById('activeFiltersTags');
    dom.paginationContainer = document.getElementById('paginationContainer');

    dom.detailModal = document.getElementById('detailModal');
    dom.detailModalContent = document.getElementById('detailModalContent');

    dom.adminParamModal = document.getElementById('adminParamModal');
    dom.adminNormModal = document.getElementById('adminNormModal');

    dom.statParams = document.getElementById('statParams');
    dom.statNorms = document.getElementById('statNorms');
    dom.statSectors = document.getElementById('statSectors');
    dom.statDate = document.getElementById('statDate');

    dom.toastContainer = document.getElementById('toastContainer');
  }

  function initTheme() {
    const saved = localStorage.getItem('econorma_theme');
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (saved === 'dark' || (!saved && prefersDark)) {
      document.documentElement.classList.add('dark');
      updateThemeIcon(true);
    } else {
      document.documentElement.classList.remove('dark');
      updateThemeIcon(false);
    }
  }

  function toggleTheme() {
    const isDark = document.documentElement.classList.toggle('dark');
    localStorage.setItem('econorma_theme', isDark ? 'dark' : 'light');
    updateThemeIcon(isDark);
  }

  function updateThemeIcon(isDark) {
    if (dom.themeIcon) {
      dom.themeIcon.setAttribute('data-lucide', isDark ? 'sun' : 'moon');
      if (window.lucide) window.lucide.createIcons();
    }
  }

  async function fetchSystemInfo() {
    try {
      const res = await fetch('/api/stats/info');
      if (res.ok) {
        state.systemInfo = await res.json();
        renderSystemInfo();
      }
    } catch (e) {
      console.warn('Error cargando info:', e);
    }
  }

  function renderSystemInfo() {
    document.querySelectorAll('.app-title').forEach(el => el.textContent = state.systemInfo.app_name || 'EcoNorma Perú');
    document.querySelectorAll('.app-tagline').forEach(el => el.textContent = state.systemInfo.tagline || 'Plataforma de Consulta de Estándares Ambientales del Perú');
    document.querySelectorAll('.project-author').forEach(el => el.textContent = state.systemInfo.author || 'Alessandro Piero Herrera Balladares');
    
    document.querySelectorAll('.project-phone').forEach(el => {
      el.textContent = state.systemInfo.phone || '+51 981520990';
      if (el.tagName === 'A') el.href = `tel:${state.systemInfo.phone || '+51981520990'}`;
    });

    document.querySelectorAll('.project-email').forEach(el => {
      el.textContent = state.systemInfo.email || 'alessandroherrera1129@gmail.com';
      if (el.tagName === 'A') el.href = `mailto:${state.systemInfo.email || 'alessandroherrera1129@gmail.com'}`;
    });

    document.querySelectorAll('.current-year').forEach(el => el.textContent = new Date().getFullYear());
  }

  async function fetchSystemStats() {
    try {
      const res = await fetch('/api/stats');
      if (res.ok) {
        state.systemStats = await res.json();
        if (dom.statParams) dom.statParams.textContent = state.systemStats.total_parameters || 0;
        if (dom.statNorms) dom.statNorms.textContent = state.systemStats.total_norms || 0;
        if (dom.statSectors) dom.statSectors.textContent = state.systemStats.total_sectors || 0;
        if (dom.statDate) dom.statDate.textContent = state.systemStats.last_database_update || '2026-08-28';
      }
    } catch (e) {
      console.warn('Error stats:', e);
    }
  }

  async function fetchFilterOptions() {
    try {
      const res = await fetch('/api/parameters/filters');
      if (res.ok) {
        state.filterOptions = await res.json();
        populateFilterDropdowns();
      }
    } catch (e) {
      console.warn('Error filters:', e);
    }
  }

  function populateFilterDropdowns() {
    populateSelect(dom.filterInstrument, state.filterOptions.instruments);
    populateSelect(dom.filterMedium, state.filterOptions.environmental_media);
    populateSelect(dom.filterSector, state.filterOptions.sectors);
    populateSelect(dom.filterCategory, state.filterOptions.categories);
    populateSelect(dom.filterEntity, state.filterOptions.issuing_entities);

    const adminMedium = document.getElementById('adminFilterMedium');
    const adminSector = document.getElementById('adminFilterSector');
    const adminNorm = document.getElementById('adminFilterNorm');
    if (adminMedium) populateSelect(adminMedium, state.filterOptions.environmental_media);
    if (adminSector) populateSelect(adminSector, state.filterOptions.sectors);
    if (adminNorm) populateSelect(adminNorm, state.filterOptions.norm_codes);
  }

  function populateSelect(selectEl, items) {
    if (!selectEl || !items) return;
    const currentVal = selectEl.value;
    const defaultOption = selectEl.options[0];
    selectEl.innerHTML = '';
    if (defaultOption) selectEl.appendChild(defaultOption);
    
    items.forEach(item => {
      if (!item) return;
      const opt = document.createElement('option');
      opt.value = item;
      opt.textContent = item;
      selectEl.appendChild(opt);
    });
    if (currentVal) selectEl.value = currentVal;
  }

  function navigateTo(tab, params = {}) {
    state.activeTab = tab;
    let hash = `#${tab}`;
    const searchParams = new URLSearchParams();
    if (params.q) searchParams.set('q', params.q);
    if (params.instrument && params.instrument !== 'TODOS') searchParams.set('tipo', params.instrument);
    if (params.medium && params.medium !== 'TODOS') searchParams.set('medio', params.medium);
    if (params.sector && params.sector !== 'TODOS') searchParams.set('sector', params.sector);
    if (params.category && params.category !== 'TODOS') searchParams.set('categoria', params.category);
    if (params.normCode && params.normCode !== 'TODOS') searchParams.set('norma', params.normCode);
    if (params.paramName) searchParams.set('parametro', params.paramName);

    const queryString = searchParams.toString();
    if (queryString) hash += `?${queryString}`;
    window.location.hash = hash;
  }

  function handleRoute() {
    const rawHash = window.location.hash.slice(1) || 'inicio';
    const [path, queryString] = rawHash.split('?');
    const params = new URLSearchParams(queryString || '');

    state.activeTab = path || 'inicio';
    dom.navLinks.forEach(link => {
      const target = link.getAttribute('data-tab');
      if (target === state.activeTab) {
        link.classList.add('text-emerald-600', 'dark:text-emerald-400', 'font-bold', 'border-b-2', 'border-emerald-600');
        link.classList.remove('text-slate-600', 'dark:text-slate-300');
      } else {
        link.classList.remove('text-emerald-600', 'dark:text-emerald-400', 'font-bold', 'border-b-2', 'border-emerald-600');
        link.classList.add('text-slate-600', 'dark:text-slate-300');
      }
    });

    Object.keys(dom.views).forEach(vKey => {
      if (dom.views[vKey]) {
        if (vKey === state.activeTab) {
          dom.views[vKey].classList.remove('hidden');
        } else {
          dom.views[vKey].classList.add('hidden');
        }
      }
    });

    if (dom.mobileMenu) dom.mobileMenu.classList.add('hidden');

    if (state.activeTab === 'busqueda' || state.activeTab === 'eca' || state.activeTab === 'lmp' || state.activeTab === 'vma') {
      if (state.activeTab === 'eca') state.instrument = 'ECA';
      else if (state.activeTab === 'lmp') state.instrument = 'LMP';
      else if (state.activeTab === 'vma') state.instrument = 'VMA';
      
      if (params.get('q')) state.query = params.get('q');
      if (params.get('parametro')) state.query = params.get('parametro');
      if (params.get('tipo')) state.instrument = params.get('tipo');
      if (params.get('medio')) state.medium = params.get('medio');
      if (params.get('sector')) state.sector = params.get('sector');
      if (params.get('categoria')) state.category = params.get('categoria');
      if (params.get('norma')) state.normCode = params.get('norma');

      syncFiltersToUI();
      executeSearch();
      if (state.activeTab !== 'busqueda') {
        if (dom.views.busqueda) dom.views.busqueda.classList.remove('hidden');
      }
    } else if (state.activeTab === 'normas') {
      loadNormsView(params.get('q') || '');
    } else if (state.activeTab === 'comparador') {
      initComparatorView(params.get('param_id'));
    } else if (state.activeTab === 'admin') {
      initAdminView();
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
    if (window.lucide) window.lucide.createIcons();
  }

  function syncFiltersToUI() {
    if (dom.mainSearchInput) dom.mainSearchInput.value = state.query;
    if (dom.filterInstrument) dom.filterInstrument.value = state.instrument;
    if (dom.filterMedium) dom.filterMedium.value = state.medium;
    if (dom.filterSector) dom.filterSector.value = state.sector;
    if (dom.filterCategory) dom.filterCategory.value = state.category;
    if (dom.filterStatus) dom.filterStatus.value = state.status;
  }

  let debounceTimeout = null;
  function onSearchInput(e) {
    const val = e.target.value;
    state.query = val;
    
    if (dom.clearSearchBtn) dom.clearSearchBtn.classList.toggle('hidden', val.length === 0);

    clearTimeout(debounceTimeout);
    if (val.trim().length >= 1) {
      debounceTimeout = setTimeout(() => {
        fetchAutocomplete(val.trim());
      }, 180);
    } else {
      hideAutocomplete();
    }
  }

  async function fetchAutocomplete(q) {
    try {
      const res = await fetch(`/api/parameters/autocomplete?q=${encodeURIComponent(q)}`);
      if (res.ok) {
        const data = await res.json();
        state.autocompleteItems = data.suggestions || [];
        renderAutocomplete(state.autocompleteItems);
      }
    } catch (e) {
      console.warn('Error autocomplete:', e);
    }
  }

  function renderAutocomplete(items) {
    if (!dom.autocompleteDropdown) return;
    if (items.length === 0) {
      hideAutocomplete();
      return;
    }

    state.autocompleteSelectedIndex = -1;
    dom.autocompleteDropdown.innerHTML = '';
    
    items.forEach((item) => {
      const el = document.createElement('div');
      el.className = 'px-4 py-3 cursor-pointer hover:bg-emerald-50 dark:hover:bg-slate-700/60 border-b border-slate-100 dark:border-slate-700/50 flex items-center justify-between transition-colors';
      el.innerHTML = `
        <div class="flex items-center space-x-3">
          <span class="p-1.5 rounded-lg ${getInstrumentBgClass(item.instrument)} text-xs font-bold font-mono">
            ${item.instrument}
          </span>
          <div>
            <div class="font-semibold text-slate-800 dark:text-slate-100 text-sm">
              ${highlightMatch(item.parameter_name, state.query)}
              ${item.symbol ? `<span class="text-xs text-slate-400 font-mono ml-1.5">(${item.symbol})</span>` : ''}
            </div>
            <div class="text-xs text-slate-500 dark:text-slate-400">
              Medio: ${item.environmental_medium}
            </div>
          </div>
        </div>
        <i data-lucide="chevron-right" class="w-4 h-4 text-slate-400"></i>
      `;
      
      el.addEventListener('click', () => {
        state.query = item.parameter_name;
        if (dom.mainSearchInput) dom.mainSearchInput.value = item.parameter_name;
        hideAutocomplete();
        navigateTo('busqueda', { q: item.parameter_name });
      });

      dom.autocompleteDropdown.appendChild(el);
    });

    dom.autocompleteDropdown.classList.remove('hidden');
    if (window.lucide) window.lucide.createIcons();
  }

  function hideAutocomplete() {
    if (dom.autocompleteDropdown) {
      dom.autocompleteDropdown.classList.add('hidden');
      dom.autocompleteDropdown.innerHTML = '';
    }
  }

  function highlightMatch(text, query) {
    if (!query) return text;
    const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
    return text.replace(regex, '<mark class="bg-yellow-200 dark:bg-yellow-800/80 text-inherit px-0.5 rounded">$1</mark>');
  }

  function escapeRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  function getInstrumentBgClass(inst) {
    switch (inst) {
      case 'ECA': return 'badge-eca';
      case 'LMP': return 'badge-lmp';
      case 'VMA': return 'badge-vma';
      default: return 'bg-slate-100 text-slate-700';
    }
  }

  async function executeSearch() {
    if (!dom.resultsContainer) return;
    
    dom.resultsContainer.innerHTML = renderSkeletonLoaders();
    renderActiveFilterBadges();

    const params = new URLSearchParams();
    if (state.query) params.set('q', state.query);
    if (state.instrument !== 'TODOS') params.set('instrument', state.instrument);
    if (state.medium !== 'TODOS') params.set('medium', state.medium);
    if (state.sector !== 'TODOS') params.set('sector', state.sector);
    if (state.category !== 'TODOS') params.set('category', state.category);
    if (state.status !== 'TODOS') params.set('status', state.status);
    if (state.normCode !== 'TODOS') params.set('norm_code', state.normCode);
    if (state.entity !== 'TODOS') params.set('entity', state.entity);
    if (state.year) params.set('year', state.year);
    params.set('page', state.page);
    params.set('page_size', state.pageSize);

    try {
      const res = await fetch(`/api/parameters/search?${params.toString()}`);
      if (res.ok) {
        const data = await res.json();
        state.results = data.results || [];
        state.totalResults = data.total || 0;
        renderResults();
        renderPagination();
      } else {
        dom.resultsContainer.innerHTML = renderErrorState('Ocurrió un error al consultar los parámetros normativos.');
      }
    } catch (e) {
      console.error('Error buscando parámetros:', e);
      dom.resultsContainer.innerHTML = renderErrorState('Error de conexión con la base de datos ambiental.');
    }
  }

  function renderSkeletonLoaders() {
    return Array(6).fill(0).map(() => `
      <div class="glass-card rounded-2xl p-6 border border-slate-200 dark:border-slate-800 space-y-4">
        <div class="flex justify-between items-center">
          <div class="h-6 w-20 skeleton rounded-full"></div>
          <div class="h-5 w-28 skeleton rounded-full"></div>
        </div>
        <div class="h-7 w-3/4 skeleton rounded-lg"></div>
        <div class="h-4 w-1/2 skeleton rounded"></div>
        <div class="h-10 w-full skeleton rounded-xl"></div>
        <div class="flex gap-2 pt-2">
          <div class="h-9 flex-1 skeleton rounded-lg"></div>
          <div class="h-9 flex-1 skeleton rounded-lg"></div>
        </div>
      </div>
    `).join('');
  }

  function renderErrorState(msg) {
    return `
      <div class="col-span-full py-16 text-center">
        <div class="w-16 h-16 bg-rose-100 dark:bg-rose-900/30 text-rose-600 dark:text-rose-400 rounded-full flex items-center justify-center mx-auto mb-4">
          <i data-lucide="alert-triangle" class="w-8 h-8"></i>
        </div>
        <h3 class="text-xl font-bold text-slate-800 dark:text-slate-100 mb-2">Consulta no completada</h3>
        <p class="text-slate-500 dark:text-slate-400 max-w-md mx-auto mb-6">${msg}</p>
        <button onclick="EcoNorma.resetAllFilters()" class="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-semibold shadow-md transition-colors">
          Restablecer filtros de búsqueda
        </button>
      </div>
    `;
  }

  function renderActiveFilterBadges() {
    if (!dom.activeFiltersTags) return;
    const badges = [];

    if (state.query) badges.push({ key: 'q', label: `Búsqueda: "${state.query}"` });
    if (state.instrument !== 'TODOS') badges.push({ key: 'instrument', label: `Instrumento: ${state.instrument}` });
    if (state.medium !== 'TODOS') badges.push({ key: 'medium', label: `Medio: ${state.medium}` });
    if (state.sector !== 'TODOS') badges.push({ key: 'sector', label: `Sector: ${state.sector}` });
    if (state.category !== 'TODOS') badges.push({ key: 'category', label: `Categoría: ${state.category}` });
    if (state.status !== 'TODOS') badges.push({ key: 'status', label: `Estado: ${state.status}` });

    if (badges.length === 0) {
      dom.activeFiltersTags.innerHTML = '<span class="text-xs text-slate-400">Sin filtros aplicados</span>';
      return;
    }

    dom.activeFiltersTags.innerHTML = badges.map(b => `
      <span class="inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 rounded-full text-xs font-semibold border border-emerald-200 dark:border-emerald-800">
        ${b.label}
        <button onclick="EcoNorma.removeFilter('${b.key}')" class="hover:text-emerald-950 dark:hover:text-emerald-100 focus:outline-none">
          <i data-lucide="x" class="w-3 h-3"></i>
        </button>
      </span>
    `).join('');

    if (window.lucide) window.lucide.createIcons();
  }

  function renderResults() {
    if (dom.resultsCount) {
      dom.resultsCount.textContent = `${state.totalResults} resultados encontrados`;
    }

    if (state.results.length === 0) {
      dom.resultsContainer.innerHTML = `
        <div class="col-span-full py-16 text-center">
          <div class="w-20 h-20 bg-slate-100 dark:bg-slate-800 text-slate-400 rounded-full flex items-center justify-center mx-auto mb-4">
            <i data-lucide="search-x" class="w-10 h-10"></i>
          </div>
          <h3 class="text-2xl font-bold text-slate-800 dark:text-slate-100 mb-2">No encontramos estándares con esos criterios</h3>
          <p class="text-slate-500 dark:text-slate-400 max-w-md mx-auto mb-6">
            Intenta buscar por el nombre químico, símbolo o restablece los filtros.
          </p>
          <button onclick="EcoNorma.resetAllFilters()" class="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-semibold shadow-md transition-colors">
            Restablecer todos los filtros
          </button>
        </div>
      `;
      if (window.lucide) window.lucide.createIcons();
      return;
    }

    if (state.viewMode === 'cards') {
      renderCardsView();
    } else {
      renderTableView();
    }

    if (window.lucide) window.lucide.createIcons();
  }

  function renderCardsView() {
    dom.resultsContainer.className = 'grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6';
    dom.resultsContainer.innerHTML = state.results.map(item => `
      <div class="glass-card rounded-2xl p-6 border border-slate-200/80 dark:border-slate-800 flex flex-col justify-between relative group hover:border-emerald-500/50 dark:hover:border-emerald-500/50">
        <div>
          <div class="flex items-center justify-between gap-2 mb-3">
            <div class="flex items-center gap-2">
              <span class="px-2.5 py-1 rounded-md text-xs font-black tracking-wider ${getInstrumentBgClass(item.instrument)}">
                ${item.instrument}
              </span>
              <span class="text-xs font-semibold text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded">
                ${item.environmental_medium}
              </span>
            </div>
            <span class="inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded-full ${getStatusBadgeClass(item.status)}">
              <span class="w-1.5 h-1.5 rounded-full bg-current"></span>
              ${item.status}
            </span>
          </div>

          <div class="mb-2">
            <h4 class="text-lg font-bold text-slate-900 dark:text-white group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors">
              ${item.parameter_name}
            </h4>
            <div class="flex items-center gap-2 mt-0.5">
              ${item.symbol ? `<span class="text-xs font-mono font-semibold text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/60 px-1.5 py-0.5 rounded border border-emerald-200 dark:border-emerald-900">${item.symbol}</span>` : ''}
              ${item.cas_number ? `<span class="text-xs font-mono text-slate-400">CAS: ${item.cas_number}</span>` : ''}
            </div>
          </div>

          <div class="text-xs text-slate-600 dark:text-slate-300 bg-slate-50 dark:bg-slate-800/60 rounded-xl p-3 mb-4 space-y-1 border border-slate-100 dark:border-slate-800">
            <div class="font-semibold text-slate-800 dark:text-slate-200">
              <i data-lucide="tag" class="w-3.5 h-3.5 inline-block mr-1 text-emerald-600"></i> ${item.category}
            </div>
            ${item.subcategory ? `<div class="text-slate-500 dark:text-slate-400 pl-4 border-l border-emerald-500/30">${item.subcategory}</div>` : ''}
            ${item.sector ? `<div class="text-[11px] text-slate-400">Sector: ${item.sector}</div>` : ''}
          </div>

          <div class="bg-gradient-to-br from-emerald-50/50 to-teal-50/50 dark:from-slate-800/80 dark:to-emerald-950/30 rounded-xl p-4 mb-4 border border-emerald-100 dark:border-emerald-900/40">
            <span class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider block mb-1">
              Valor Regulatorio
            </span>
            <div class="flex items-baseline gap-2">
              <span class="text-2xl font-black text-emerald-700 dark:text-emerald-300 font-mono">
                ${item.value_text || formatParamValue(item)}
              </span>
              <span class="text-xs font-bold text-slate-500 dark:text-slate-400 font-mono">
                ${item.unit}
              </span>
            </div>
            ${item.evaluation_period ? `<span class="text-[11px] text-slate-500 dark:text-slate-400 block mt-1"><i data-lucide="clock" class="w-3 h-3 inline mr-1"></i> ${item.evaluation_period}</span>` : ''}
          </div>

          <div class="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 mb-4 pb-2 border-b border-slate-100 dark:border-slate-800">
            <span class="font-semibold text-slate-700 dark:text-slate-300">
              <i data-lucide="file-text" class="w-3.5 h-3.5 inline mr-1 text-slate-400"></i> ${item.norm_code}
            </span>
            <span class="text-[11px]">${item.issuing_entity} (${item.year})</span>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-2 pt-2">
          <button onclick="EcoNorma.openParamDetail(${item.id})" class="flex items-center justify-center gap-1.5 px-3 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold shadow-sm transition-all">
            <i data-lucide="eye" class="w-3.5 h-3.5"></i> Ficha Técnica
          </button>
          <button onclick="EcoNorma.openComparatorWithParam(${item.id})" class="flex items-center justify-center gap-1.5 px-3 py-2 bg-sky-50 dark:bg-sky-950/50 hover:bg-sky-100 dark:hover:bg-sky-900/50 text-sky-700 dark:text-sky-300 rounded-xl text-xs font-bold border border-sky-200 dark:border-sky-800 transition-all">
            <i data-lucide="scale" class="w-3.5 h-3.5"></i> Comparar
          </button>
          <a href="${item.official_url || '#'}" target="_blank" rel="noopener noreferrer" class="flex items-center justify-center gap-1.5 px-3 py-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-xl text-[11px] font-semibold transition-all">
            <i data-lucide="external-link" class="w-3 h-3"></i> Norma Oficial
          </a>
          <button onclick="EcoNorma.copyParamReference(${item.id})" class="flex items-center justify-center gap-1.5 px-3 py-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-xl text-[11px] font-semibold transition-all">
            <i data-lucide="copy" class="w-3 h-3"></i> Referencia
          </button>
        </div>
      </div>
    `).join('');
  }

  function renderTableView() {
    dom.resultsContainer.className = 'col-span-full';
    dom.resultsContainer.innerHTML = `
      <div class="glass-panel rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
        <div class="table-responsive">
          <table class="w-full text-left text-sm text-slate-600 dark:text-slate-300">
            <thead class="bg-slate-50 dark:bg-slate-800/80 text-xs uppercase font-bold text-slate-700 dark:text-slate-200 border-b border-slate-200 dark:border-slate-700">
              <tr>
                <th class="px-4 py-3.5">Instrumento</th>
                <th class="px-4 py-3.5">Medio / Sector</th>
                <th class="px-4 py-3.5">Parámetro</th>
                <th class="px-4 py-3.5">Categoría / Subcategoría</th>
                <th class="px-4 py-3.5">Límite Normativo</th>
                <th class="px-4 py-3.5">Unidad</th>
                <th class="px-4 py-3.5">Norma Legal</th>
                <th class="px-4 py-3.5 text-center">Acciones</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
              ${state.results.map(item => `
                <tr class="hover:bg-emerald-50/40 dark:hover:bg-slate-800/50 transition-colors">
                  <td class="px-4 py-3 font-mono font-bold">
                    <span class="px-2 py-0.5 rounded text-xs ${getInstrumentBgClass(item.instrument)}">${item.instrument}</span>
                  </td>
                  <td class="px-4 py-3">
                    <div class="font-semibold text-slate-800 dark:text-slate-200">${item.environmental_medium}</div>
                    ${item.sector ? `<div class="text-xs text-slate-400">${item.sector}</div>` : ''}
                  </td>
                  <td class="px-4 py-3">
                    <div class="font-bold text-slate-900 dark:text-white">${item.parameter_name}</div>
                    ${item.symbol ? `<span class="text-xs font-mono text-emerald-600 dark:text-emerald-400">(${item.symbol})</span>` : ''}
                  </td>
                  <td class="px-4 py-3 text-xs max-w-xs">
                    <div class="font-medium text-slate-800 dark:text-slate-200">${item.category}</div>
                    ${item.subcategory ? `<div class="text-slate-400">${item.subcategory}</div>` : ''}
                  </td>
                  <td class="px-4 py-3 font-mono font-bold text-emerald-700 dark:text-emerald-300">
                    ${item.value_text || formatParamValue(item)}
                  </td>
                  <td class="px-4 py-3 font-mono text-xs text-slate-500">
                    ${item.unit}
                  </td>
                  <td class="px-4 py-3 text-xs">
                    <div class="font-semibold">${item.norm_code}</div>
                    <div class="text-slate-400">${item.issuing_entity} (${item.year})</div>
                  </td>
                  <td class="px-4 py-3 text-center">
                    <div class="flex items-center justify-center gap-1.5">
                      <button onclick="EcoNorma.openParamDetail(${item.id})" title="Ver ficha técnica" class="p-1.5 hover:bg-emerald-100 dark:hover:bg-emerald-950 text-emerald-700 dark:text-emerald-300 rounded-lg">
                        <i data-lucide="eye" class="w-4 h-4"></i>
                      </button>
                      <button onclick="EcoNorma.openComparatorWithParam(${item.id})" title="Comparar resultado" class="p-1.5 hover:bg-sky-100 dark:hover:bg-sky-950 text-sky-700 dark:text-sky-300 rounded-lg">
                        <i data-lucide="scale" class="w-4 h-4"></i>
                      </button>
                      <a href="${item.official_url || '#'}" target="_blank" rel="noopener noreferrer" title="Consultar norma oficial" class="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 rounded-lg">
                        <i data-lucide="external-link" class="w-4 h-4"></i>
                      </a>
                    </div>
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  }

  function formatParamValue(item) {
    if (item.min_value !== null && item.max_value !== null) return `${item.min_value} - ${item.max_value}`;
    if (item.max_value !== null) return `${item.max_value}`;
    if (item.min_value !== null) return `≥ ${item.min_value}`;
    return 'N/A';
  }

  function getStatusBadgeClass(status) {
    switch (status) {
      case 'VIGENTE': return 'bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800';
      case 'MODIFICADO': return 'bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800';
      case 'DEROGADO': return 'bg-rose-100 dark:bg-rose-950 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-800';
      case 'INACTIVO':
      case 'INACTIVA':
        return 'bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-300';
      case 'PENDIENTE DE VERIFICACIÓN': return 'bg-yellow-100 dark:bg-yellow-950 text-yellow-800 dark:text-yellow-300 border border-yellow-300';
      case 'REQUIERE REVISIÓN': return 'bg-orange-100 dark:bg-orange-950 text-orange-800 dark:text-orange-300 border border-orange-300';
      case 'NO PUBLICAR': return 'bg-rose-100 dark:bg-rose-950 text-rose-800 dark:text-rose-300 border border-rose-300';
      default: return 'bg-slate-100 text-slate-700';
    }
  }

  function getVerificationBadgeHtml(verifStatus) {
    switch (verifStatus) {
      case 'VERIFICADO':
        return `<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300 border border-emerald-200"><i data-lucide="check" class="w-3 h-3"></i> Verificado</span>`;
      case 'PENDIENTE DE VERIFICACIÓN':
        return `<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-bold bg-yellow-100 dark:bg-yellow-950 text-yellow-800 dark:text-yellow-300 border border-yellow-300"><i data-lucide="clock" class="w-3 h-3"></i> Pendiente</span>`;
      case 'REQUIERE REVISIÓN':
        return `<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-bold bg-orange-100 dark:bg-orange-950 text-orange-800 dark:text-orange-300 border border-orange-300"><i data-lucide="alert-circle" class="w-3 h-3"></i> Revisión</span>`;
      case 'NO PUBLICAR':
        return `<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-bold bg-rose-100 dark:bg-rose-950 text-rose-800 dark:text-rose-300 border border-rose-300"><i data-lucide="eye-off" class="w-3 h-3"></i> Oculto</span>`;
      default:
        return `<span class="px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-100">${verifStatus || 'Sin estado'}</span>`;
    }
  }

  function renderPagination() {
    if (!dom.paginationContainer) return;
    const totalPages = Math.ceil(state.totalResults / state.pageSize);
    if (totalPages <= 1) {
      dom.paginationContainer.innerHTML = '';
      return;
    }

    let html = `
      <div class="flex items-center justify-between w-full pt-6 border-t border-slate-200 dark:border-slate-800">
        <span class="text-xs text-slate-500 dark:text-slate-400">
          Página ${state.page} de ${totalPages} (${state.totalResults} registros)
        </span>
        <div class="flex items-center space-x-1.5">
          <button onclick="EcoNorma.changePage(${state.page - 1})" ${state.page === 1 ? 'disabled' : ''} class="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-xs font-semibold hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors">
            Anterior
          </button>
    `;

    for (let p = Math.max(1, state.page - 2); p <= Math.min(totalPages, state.page + 2); p++) {
      html += `
        <button onclick="EcoNorma.changePage(${p})" class="w-8 h-8 rounded-lg text-xs font-bold ${p === state.page ? 'bg-emerald-600 text-white' : 'border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300'} transition-colors">
          ${p}
        </button>
      `;
    }

    html += `
          <button onclick="EcoNorma.changePage(${state.page + 1})" ${state.page === totalPages ? 'disabled' : ''} class="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-xs font-semibold hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors">
            Siguiente
          </button>
        </div>
      </div>
    `;

    dom.paginationContainer.innerHTML = html;
  }

  function changePage(p) {
    const totalPages = Math.ceil(state.totalResults / state.pageSize);
    if (p < 1 || p > totalPages) return;
    state.page = p;
    executeSearch();
    window.scrollTo({ top: 400, behavior: 'smooth' });
  }

  async function openParamDetail(id) {
    try {
      const res = await fetch(`/api/parameters/${id}`);
      if (res.ok) {
        state.selectedParamForDetail = await res.json();
        renderParamDetailModal(state.selectedParamForDetail);
      }
    } catch (e) {
      console.error('Error cargando detalle:', e);
      showToast('Error al cargar la ficha técnica.', 'error');
    }
  }

  function renderParamDetailModal(p) {
    if (!dom.detailModal || !dom.detailModalContent) return;

    dom.detailModalContent.innerHTML = `
      <div class="space-y-6">
        <div class="flex items-start justify-between border-b border-slate-200 dark:border-slate-800 pb-4">
          <div>
            <div class="flex items-center gap-2 mb-1.5">
              <span class="px-2.5 py-1 rounded-md text-xs font-black tracking-wider ${getInstrumentBgClass(p.instrument)}">
                ${p.instrument}
              </span>
              <span class="text-xs font-semibold text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded">
                ${p.environmental_medium}
              </span>
              <span class="text-xs font-bold px-2 py-0.5 rounded-full ${getStatusBadgeClass(p.status)}">
                ${p.status}
              </span>
            </div>
            <h3 class="text-2xl font-extrabold text-slate-900 dark:text-white">
              ${p.parameter_name}
            </h3>
            ${p.alternative_names ? `<p class="text-xs text-slate-400 mt-0.5">Nombres alternativos: ${p.alternative_names}</p>` : ''}
          </div>
          <button onclick="EcoNorma.closeDetailModal()" class="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
            <i data-lucide="x" class="w-6 h-6"></i>
          </button>
        </div>

        <div class="bg-gradient-to-r from-emerald-500/10 via-teal-500/10 to-sky-500/10 border border-emerald-500/30 dark:border-emerald-500/20 rounded-2xl p-5 flex flex-wrap items-center justify-between gap-4">
          <div>
            <span class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider block">Valor Normativo Establecido</span>
            <div class="flex items-baseline gap-2 mt-1">
              <span class="text-3xl font-black text-emerald-600 dark:text-emerald-400 font-mono">
                ${p.value_text || formatParamValue(p)}
              </span>
              <span class="text-base font-bold text-slate-600 dark:text-slate-300 font-mono">
                ${p.unit}
              </span>
            </div>
          </div>
          <div class="text-right text-xs space-y-1">
            ${p.symbol ? `<div><span class="text-slate-400">Símbolo:</span> <span class="font-mono font-bold text-slate-700 dark:text-slate-200">${p.symbol}</span></div>` : ''}
            ${p.cas_number ? `<div><span class="text-slate-400">N° CAS:</span> <span class="font-mono text-slate-700 dark:text-slate-200">${p.cas_number}</span></div>` : ''}
            ${p.evaluation_period ? `<div><span class="text-slate-400">Periodo:</span> <span class="font-semibold text-slate-700 dark:text-slate-200">${p.evaluation_period}</span></div>` : ''}
          </div>
        </div>

        <div class="space-y-2">
          <h4 class="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <i data-lucide="map-pin" class="w-4 h-4 text-emerald-600"></i> ¿Dónde aplica este estándar?
          </h4>
          <div class="bg-slate-50 dark:bg-slate-800/60 rounded-xl p-4 border border-slate-100 dark:border-slate-800 text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
            <p class="font-semibold text-slate-800 dark:text-slate-200 mb-1">${p.category}</p>
            ${p.subcategory ? `<p class="text-slate-600 dark:text-slate-400 mb-1.5">${p.subcategory}</p>` : ''}
            ${p.sector ? `<p class="text-slate-500"><strong>Sector regulado:</strong> ${p.sector} ${p.subsector ? `(${p.subsector})` : ''}</p>` : ''}
            ${p.activity ? `<p class="text-slate-500"><strong>Actividad:</strong> ${p.activity}</p>` : ''}
          </div>
        </div>

        ${p.method_criteria || p.observations ? `
          <div class="space-y-2">
            <h4 class="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <i data-lucide="flask-conical" class="w-4 h-4 text-sky-600"></i> Criterios y Métodos de Evaluación
            </h4>
            <div class="bg-slate-50 dark:bg-slate-800/60 rounded-xl p-4 border border-slate-100 dark:border-slate-800 text-xs text-slate-600 dark:text-slate-300 space-y-2">
              ${p.method_criteria ? `<p><strong>Método de referencia:</strong> ${p.method_criteria}</p>` : ''}
              ${p.observations ? `<p><strong>Observaciones y notas:</strong> ${p.observations}</p>` : ''}
            </div>
          </div>
        ` : ''}

        <div class="space-y-2">
          <h4 class="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <i data-lucide="scale" class="w-4 h-4 text-emerald-600"></i> Fuente Legal y Sustento Normativo
          </h4>
          <div class="bg-slate-50 dark:bg-slate-800/60 rounded-xl p-4 border border-slate-100 dark:border-slate-800 text-xs space-y-2">
            <p class="font-bold text-slate-800 dark:text-slate-200">${p.norm_name || p.norm_code} (${p.norm_code})</p>
            <div class="grid grid-cols-2 gap-2 text-slate-500">
              <div><strong>Entidad emisora:</strong> ${p.issuing_entity}</div>
              <div><strong>Año de publicación:</strong> ${p.year}</div>
              <div><strong>Ubicación en norma:</strong> ${p.annex || ''} ${p.table_ref ? `· ${p.table_ref}` : ''} ${p.article_ref ? `· ${p.article_ref}` : ''}</div>
              <div><strong>Última verificación:</strong> ${p.last_verified_date || '2026-08-28'} (${p.verification_status})</div>
            </div>
          </div>
        </div>

        <div class="flex flex-wrap items-center justify-between gap-3 pt-4 border-t border-slate-200 dark:border-slate-800">
          <button onclick="EcoNorma.copyParamReference(${p.id})" class="px-4 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-xl text-xs font-bold transition-colors flex items-center gap-1.5">
            <i data-lucide="copy" class="w-3.5 h-3.5"></i> Copiar Cita Bibliográfica
          </button>
          <div class="flex items-center gap-2">
            <button onclick="EcoNorma.openComparatorWithParam(${p.id}); EcoNorma.closeDetailModal();" class="px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white rounded-xl text-xs font-bold shadow-sm transition-colors flex items-center gap-1.5">
              <i data-lucide="scale" class="w-3.5 h-3.5"></i> Comparar en Laboratorio
            </button>
            <a href="${p.official_url || '#'}" target="_blank" rel="noopener noreferrer" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold shadow-sm transition-colors flex items-center gap-1.5">
              <i data-lucide="external-link" class="w-3.5 h-3.5"></i> Consultar Norma Oficial
            </a>
          </div>
        </div>
      </div>
    `;

    dom.detailModal.classList.remove('hidden');
    dom.detailModal.classList.add('flex');
    if (window.lucide) window.lucide.createIcons();
  }

  function closeDetailModal() {
    if (dom.detailModal) {
      dom.detailModal.classList.add('hidden');
      dom.detailModal.classList.remove('flex');
    }
  }

  function copyParamReference(paramId) {
    const p = state.results.find(x => x.id === paramId) || state.selectedParamForDetail;
    if (!p) return;
    const citation = `MINAM / ${p.issuing_entity} (${p.year}). ${p.norm_name || p.norm_code} [${p.norm_code}]. Parámetro: ${p.parameter_name} (${p.value_text || formatParamValue(p)} ${p.unit}) en ${p.category} ${p.subcategory ? `- ${p.subcategory}` : ''}. Fuente oficial: ${p.official_url || ''}`;
    navigator.clipboard.writeText(citation).then(() => {
      showToast('Referencia legal copiada al portapapeles', 'success');
    }).catch(() => {
      showToast('No se pudo copiar automáticamente', 'error');
    });
  }

  async function initComparatorView(preselectedParamId = null) {
    const compParamSelect = document.getElementById('compParamSelect');
    if (!compParamSelect) return;

    try {
      const res = await fetch('/api/parameters/search?page_size=500');
      if (res.ok) {
        const data = await res.json();
        const allParams = data.results || [];
        
        compParamSelect.innerHTML = '<option value="">-- Selecciona el parámetro exacto y su categoría --</option>';
        allParams.forEach(p => {
          const opt = document.createElement('option');
          opt.value = p.id;
          opt.textContent = `[${p.instrument} - ${p.environmental_medium}] ${p.parameter_name} (${p.category} ${p.subcategory ? '· ' + p.subcategory : ''}) [Límite: ${p.value_text || formatParamValue(p)} ${p.unit}]`;
          compParamSelect.appendChild(opt);
        });

        if (preselectedParamId) {
          compParamSelect.value = preselectedParamId;
        }
      }
    } catch (e) {
      console.warn('Error inicializando comparador:', e);
    }
  }

  function openComparatorWithParam(paramId) {
    navigateTo('comparador', { param_id: paramId });
  }

  async function evaluateCompliance() {
    const compParamSelect = document.getElementById('compParamSelect');
    const compMeasuredValue = document.getElementById('compMeasuredValue');
    const compResultBox = document.getElementById('compResultBox');

    if (!compParamSelect || !compMeasuredValue || !compResultBox) return;

    const paramId = parseInt(compParamSelect.value, 10);
    const measuredVal = parseFloat(compMeasuredValue.value);

    if (!paramId) {
      showToast('Por favor selecciona primero un parámetro normativo aplicable.', 'warning');
      return;
    }
    if (isNaN(measuredVal)) {
      showToast('Por favor ingresa un resultado numérico de laboratorio válido.', 'warning');
      return;
    }

    try {
      const res = await fetch('/api/comparator/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ parameter_id: paramId, measured_value: measuredVal })
      });

      if (res.ok) {
        const evalData = await res.json();
        renderComplianceResult(evalData);
      } else {
        showToast('Error al procesar la evaluación de cumplimiento.', 'error');
      }
    } catch (e) {
      console.error('Error evaluando cumplimiento:', e);
      showToast('Error de comunicación con el servidor.', 'error');
    }
  }

  function renderComplianceResult(evalData) {
    const compResultBox = document.getElementById('compResultBox');
    if (!compResultBox) return;

    const isCompliant = evalData.is_compliant;
    const cardBg = isCompliant 
      ? 'bg-emerald-50 dark:bg-emerald-950/50 border-emerald-300 dark:border-emerald-800' 
      : 'bg-rose-50 dark:bg-rose-950/50 border-rose-300 dark:border-rose-800';
    
    const badgeBg = isCompliant 
      ? 'bg-emerald-600 text-white' 
      : 'bg-rose-600 text-white';

    const icon = isCompliant ? 'check-circle-2' : 'alert-octagon';

    compResultBox.innerHTML = `
      <div class="rounded-2xl p-6 border ${cardBg} transition-all space-y-4 animate-fade-in">
        <div class="flex items-center justify-between flex-wrap gap-2">
          <div class="flex items-center gap-3">
            <span class="px-3.5 py-1.5 rounded-xl text-sm font-black flex items-center gap-2 ${badgeBg} shadow-sm">
              <i data-lucide="${icon}" class="w-4 h-4"></i>
              ${evalData.status_label.toUpperCase()}
            </span>
            <span class="text-xs font-semibold text-slate-500 font-mono">
              Instrumento: ${evalData.instrument} · ${evalData.norm_code}
            </span>
          </div>
          ${evalData.percentage_of_limit !== null ? `
            <span class="text-xs font-mono font-bold px-2.5 py-1 rounded-lg ${isCompliant ? 'bg-emerald-200/60 dark:bg-emerald-900/60 text-emerald-900 dark:text-emerald-200' : 'bg-rose-200/60 dark:bg-rose-900/60 text-rose-900 dark:text-rose-200'}">
              ${evalData.percentage_of_limit}% del límite
            </span>
          ` : ''}
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 py-2 border-y border-slate-200 dark:border-slate-800 text-sm">
          <div>
            <span class="text-xs text-slate-400 block mb-0.5">Resultado ingresado:</span>
            <span class="text-2xl font-black font-mono text-slate-900 dark:text-white">
              ${evalData.measured_value} <span class="text-xs font-semibold text-slate-500">${evalData.unit}</span>
            </span>
          </div>
          <div>
            <span class="text-xs text-slate-400 block mb-0.5">Límite normativo aplicable:</span>
            <span class="text-2xl font-black font-mono text-emerald-700 dark:text-emerald-400">
              ${evalData.max_value !== null ? `≤ ${evalData.max_value}` : ''}
              ${evalData.min_value !== null && evalData.max_value !== null ? ` [${evalData.min_value} - ${evalData.max_value}]` : ''}
              ${evalData.min_value !== null && evalData.max_value === null ? `≥ ${evalData.min_value}` : ''}
              <span class="text-xs font-semibold text-slate-500">${evalData.unit}</span>
            </span>
          </div>
        </div>

        <p class="text-sm font-medium text-slate-700 dark:text-slate-200">
          ${evalData.evaluation_text}
        </p>

        <div class="bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900/60 rounded-xl p-3.5 text-xs text-amber-800 dark:text-amber-300 flex items-start gap-2.5">
          <i data-lucide="info" class="w-4 h-4 flex-shrink-0 mt-0.5 text-amber-600"></i>
          <span>${evalData.disclaimer}</span>
        </div>
      </div>
    `;

    if (window.lucide) window.lucide.createIcons();
  }

  async function loadInterCategoryComparison(paramName) {
    const chartCanvas = document.getElementById('interCategoryChartCanvas');
    if (!chartCanvas || !paramName) return;

    try {
      const res = await fetch(`/api/parameters/compare-categories?param_name=${encodeURIComponent(paramName)}`);
      if (res.ok) {
        const data = await res.json();
        const items = data.items || [];
        renderInterCategoryChart(items, paramName);
      }
    } catch (e) {
      console.warn('Error cargando comparación intercategorías:', e);
    }
  }

  function renderInterCategoryChart(items, paramName) {
    const ctx = document.getElementById('interCategoryChartCanvas');
    if (!ctx) return;

    if (state.interCategoryChart) {
      state.interCategoryChart.destroy();
    }

    const validItems = items.filter(x => x.max_value !== null || x.min_value !== null);
    if (validItems.length === 0) return;

    const labels = validItems.map(x => `${x.instrument}: ${x.category.substring(0, 20)}...`);
    const values = validItems.map(x => x.max_value !== null ? x.max_value : x.min_value);
    const colors = validItems.map(x => {
      if (x.instrument === 'ECA') return '#0284C7';
      if (x.instrument === 'LMP') return '#D97706';
      return '#7C3AED';
    });

    state.interCategoryChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: `Límite Normativo (${validItems[0].unit})`,
          data: values,
          backgroundColor: colors,
          borderRadius: 8
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          title: {
            display: true,
            text: `Comparativa del parámetro ${paramName} según Instrumento y Categoría`
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: { display: true, text: validItems[0].unit }
          }
        }
      }
    });
  }

  async function loadNormsView(query = '') {
    const container = document.getElementById('normsListContainer');
    const searchInput = document.getElementById('normsSearchInput');
    if (!container) return;

    if (searchInput) searchInput.value = query;
    container.innerHTML = renderSkeletonLoaders();

    try {
      const res = await fetch(`/api/norms?q=${encodeURIComponent(query)}`);
      if (res.ok) {
        const data = await res.json();
        renderNormsCards(data.norms || []);
      }
    } catch (e) {
      console.error('Error cargando normas:', e);
    }
  }

  function renderNormsCards(norms) {
    const container = document.getElementById('normsListContainer');
    if (!container) return;

    if (norms.length === 0) {
      container.innerHTML = `
        <div class="col-span-full text-center py-12">
          <p class="text-slate-500">No encontramos normas con ese número o título.</p>
        </div>
      `;
      return;
    }

    container.innerHTML = norms.map(n => `
      <div class="glass-card rounded-2xl p-6 border border-slate-200 dark:border-slate-800 flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between gap-2 mb-3">
            <span class="px-2.5 py-1 rounded-md text-xs font-black tracking-wider ${getInstrumentBgClass(n.instrument)}">
              ${n.instrument}
            </span>
            <span class="text-xs font-bold text-slate-500 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded">
              Año ${n.year} · ${n.issuing_entity}
            </span>
          </div>

          <h4 class="text-lg font-bold text-slate-900 dark:text-white mb-1.5">
            ${n.code}
          </h4>
          <p class="text-xs font-medium text-slate-600 dark:text-slate-300 mb-3 line-clamp-2">
            ${n.title}
          </p>
          <p class="text-xs text-slate-500 dark:text-slate-400 bg-slate-50 dark:bg-slate-800/50 p-3 rounded-xl mb-4 leading-relaxed">
            ${n.summary || 'Regulación ambiental oficial del Estado Peruano.'}
          </p>
        </div>

        <div class="space-y-3 pt-3 border-t border-slate-100 dark:border-slate-800">
          <div class="flex items-center justify-between text-xs text-slate-500">
            <span><i data-lucide="database" class="w-3.5 h-3.5 inline mr-1 text-emerald-600"></i> ${n.parameters_count} parámetros registrados</span>
            <span class="text-emerald-600 font-bold font-mono">${n.status}</span>
          </div>
          <div class="grid grid-cols-2 gap-2">
            <button onclick="EcoNorma.searchByNorm('${n.code}')" class="px-3 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold shadow-sm transition-colors flex items-center justify-center gap-1.5">
              <i data-lucide="search" class="w-3.5 h-3.5"></i> Ver Parámetros
            </button>
            <a href="${n.official_url || '#'}" target="_blank" rel="noopener noreferrer" class="px-3 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-xl text-xs font-bold transition-colors flex items-center justify-center gap-1.5">
              <i data-lucide="external-link" class="w-3.5 h-3.5"></i> Norma Oficial
            </a>
          </div>
        </div>
      </div>
    `).join('');

    if (window.lucide) window.lucide.createIcons();
  }

  function searchByNorm(normCode) {
    navigateTo('busqueda', { normCode: normCode });
  }

  async function submitContactForm(e) {
    e.preventDefault();
    const name = document.getElementById('contactName').value;
    const email = document.getElementById('contactEmail').value;
    const type = document.getElementById('contactType').value;
    const subject = document.getElementById('contactSubject').value;
    const message = document.getElementById('contactMessage').value;

    try {
      const res = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: name,
          email: email,
          inquiry_type: type,
          subject: subject,
          message: message
        })
      });

      if (res.ok) {
        showToast('¡Gracias! Tu mensaje u observación ha sido registrado exitosamente.', 'success');
        document.getElementById('contactForm').reset();
      } else {
        showToast('Error al enviar el formulario. Verifica los campos obligatorios.', 'error');
      }
    } catch (err) {
      console.error('Error enviando contacto:', err);
      showToast('Error de conexión con el servidor.', 'error');
    }
  }

  // =========================================================================
  // SISTEMA ADMINISTRATIVO Y CRUD INTEGRAL (PARÁMETROS, NORMAS, HISTORIAL)
  // =========================================================================

  async function initAdminView() {
    const adminLoginBox = document.getElementById('adminLoginBox');
    const adminDashboard = document.getElementById('adminDashboard');
    if (!adminLoginBox || !adminDashboard) return;

    if (state.adminToken) {
      adminLoginBox.classList.add('hidden');
      adminDashboard.classList.remove('hidden');
      await preloadAdminNormsCatalog();
      switchAdminSubTab(state.adminSubTab || 'parametros');
    } else {
      adminLoginBox.classList.remove('hidden');
      adminDashboard.classList.add('hidden');
    }
  }

  async function preloadAdminNormsCatalog() {
    try {
      const res = await fetch('/api/admin/norms', {
        headers: { 'x-admin-token': state.adminToken }
      });
      if (res.ok) {
        const data = await res.json();
        state.adminNormsList = data.norms || [];
        populateAdminNormsDropdowns();
      }
    } catch (e) {
      console.warn('Error precargando normas admin:', e);
    }
  }

  function populateAdminNormsDropdowns() {
    const editParamNormCode = document.getElementById('editParamNormCode');
    const adminFilterNorm = document.getElementById('adminFilterNorm');

    if (editParamNormCode) {
      editParamNormCode.innerHTML = '<option value="">-- Selecciona la norma legal oficial --</option>';
      state.adminNormsList.forEach(n => {
        const opt = document.createElement('option');
        opt.value = n.code;
        opt.textContent = `${n.code} - ${n.title.substring(0, 60)}... (${n.year})`;
        editParamNormCode.appendChild(opt);
      });
    }

    if (adminFilterNorm) {
      adminFilterNorm.innerHTML = '<option value="TODOS">Todas las normas</option>';
      state.adminNormsList.forEach(n => {
        const opt = document.createElement('option');
        opt.value = n.code;
        opt.textContent = n.code;
        adminFilterNorm.appendChild(opt);
      });
    }
  }

  function switchAdminSubTab(subTab) {
    state.adminSubTab = subTab;
    document.querySelectorAll('.admin-tab-btn').forEach(btn => {
      if (btn.getAttribute('data-admin-tab') === subTab) {
        btn.classList.add('bg-brand-600', 'text-white', 'shadow-sm');
        btn.classList.remove('bg-slate-100', 'dark:bg-slate-800', 'text-slate-700', 'dark:text-slate-300');
      } else {
        btn.classList.remove('bg-brand-600', 'text-white', 'shadow-sm');
        btn.classList.add('bg-slate-100', 'dark:bg-slate-800', 'text-slate-700', 'dark:text-slate-300');
      }
    });

    const sections = {
      parametros: document.getElementById('adminSectionParametros'),
      normas: document.getElementById('adminSectionNormas'),
      pendientes: document.getElementById('adminSectionPendientes'),
      historial: document.getElementById('adminSectionHistorial'),
      mensajes: document.getElementById('adminSectionMensajes'),
      importar: document.getElementById('adminSectionImportar')
    };

    Object.keys(sections).forEach(k => {
      if (sections[k]) {
        if (k === subTab) sections[k].classList.remove('hidden');
        else sections[k].classList.add('hidden');
      }
    });

    if (subTab === 'parametros') loadAdminParameters();
    else if (subTab === 'normas') loadAdminNorms();
    else if (subTab === 'pendientes') loadAdminPendingVerification();
    else if (subTab === 'historial') loadAdminAuditLogs();
    else if (subTab === 'mensajes') loadAdminInquiries();

    if (window.lucide) window.lucide.createIcons();
  }

  async function loginAdmin() {
    const tokenInput = document.getElementById('adminTokenInput');
    if (!tokenInput) return;
    const token = tokenInput.value.trim();

    try {
      const res = await fetch('/api/admin/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: token })
      });

      if (res.ok) {
        state.adminToken = token;
        localStorage.setItem('econorma_admin_token', token);
        showToast('Sesión administrativa iniciada correctamente', 'success');
        initAdminView();
      } else {
        showToast('Clave de acceso administrativa incorrecta', 'error');
      }
    } catch (e) {
      showToast('Error al autenticar', 'error');
    }
  }

  function logoutAdmin() {
    state.adminToken = '';
    localStorage.removeItem('econorma_admin_token');
    showToast('Sesión administrativa cerrada', 'info');
    initAdminView();
  }

  // --- GESTIÓN DE PARÁMETROS: CARGA, FILTROS Y TABLA ---

  async function loadAdminParameters() {
    const tbody = document.getElementById('adminParamsTableBody');
    if (!tbody) return;

    tbody.innerHTML = `<tr><td colspan="9" class="text-center py-6 text-slate-400">Consultando base de datos...</td></tr>`;

    const searchInput = document.getElementById('adminParamSearchInput');
    const filterInst = document.getElementById('adminFilterInstrument');
    const filterMed = document.getElementById('adminFilterMedium');
    const filterSec = document.getElementById('adminFilterSector');
    const filterVer = document.getElementById('adminFilterVerif');
    const filterNorm = document.getElementById('adminFilterNorm');
    const filterStat = document.getElementById('adminFilterStatus');

    const params = new URLSearchParams();
    if (searchInput && searchInput.value.trim()) params.set('q', searchInput.value.trim());
    if (filterInst && filterInst.value !== 'TODOS') params.set('instrument', filterInst.value);
    if (filterMed && filterMed.value !== 'TODOS') params.set('medium', filterMed.value);
    if (filterSec && filterSec.value !== 'TODOS') params.set('sector', filterSec.value);
    if (filterVer && filterVer.value !== 'TODOS') params.set('verification_status', filterVer.value);
    if (filterNorm && filterNorm.value !== 'TODOS') params.set('norm_code', filterNorm.value);
    if (filterStat && filterStat.value !== 'TODOS') params.set('status', filterStat.value);

    params.set('page', state.adminParamPage);
    params.set('page_size', state.adminParamPageSize);

    try {
      const res = await fetch(`/api/admin/parameters?${params.toString()}`, {
        headers: { 'x-admin-token': state.adminToken }
      });
      if (res.ok) {
        const data = await res.json();
        const items = data.results || [];
        state.adminParamTotal = data.total || 0;

        if (items.length === 0) {
          tbody.innerHTML = `<tr><td colspan="9" class="text-center py-8 text-slate-400">No se encontraron parámetros con los criterios seleccionados.</td></tr>`;
          renderAdminParamPagination();
          return;
        }

        tbody.innerHTML = items.map(p => `
          <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/50 text-xs border-b border-slate-100 dark:border-slate-800">
            <td class="px-3 py-3 font-mono font-bold text-slate-400">${p.id}</td>
            <td class="px-3 py-3">
              <div class="font-bold text-slate-900 dark:text-white">${p.parameter_name}</div>
              ${p.symbol ? `<span class="text-[11px] font-mono text-emerald-600 font-semibold">(${p.symbol})</span>` : ''}
              ${p.cas_number ? `<span class="text-[10px] text-slate-400 block font-mono">CAS: ${p.cas_number}</span>` : ''}
            </td>
            <td class="px-3 py-3">
              <span class="px-2 py-0.5 rounded text-[11px] font-bold ${getInstrumentBgClass(p.instrument)}">${p.instrument}</span>
            </td>
            <td class="px-3 py-3">
              <div class="font-semibold text-slate-700 dark:text-slate-300">${p.environmental_medium}</div>
              ${p.sector ? `<div class="text-[11px] text-slate-400">${p.sector}</div>` : ''}
            </td>
            <td class="px-3 py-3 max-w-xs">
              <div class="font-medium text-slate-800 dark:text-slate-200 line-clamp-1">${p.category}</div>
              ${p.subcategory ? `<div class="text-[11px] text-slate-400 line-clamp-1">${p.subcategory}</div>` : ''}
            </td>
            <td class="px-3 py-3 font-mono font-bold text-emerald-700 dark:text-emerald-400">
              ${p.value_text || formatParamValue(p)} <span class="text-[11px] font-semibold text-slate-500">${p.unit}</span>
            </td>
            <td class="px-3 py-3">
              <div class="font-semibold text-slate-800 dark:text-slate-200">${p.norm_code}</div>
              <div class="text-[10px] text-slate-400">${p.annex || ''}</div>
            </td>
            <td class="px-3 py-3">
              ${getVerificationBadgeHtml(p.verification_status)}
              <span class="text-[10px] text-slate-400 block mt-0.5">${p.status}</span>
            </td>
            <td class="px-3 py-3 text-center">
              <div class="flex items-center justify-center gap-1.5">
                <button onclick="EcoNorma.openParamDetail(${p.id})" title="Ver ficha técnica" class="p-1.5 text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800">
                  <i data-lucide="eye" class="w-4 h-4"></i>
                </button>
                <button onclick="EcoNorma.openEditParamModal(${p.id})" title="Editar parámetro completo" class="p-1.5 text-sky-600 hover:text-sky-800 dark:text-sky-400 rounded-lg hover:bg-sky-50 dark:hover:bg-sky-950">
                  <i data-lucide="edit-3" class="w-4 h-4"></i>
                </button>
                ${p.verification_status !== 'VERIFICADO' ? `
                  <button onclick="EcoNorma.quickVerifyParam(${p.id})" title="Aprobar y verificar" class="p-1.5 text-emerald-600 hover:text-emerald-800 dark:text-emerald-400 rounded-lg hover:bg-emerald-50 dark:hover:bg-emerald-950">
                    <i data-lucide="check-circle" class="w-4 h-4"></i>
                  </button>
                ` : ''}
                <button onclick="EcoNorma.deleteParam(${p.id}, '${p.parameter_name.replace(/'/g, "\\'")}')" title="Desactivar o retirar" class="p-1.5 text-rose-600 hover:text-rose-800 dark:text-rose-400 rounded-lg hover:bg-rose-50 dark:hover:bg-rose-950">
                  <i data-lucide="trash-2" class="w-4 h-4"></i>
                </button>
              </div>
            </td>
          </tr>
        `).join('');

        renderAdminParamPagination();
        if (window.lucide) window.lucide.createIcons();
      }
    } catch (e) {
      console.warn('Error cargando parámetros admin:', e);
    }
  }

  function renderAdminParamPagination() {
    const container = document.getElementById('adminParamPagination');
    if (!container) return;
    const totalPages = Math.ceil(state.adminParamTotal / state.adminParamPageSize);

    container.innerHTML = `
      <span>Total: <strong>${state.adminParamTotal}</strong> parámetros registrados</span>
      <div class="flex items-center space-x-2">
        <button onclick="EcoNorma.changeAdminParamPage(${state.adminParamPage - 1})" ${state.adminParamPage <= 1 ? 'disabled' : ''} class="px-2.5 py-1 border border-slate-200 dark:border-slate-700 rounded-lg disabled:opacity-40">Anterior</button>
        <span>Página ${state.adminParamPage} de ${Math.max(1, totalPages)}</span>
        <button onclick="EcoNorma.changeAdminParamPage(${state.adminParamPage + 1})" ${state.adminParamPage >= totalPages ? 'disabled' : ''} class="px-2.5 py-1 border border-slate-200 dark:border-slate-700 rounded-lg disabled:opacity-40">Siguiente</button>
      </div>
    `;
  }

  function changeAdminParamPage(p) {
    const totalPages = Math.ceil(state.adminParamTotal / state.adminParamPageSize);
    if (p < 1 || p > totalPages) return;
    state.adminParamPage = p;
    loadAdminParameters();
  }

  // --- MODAL DE EDICIÓN Y CREACIÓN DE PARÁMETRO ---

  function openNewParamModal() {
    const modal = dom.adminParamModal;
    if (!modal) return;
    document.getElementById('adminParamModalTitle').innerHTML = `<i data-lucide="plus-circle" class="w-5 h-5 text-brand-600"></i> Registrar Nuevo Parámetro Ambiental`;
    document.getElementById('editParamId').value = '';
    document.getElementById('adminParamForm').reset();
    document.getElementById('editParamNormInheritedUrl').textContent = 'Selecciona una norma para visualizar su enlace oficial heredado.';
    
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    if (window.lucide) window.lucide.createIcons();
  }

  async function openEditParamModal(paramId) {
    try {
      const res = await fetch(`/api/admin/parameters/${paramId}`, {
        headers: { 'x-admin-token': state.adminToken }
      });
      if (res.ok) {
        const p = await res.json();
        const modal = dom.adminParamModal;
        if (!modal) return;

        document.getElementById('adminParamModalTitle').innerHTML = `<i data-lucide="edit-3" class="w-5 h-5 text-brand-600"></i> Editar Parámetro Ambiental (ID: ${p.id})`;
        document.getElementById('editParamId').value = p.id;
        
        document.getElementById('editParamName').value = p.parameter_name || '';
        document.getElementById('editParamAltNames').value = p.alternative_names || '';
        document.getElementById('editParamSymbol').value = p.symbol || '';
        document.getElementById('editParamCas').value = p.cas_number || '';
        
        document.getElementById('editParamInstrument').value = p.instrument || 'ECA';
        document.getElementById('editParamMedium').value = p.environmental_medium || '';
        document.getElementById('editParamSector').value = p.sector || '';
        document.getElementById('editParamCategory').value = p.category || '';
        document.getElementById('editParamSubcategory').value = p.subcategory || '';
        
        document.getElementById('editParamLimitType').value = p.limit_type || 'Máximo';
        document.getElementById('editParamMinVal').value = p.min_value !== null ? p.min_value : '';
        document.getElementById('editParamMaxVal').value = p.max_value !== null ? p.max_value : '';
        document.getElementById('editParamValText').value = p.value_text || '';
        document.getElementById('editParamUnit').value = p.unit || '';
        
        document.getElementById('editParamNormCode').value = p.norm_code || '';
        document.getElementById('editParamAnnex').value = p.annex || '';
        document.getElementById('editParamObservations').value = p.observations || '';
        document.getElementById('editParamSourceOverride').value = p.source_url_override || '';

        onNormSelectionChange();

        document.getElementById('editParamVerifStatus').value = p.verification_status || 'VERIFICADO';
        document.getElementById('editParamStatus').value = p.status || 'VIGENTE';
        document.getElementById('editParamAdminComment').value = '';

        modal.classList.remove('hidden');
        modal.classList.add('flex');
        if (window.lucide) window.lucide.createIcons();
      }
    } catch (e) {
      showToast('Error al cargar datos del parámetro para edición', 'error');
    }
  }

  function closeAdminParamModal() {
    if (dom.adminParamModal) {
      dom.adminParamModal.classList.add('hidden');
      dom.adminParamModal.classList.remove('flex');
    }
  }

  function onNormSelectionChange() {
    const normSelect = document.getElementById('editParamNormCode');
    const inheritedUrlEl = document.getElementById('editParamNormInheritedUrl');
    if (!normSelect || !inheritedUrlEl) return;

    const selectedCode = normSelect.value;
    const normObj = state.adminNormsList.find(n => n.code === selectedCode);
    if (normObj) {
      inheritedUrlEl.textContent = normObj.official_url || 'Sin URL registrada';
    } else {
      inheritedUrlEl.textContent = 'Selecciona una norma oficial para heredar su URL';
    }
  }

  function setUnitQuick(unitStr) {
    const unitInput = document.getElementById('editParamUnit');
    if (unitInput) {
      unitInput.value = unitStr;
      unitInput.focus();
    }
  }

  function testUrl(url) {
    if (!url || url.trim() === '' || url.includes('Selecciona')) {
      showToast('Por favor introduce primero una URL válida para probar.', 'warning');
      return;
    }
    const clean = url.trim();
    if (!clean.startsWith('http://') && !clean.startsWith('https://')) {
      showToast('La URL debe comenzar con http:// o https://', 'warning');
      return;
    }
    window.open(clean, '_blank');
  }

  async function saveParamForm(e) {
    e.preventDefault();
    const paramId = document.getElementById('editParamId').value;
    const isNew = !paramId;

    const confirmMsg = isNew 
      ? "¿Deseas registrar este nuevo parámetro en la base de datos oficial?"
      : "¿Deseas guardar las modificaciones realizadas en este registro?";

    if (!confirm(confirmMsg)) return;

    const minValStr = document.getElementById('editParamMinVal').value;
    const maxValStr = document.getElementById('editParamMaxVal').value;
    const normCode = document.getElementById('editParamNormCode').value;
    const normObj = state.adminNormsList.find(n => n.code === normCode) || {};

    const payload = {
      parameter_name: document.getElementById('editParamName').value.trim(),
      alternative_names: document.getElementById('editParamAltNames').value.trim() || null,
      symbol: document.getElementById('editParamSymbol').value.trim() || null,
      cas_number: document.getElementById('editParamCas').value.trim() || null,
      instrument: document.getElementById('editParamInstrument').value,
      environmental_medium: document.getElementById('editParamMedium').value.trim(),
      sector: document.getElementById('editParamSector').value.trim() || null,
      category: document.getElementById('editParamCategory').value.trim(),
      subcategory: document.getElementById('editParamSubcategory').value.trim() || null,
      limit_type: document.getElementById('editParamLimitType').value,
      min_value: minValStr !== '' ? parseFloat(minValStr) : null,
      max_value: maxValStr !== '' ? parseFloat(maxValStr) : null,
      value_text: document.getElementById('editParamValText').value.trim() || null,
      unit: document.getElementById('editParamUnit').value.trim(),
      norm_code: normCode,
      norm_name: normObj.title || normCode,
      year: normObj.year || new Date().getFullYear(),
      issuing_entity: normObj.issuing_entity || 'MINAM',
      annex: document.getElementById('editParamAnnex').value.trim() || null,
      observations: document.getElementById('editParamObservations').value.trim() || null,
      source_url_override: document.getElementById('editParamSourceOverride').value.trim() || null,
      verification_status: document.getElementById('editParamVerifStatus').value,
      status: document.getElementById('editParamStatus').value,
      admin_comment: document.getElementById('editParamAdminComment').value.trim() || null
    };

    try {
      const url = isNew ? '/api/admin/parameters' : `/api/admin/parameters/${paramId}`;
      const method = isNew ? 'POST' : 'PUT';

      const res = await fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
          'x-admin-token': state.adminToken
        },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        const data = await res.json();
        showToast(data.message || 'Parámetro guardado exitosamente', 'success');
        closeAdminParamModal();
        loadAdminParameters();
        fetchSystemStats();
      } else {
        const err = await res.json();
        showToast(`Error al guardar: ${err.detail || 'Verifica los campos'}`, 'error');
      }
    } catch (e) {
      showToast('Error de conexión con el servidor', 'error');
    }
  }

  async function verifyParamCurrentModal() {
    const paramId = document.getElementById('editParamId').value;
    if (!paramId) {
      document.getElementById('editParamVerifStatus').value = 'VERIFICADO';
      showToast('Estado cambiado a Verificado. Guarda el formulario para confirmar.', 'info');
      return;
    }
    await quickVerifyParam(parseInt(paramId, 10));
    closeAdminParamModal();
  }

  async function quickVerifyParam(id) {
    try {
      const res = await fetch(`/api/admin/parameters/${id}/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-admin-token': state.adminToken
        },
        body: JSON.stringify({ comment: 'Verificación manual aprobada por el administrador' })
      });

      if (res.ok) {
        showToast('Parámetro marcado como Verificado y publicado exitosamente', 'success');
        loadAdminParameters();
        loadAdminPendingVerification();
        fetchSystemStats();
      } else {
        showToast('Error al verificar el parámetro', 'error');
      }
    } catch (e) {
      showToast('Error de conexión', 'error');
    }
  }

  async function deleteParam(id, name) {
    if (!confirm(`¿Estás seguro de que deseas retirar el parámetro "${name}" (ID ${id})? Quedará marcado como inactivo.`)) return;

    try {
      const res = await fetch(`/api/admin/parameters/${id}`, {
        method: 'DELETE',
        headers: { 'x-admin-token': state.adminToken }
      });

      if (res.ok) {
        showToast(`Parámetro ID ${id} desactivado correctamente`, 'info');
        loadAdminParameters();
        fetchSystemStats();
      } else {
        showToast('No se pudo desactivar el parámetro', 'error');
      }
    } catch (e) {
      showToast('Error de conexión', 'error');
    }
  }

  // --- GESTIÓN DE NORMAS (CRUD Y ACTUALIZACIÓN PROPAGADA) ---

  async function loadAdminNorms() {
    const tbody = document.getElementById('adminNormsTableBody');
    if (!tbody) return;
    tbody.innerHTML = `<tr><td colspan="8" class="text-center py-6 text-slate-400">Consultando catálogo de normas...</td></tr>`;

    const searchInput = document.getElementById('adminNormSearchInput');
    const q = searchInput ? searchInput.value.trim() : '';

    try {
      const res = await fetch(`/api/admin/norms?q=${encodeURIComponent(q)}`, {
        headers: { 'x-admin-token': state.adminToken }
      });
      if (res.ok) {
        const data = await res.json();
        state.adminNormsList = data.norms || [];

        if (state.adminNormsList.length === 0) {
          tbody.innerHTML = `<tr><td colspan="8" class="text-center py-8 text-slate-400">No se encontraron normas registradas.</td></tr>`;
          return;
        }

        tbody.innerHTML = state.adminNormsList.map(n => `
          <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/50 text-xs border-b border-slate-100 dark:border-slate-800">
            <td class="px-4 py-3 font-mono font-bold text-slate-900 dark:text-white">${n.code}</td>
            <td class="px-4 py-3">
              <span class="font-semibold text-slate-700 dark:text-slate-300">${n.norm_type || 'Decreto Supremo'}</span>
              <div class="text-[10px] font-mono text-slate-400">${n.norm_number}</div>
            </td>
            <td class="px-4 py-3 max-w-sm">
              <div class="font-medium text-slate-800 dark:text-slate-200 line-clamp-2">${n.title}</div>
            </td>
            <td class="px-4 py-3">
              <div class="font-semibold text-slate-700 dark:text-slate-300">${n.issuing_entity}</div>
              <div class="text-[10px] text-slate-400">${n.year}</div>
            </td>
            <td class="px-4 py-3">
              <span class="px-2 py-0.5 rounded text-[11px] font-bold ${getStatusBadgeClass(n.status)}">${n.status}</span>
            </td>
            <td class="px-4 py-3 max-w-xs">
              <div class="flex items-center gap-1.5">
                <a href="${n.official_url}" target="_blank" rel="noopener noreferrer" class="text-emerald-600 hover:underline font-mono truncate block max-w-[160px] text-[11px]" title="${n.official_url}">
                  ${n.official_url}
                </a>
                <button onclick="EcoNorma.testUrl('${n.official_url}')" title="Probar enlace" class="p-1 text-slate-400 hover:text-emerald-600">
                  <i data-lucide="external-link" class="w-3.5 h-3.5"></i>
                </button>
              </div>
            </td>
            <td class="px-4 py-3 font-mono font-bold text-center text-slate-700 dark:text-slate-300">
              ${n.parameters_count || 0}
            </td>
            <td class="px-4 py-3 text-center">
              <div class="flex items-center justify-center gap-1.5">
                <button onclick="EcoNorma.openEditNormModal('${n.code}')" title="Editar norma y corregir URL" class="p-1.5 text-sky-600 hover:text-sky-800 rounded-lg hover:bg-sky-50 dark:hover:bg-sky-950">
                  <i data-lucide="edit-3" class="w-4 h-4"></i>
                </button>
                <button onclick="EcoNorma.filterParamsByNorm('${n.code}')" title="Ver todos sus parámetros" class="p-1.5 text-emerald-600 hover:text-emerald-800 rounded-lg hover:bg-emerald-50 dark:hover:bg-emerald-950">
                  <i data-lucide="search" class="w-4 h-4"></i>
                </button>
              </div>
            </td>
          </tr>
        `).join('');

        if (window.lucide) window.lucide.createIcons();
      }
    } catch (e) {
      console.warn('Error cargando normas admin:', e);
    }
  }

  function filterParamsByNorm(normCode) {
    switchAdminSubTab('parametros');
    const normSelect = document.getElementById('adminFilterNorm');
    if (normSelect) {
      normSelect.value = normCode;
      loadAdminParameters();
    }
  }

  function openNewNormModal() {
    const modal = dom.adminNormModal;
    if (!modal) return;

    document.getElementById('adminNormModalTitle').innerHTML = `<i data-lucide="plus-circle" class="w-5 h-5 text-brand-600"></i> Registrar Nueva Norma Oficial`;
    document.getElementById('editNormIsNew').value = '1';
    document.getElementById('adminNormForm').reset();
    document.getElementById('editNormCode').removeAttribute('readonly');

    modal.classList.remove('hidden');
    modal.classList.add('flex');
    if (window.lucide) window.lucide.createIcons();
  }

  async function openEditNormModal(normCode) {
    try {
      const res = await fetch(`/api/admin/norms/${encodeURIComponent(normCode)}`, {
        headers: { 'x-admin-token': state.adminToken }
      });
      if (res.ok) {
        const n = await res.json();
        const modal = dom.adminNormModal;
        if (!modal) return;

        document.getElementById('adminNormModalTitle').innerHTML = `<i data-lucide="edit-3" class="w-5 h-5 text-brand-600"></i> Editar Norma Oficial (${n.code})`;
        document.getElementById('editNormIsNew').value = '0';
        
        document.getElementById('editNormCode').value = n.code;
        document.getElementById('editNormCode').setAttribute('readonly', 'true');
        document.getElementById('editNormType').value = n.norm_type || 'Decreto Supremo';
        document.getElementById('editNormNumber').value = n.norm_number || '';
        document.getElementById('editNormEntity').value = n.issuing_entity || '';
        document.getElementById('editNormInstrument').value = n.instrument || 'ECA';
        document.getElementById('editNormYear').value = n.year || '';
        document.getElementById('editNormTitle').value = n.title || '';
        document.getElementById('editNormOfficialUrl').value = n.official_url || '';
        document.getElementById('editNormAlternateUrl').value = n.alternate_url || '';
        document.getElementById('editNormStatus').value = n.status || 'VIGENTE';
        document.getElementById('editNormSummary').value = n.summary || '';
        document.getElementById('editNormAdminComment').value = '';

        modal.classList.remove('hidden');
        modal.classList.add('flex');
        if (window.lucide) window.lucide.createIcons();
      }
    } catch (e) {
      showToast('Error al cargar datos de la norma para edición', 'error');
    }
  }

  function closeAdminNormModal() {
    if (dom.adminNormModal) {
      dom.adminNormModal.classList.add('hidden');
      dom.adminNormModal.classList.remove('flex');
    }
  }

  async function saveNormForm(e) {
    e.preventDefault();
    const isNew = document.getElementById('editNormIsNew').value === '1';
    const normCode = document.getElementById('editNormCode').value.trim();

    const confirmMsg = isNew
      ? "¿Deseas registrar esta nueva norma oficial en el sistema?"
      : "¿Deseas guardar los cambios en esta norma? Todos los parámetros vinculados adoptarán automáticamente la nueva URL oficial.";

    if (!confirm(confirmMsg)) return;

    const payload = {
      code: normCode,
      norm_type: document.getElementById('editNormType').value,
      norm_number: document.getElementById('editNormNumber').value.trim(),
      title: document.getElementById('editNormTitle').value.trim(),
      issuing_entity: document.getElementById('editNormEntity').value.trim(),
      instrument: document.getElementById('editNormInstrument').value,
      year: parseInt(document.getElementById('editNormYear').value, 10) || new Date().getFullYear(),
      official_url: document.getElementById('editNormOfficialUrl').value.trim(),
      alternate_url: document.getElementById('editNormAlternateUrl').value.trim() || null,
      status: document.getElementById('editNormStatus').value,
      summary: document.getElementById('editNormSummary').value.trim() || null,
      admin_comment: document.getElementById('editNormAdminComment').value.trim() || null
    };

    try {
      const url = isNew ? '/api/admin/norms' : `/api/admin/norms/${encodeURIComponent(normCode)}`;
      const method = isNew ? 'POST' : 'PUT';

      const res = await fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
          'x-admin-token': state.adminToken
        },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        const data = await res.json();
        showToast(data.message || 'Norma guardada exitosamente', 'success');
        closeAdminNormModal();
        await preloadAdminNormsCatalog();
        loadAdminNorms();
      } else {
        const err = await res.json();
        showToast(`Error al guardar norma: ${err.detail || 'Verifica los campos'}`, 'error');
      }
    } catch (e) {
      showToast('Error de conexión con el servidor', 'error');
    }
  }

  // --- HISTORIAL DE AUDITORÍA Y TRAZABILIDAD ---

  async function loadAdminAuditLogs() {
    const tbody = document.getElementById('adminAuditLogsTableBody');
    if (!tbody) return;
    tbody.innerHTML = `<tr><td colspan="7" class="text-center py-6 text-slate-400">Consultando historial de auditoría...</td></tr>`;

    try {
      const res = await fetch('/api/admin/audit-logs?limit=150', {
        headers: { 'x-admin-token': state.adminToken }
      });
      if (res.ok) {
        const data = await res.json();
        const logs = data.logs || [];
        if (logs.length === 0) {
          tbody.innerHTML = `<tr><td colspan="7" class="text-center py-8 text-slate-400">No hay registros de modificaciones aún.</td></tr>`;
          return;
        }

        tbody.innerHTML = logs.map(l => `
          <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/50 text-xs border-b border-slate-100 dark:border-slate-800">
            <td class="px-3 py-2.5 font-mono text-[11px] text-slate-400">${l.created_at}</td>
            <td class="px-3 py-2.5">
              <span class="font-bold text-slate-800 dark:text-slate-200">${l.target_name || l.target_id}</span>
              <span class="text-[10px] text-slate-400 block">${l.target_type} #${l.target_id}</span>
            </td>
            <td class="px-3 py-2.5 font-bold font-mono text-emerald-600">${l.action}</td>
            <td class="px-3 py-2.5 font-mono text-slate-500">${l.field_name || '-'}</td>
            <td class="px-3 py-2.5 font-mono text-rose-600 dark:text-rose-400 line-through truncate max-w-xs">${l.old_value || '-'}</td>
            <td class="px-3 py-2.5 font-mono text-emerald-600 dark:text-emerald-400 font-bold truncate max-w-xs">${l.new_value || '-'}</td>
            <td class="px-3 py-2.5 text-slate-500 text-[11px]">${l.comment || 'Modificación manual'}</td>
          </tr>
        `).join('');

        if (window.lucide) window.lucide.createIcons();
      }
    } catch (e) {
      console.warn('Error cargando auditoría:', e);
    }
  }

  // --- PENDIENTES DE VERIFICACIÓN ---

  async function loadAdminPendingVerification() {
    const container = document.getElementById('adminPendingContainer');
    if (!container) return;
    container.innerHTML = `<div class="py-6 text-center text-slate-400 text-xs">Cargando cola de verificación...</div>`;

    try {
      const res = await fetch('/api/admin/pending-verification', {
        headers: { 'x-admin-token': state.adminToken }
      });
      if (res.ok) {
        const data = await res.json();
        const items = data.items || [];
        if (items.length === 0) {
          container.innerHTML = `
            <div class="py-8 text-center text-slate-500">
              <i data-lucide="check-check" class="w-8 h-8 text-emerald-500 mx-auto mb-2"></i>
              ¡Todo al día! No hay parámetros pendientes de verificación o en revisión.
            </div>
          `;
        } else {
          container.innerHTML = items.map(p => `
            <div class="p-4 bg-slate-50 dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
              <div>
                <div class="flex items-center gap-2">
                  <span class="font-bold text-sm text-slate-900 dark:text-white">${p.parameter_name}</span>
                  <span class="px-2 py-0.5 rounded text-[10px] font-bold ${getInstrumentBgClass(p.instrument)}">${p.instrument}</span>
                  ${getVerificationBadgeHtml(p.verification_status)}
                </div>
                <div class="text-slate-500 mt-1">
                  Categoría: <strong>${p.category}</strong> ${p.subcategory ? `· ${p.subcategory}` : ''} | Límite: <strong>${p.value_text || formatParamValue(p)} ${p.unit}</strong> (${p.norm_code})
                </div>
                ${p.admin_comment ? `<div class="text-[11px] text-amber-600 mt-0.5">Nota: ${p.admin_comment}</div>` : ''}
              </div>

              <div class="flex items-center gap-2 self-end sm:self-center">
                <button onclick="EcoNorma.openEditParamModal(${p.id})" class="px-3 py-1.5 bg-sky-50 text-sky-700 hover:bg-sky-100 rounded-xl font-bold flex items-center gap-1 border border-sky-200">
                  <i data-lucide="edit-3" class="w-3.5 h-3.5"></i> Revisar y Editar
                </button>
                <button onclick="EcoNorma.quickVerifyParam(${p.id})" class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold shadow-sm flex items-center gap-1">
                  <i data-lucide="check-circle" class="w-3.5 h-3.5"></i> Aprobar
                </button>
              </div>
            </div>
          `).join('');
        }
        if (window.lucide) window.lucide.createIcons();
      }
    } catch (e) {
      console.warn('Error cargando pendientes admin:', e);
    }
  }

  // --- MENSAJES Y OBSERVACIONES ---

  async function loadAdminInquiries() {
    const container = document.getElementById('adminInquiriesContainer');
    if (!container) return;
    container.innerHTML = `<div class="py-6 text-center text-slate-400 text-xs">Cargando observaciones...</div>`;

    try {
      const res = await fetch('/api/admin/inquiries', {
        headers: { 'x-admin-token': state.adminToken }
      });
      if (res.ok) {
        const data = await res.json();
        const inqs = data.inquiries || [];
        if (inqs.length === 0) {
          container.innerHTML = `<div class="py-8 text-center text-slate-400 text-xs">No hay observaciones recibidas aún.</div>`;
          return;
        }
        container.innerHTML = inqs.map(i => `
          <div class="p-4 bg-slate-50 dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 space-y-2 text-xs">
            <div class="flex items-center justify-between">
              <span class="font-bold text-slate-900 dark:text-white text-sm">${i.name} (${i.email})</span>
              <span class="px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold">${i.inquiry_type}</span>
            </div>
            <div class="font-semibold text-slate-700 dark:text-slate-300">Asunto: ${i.subject || 'Sin asunto'}</div>
            <p class="text-slate-600 dark:text-slate-400 bg-white dark:bg-slate-900/60 p-3 rounded-xl border border-slate-100 dark:border-slate-800">${i.message}</p>
            <div class="text-[10px] text-slate-400">Fecha de recepción: ${i.created_at}</div>
          </div>
        `).join('');
      }
    } catch (e) {
      console.warn('Error cargando mensajes:', e);
    }
  }

  // --- IMPORTACIÓN POR LOTE ---

  async function submitImportFile(e) {
    e.preventDefault();
    const fileInput = document.getElementById('adminImportFileInput');
    if (!fileInput || !fileInput.files[0]) {
      showToast('Selecciona un archivo .csv o .json', 'warning');
      return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    showToast('Validando e importando archivo...', 'info');

    try {
      const res = await fetch('/api/admin/import', {
        method: 'POST',
        headers: { 'x-admin-token': state.adminToken },
        body: formData
      });

      if (res.ok) {
        const data = await res.json();
        showToast(data.message || 'Importación completada', 'success');
        fileInput.value = '';
        fetchSystemStats();
        switchAdminSubTab('parametros');
      } else {
        const err = await res.json();
        showToast(`Error de importación: ${err.detail}`, 'error');
      }
    } catch (e) {
      showToast('Error al procesar la importación', 'error');
    }
  }

  // --- RESPALDO JSON ---

  async function downloadBackup() {
    try {
      const res = await fetch('/api/admin/export/backup', {
        headers: { 'x-admin-token': state.adminToken }
      });
      if (res.ok) {
        const data = await res.json();
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `econorma_backup_${new Date().toISOString().slice(0, 10)}.json`;
        a.click();
        URL.revokeObjectURL(url);
        showToast('Respaldo descargado exitosamente', 'success');
      }
    } catch (e) {
      showToast('Error al descargar respaldo', 'error');
    }
  }

  // --- UTILIDADES PÚBLICAS Y EVENTOS ---

  function exportFilteredCsv() {
    const params = new URLSearchParams();
    if (state.query) params.set('q', state.query);
    if (state.instrument !== 'TODOS') params.set('instrument', state.instrument);
    if (state.medium !== 'TODOS') params.set('medium', state.medium);
    if (state.sector !== 'TODOS') params.set('sector', state.sector);
    if (state.category !== 'TODOS') params.set('category', state.category);

    window.location.href = `/api/parameters/export/csv?${params.toString()}`;
    showToast('Generando descarga de archivo CSV...', 'info');
  }

  function shareCurrentQuery() {
    const shareUrl = window.location.href;
    navigator.clipboard.writeText(shareUrl).then(() => {
      showToast('Enlace de búsqueda copiado al portapapeles', 'success');
    }).catch(() => {
      showToast('No se pudo copiar el enlace', 'error');
    });
  }

  function removeFilter(key) {
    if (key === 'q') state.query = '';
    else if (key === 'instrument') state.instrument = 'TODOS';
    else if (key === 'medium') state.medium = 'TODOS';
    else if (key === 'sector') state.sector = 'TODOS';
    else if (key === 'category') state.category = 'TODOS';
    else if (key === 'status') state.status = 'TODOS';

    syncFiltersToUI();
    state.page = 1;
    executeSearch();
  }

  function resetAllFilters() {
    state.query = '';
    state.instrument = 'TODOS';
    state.medium = 'TODOS';
    state.sector = 'TODOS';
    state.category = 'TODOS';
    state.subcategory = 'TODOS';
    state.status = 'TODOS';
    state.normCode = 'TODOS';
    state.entity = 'TODOS';
    state.year = '';
    state.page = 1;

    syncFiltersToUI();
    executeSearch();
  }

  function showToast(message, type = 'info') {
    if (!dom.toastContainer) return;
    const toast = document.createElement('div');
    
    let bg = 'bg-slate-900 text-white';
    let icon = 'info';
    if (type === 'success') {
      bg = 'bg-emerald-700 text-white';
      icon = 'check-circle';
    } else if (type === 'error') {
      bg = 'bg-rose-700 text-white';
      icon = 'alert-circle';
    } else if (type === 'warning') {
      bg = 'bg-amber-700 text-white';
      icon = 'alert-triangle';
    }

    toast.className = `${bg} px-4 py-3 rounded-2xl shadow-xl flex items-center space-x-2.5 text-xs font-semibold transform transition-all duration-300 translate-y-2 opacity-0 pointer-events-auto`;
    toast.innerHTML = `
      <i data-lucide="${icon}" class="w-4 h-4 flex-shrink-0"></i>
      <span>${message}</span>
    `;

    dom.toastContainer.appendChild(toast);
    if (window.lucide) window.lucide.createIcons();

    setTimeout(() => toast.classList.remove('translate-y-2', 'opacity-0'), 10);
    setTimeout(() => {
      toast.classList.add('opacity-0', 'translate-y-2');
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  function bindEvents() {
    if (dom.themeToggle) dom.themeToggle.addEventListener('click', toggleTheme);

    dom.navLinks.forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const tab = link.getAttribute('data-tab');
        navigateTo(tab);
      });
    });

    if (dom.mobileMenuBtn && dom.mobileMenu) {
      dom.mobileMenuBtn.addEventListener('click', () => {
        dom.mobileMenu.classList.toggle('hidden');
      });
    }

    if (dom.mainSearchInput) {
      dom.mainSearchInput.addEventListener('input', onSearchInput);
      dom.mainSearchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          hideAutocomplete();
          state.page = 1;
          navigateTo('busqueda', { q: dom.mainSearchInput.value });
        }
      });
    }

    if (dom.clearSearchBtn) {
      dom.clearSearchBtn.addEventListener('click', () => {
        state.query = '';
        if (dom.mainSearchInput) dom.mainSearchInput.value = '';
        dom.clearSearchBtn.classList.add('hidden');
        hideAutocomplete();
        state.page = 1;
        executeSearch();
      });
    }

    dom.quickChips.forEach(chip => {
      chip.addEventListener('click', () => {
        const val = chip.getAttribute('data-search');
        state.query = val;
        if (dom.mainSearchInput) dom.mainSearchInput.value = val;
        navigateTo('busqueda', { q: val });
      });
    });

    const filterEls = [
      { el: dom.filterInstrument, key: 'instrument' },
      { el: dom.filterMedium, key: 'medium' },
      { el: dom.filterSector, key: 'sector' },
      { el: dom.filterCategory, key: 'category' },
      { el: dom.filterEntity, key: 'entity' },
      { el: dom.filterStatus, key: 'status' }
    ];

    filterEls.forEach(({ el, key }) => {
      if (el) {
        el.addEventListener('change', (e) => {
          state[key] = e.target.value;
          state.page = 1;
          executeSearch();
        });
      }
    });

    if (dom.resetFiltersBtn) dom.resetFiltersBtn.addEventListener('click', resetAllFilters);
    if (dom.exportCsvBtn) dom.exportCsvBtn.addEventListener('click', exportFilteredCsv);
    if (dom.shareQueryBtn) dom.shareQueryBtn.addEventListener('click', shareCurrentQuery);

    if (dom.viewCardsBtn && dom.viewTableBtn) {
      dom.viewCardsBtn.addEventListener('click', () => {
        state.viewMode = 'cards';
        dom.viewCardsBtn.classList.add('bg-white', 'dark:bg-slate-700', 'shadow-sm');
        dom.viewTableBtn.classList.remove('bg-white', 'dark:bg-slate-700', 'shadow-sm');
        renderResults();
      });
      dom.viewTableBtn.addEventListener('click', () => {
        state.viewMode = 'table';
        dom.viewTableBtn.classList.add('bg-white', 'dark:bg-slate-700', 'shadow-sm');
        dom.viewCardsBtn.classList.remove('bg-white', 'dark:bg-slate-700', 'shadow-sm');
        renderResults();
      });
    }

    if (dom.detailModal) {
      dom.detailModal.addEventListener('click', (e) => {
        if (e.target === dom.detailModal) closeDetailModal();
      });
    }

    const compEvaluateBtn = document.getElementById('compEvaluateBtn');
    if (compEvaluateBtn) compEvaluateBtn.addEventListener('click', evaluateCompliance);

    const contactForm = document.getElementById('contactForm');
    if (contactForm) contactForm.addEventListener('submit', submitContactForm);

    const adminParamForm = document.getElementById('adminParamForm');
    if (adminParamForm) adminParamForm.addEventListener('submit', saveParamForm);

    const adminNormForm = document.getElementById('adminNormForm');
    if (adminNormForm) adminNormForm.addEventListener('submit', saveNormForm);

    const adminImportForm = document.getElementById('adminImportForm');
    if (adminImportForm) adminImportForm.addEventListener('submit', submitImportFile);

    document.addEventListener('click', (e) => {
      if (!e.target.closest('#mainSearchInput') && !e.target.closest('#autocompleteDropdown')) {
        hideAutocomplete();
      }
    });
  }

  return {
    init,
    navigateTo,
    openParamDetail,
    closeDetailModal,
    openComparatorWithParam,
    copyParamReference,
    removeFilter,
    resetAllFilters,
    changePage,
    searchByNorm,
    loginAdmin,
    logoutAdmin,
    downloadBackup,
    loadInterCategoryComparison,
    evaluateCompliance,
    switchAdminSubTab,
    loadAdminParameters,
    changeAdminParamPage,
    openNewParamModal,
    openEditParamModal,
    closeAdminParamModal,
    saveParamForm,
    verifyParamCurrentModal,
    quickVerifyParam,
    deleteParam,
    setUnitQuick,
    testUrl,
    onNormSelectionChange,
    loadAdminNorms,
    openNewNormModal,
    openEditNormModal,
    closeAdminNormModal,
    saveNormForm,
    filterParamsByNorm,
    loadAdminAuditLogs,
    loadAdminPendingVerification,
    onSearchInput
  };
})();

document.addEventListener('DOMContentLoaded', () => {
  EcoNorma.init();
});
