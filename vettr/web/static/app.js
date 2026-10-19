document.addEventListener("DOMContentLoaded", () => {
  const tickerForm = document.getElementById("ticker-form");
  const tickerInput = document.getElementById("ticker-input");
  const searchDropdown = document.getElementById("search-dropdown");
  const loadingCurtain = document.getElementById("loading-curtain");
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabPanels = document.querySelectorAll(".tab-panel");
  const btnExportDossier = document.getElementById("btn-export-dossier");
  const btnExportJson = document.getElementById("btn-export-json");
  const btnExportCsv = document.getElementById("btn-export-csv");
  const btnCopyBrief = document.getElementById("btn-copy-brief");
  const btnPrintReport = document.getElementById("btn-print-report");
  const presetBtns = document.querySelectorAll(".screener-switcher .preset-btn");
  const btnRunCompare = document.getElementById("btn-run-compare");
  const compareInput = document.getElementById("compare-input");

  // Command Palette Elements
  const cmdPalette = document.getElementById("command-palette");
  const cmdPaletteInput = document.getElementById("cmd-palette-input");
  const cmdPaletteResults = document.getElementById("cmd-palette-results");
  const btnOpenCmd = document.getElementById("btn-open-cmd");
  let cmdPaletteItems = [];
  let selectedCmdIndex = -1;

  // Metric Formula Inspector Modal Elements
  const metricInspectorModal = document.getElementById("metric-inspector-modal");
  const inspCloseBtn = document.getElementById("insp-close-btn");
  const inspBadge = document.getElementById("insp-badge");
  const inspTitle = document.getElementById("insp-title");
  const inspCitation = document.getElementById("insp-citation");
  const inspFormula = document.getElementById("insp-formula");
  const inspVal = document.getElementById("insp-val");
  const inspBenchmark = document.getElementById("insp-benchmark");
  const inspStatus = document.getElementById("insp-status");
  const inspDesc = document.getElementById("insp-desc");
  const inspCase = document.getElementById("insp-case");

  let currentTicker = "NVDA";
  let currentReportData = null;
  let debounceTimer = null;
  let selectedDropdownIndex = -1;

  let selectedDiscountRate = 10.0;
  let selectedTerminalGrowth = 3.0;

  // Tab switching
  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      tabBtns.forEach(b => b.classList.remove("active"));
      tabPanels.forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const targetId = btn.getAttribute("data-tab");
      const targetPanel = document.getElementById(targetId);
      if (targetPanel) {
        targetPanel.classList.add("active");
      }

      updateUrlHash(currentTicker, targetId);

      if (targetId === "tab-screener") {
        const activePreset = document.querySelector(".screener-switcher .preset-btn.active");
        const preset = activePreset ? activePreset.getAttribute("data-preset") : "mega_tech";
        loadScreener(preset);
      } else if (targetId === "tab-compare") {
        loadComparison(compareInput ? compareInput.value : "NVDA, AMD, INTC");
      }
    });
  });

  // Global Institutional Keyboard Hotkeys
  document.addEventListener("keydown", (e) => {
    // Cmd+K or Ctrl+K opens/toggles Command Palette
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      toggleCommandPalette();
      return;
    }

    // Esc closes modal, command palette, or search dropdown
    if (e.key === "Escape") {
      if (cmdPalette && !cmdPalette.classList.contains("hidden")) {
        closeCommandPalette();
        return;
      }
      if (metricInspectorModal && !metricInspectorModal.classList.contains("hidden")) {
        closeMetricInspector();
        return;
      }
      closeSecModal();
      searchDropdown.classList.add("hidden");
      return;
    }

    const isInputFocused = document.activeElement === tickerInput ||
                           document.activeElement === compareInput ||
                           document.activeElement === cmdPaletteInput ||
                           (document.getElementById("modal-filter-input") && document.activeElement === document.getElementById("modal-filter-input"));

    if (e.key === "/" && !isInputFocused) {
      e.preventDefault();
      tickerInput.focus();
      tickerInput.select();
      return;
    }

    if (!isInputFocused) {
      // 1 through 9, and 0 for tab 10
      if (e.key >= "1" && e.key <= "9") {
        const tabIdx = parseInt(e.key, 10) - 1;
        if (tabBtns[tabIdx]) {
          e.preventDefault();
          tabBtns[tabIdx].click();
        }
      } else if (e.key === "0" && tabBtns[9]) {
        e.preventDefault();
        tabBtns[9].click();
      } else if (e.key.toLowerCase() === "c") {
        e.preventDefault();
        btnCopyBrief.click();
      } else if (e.key.toLowerCase() === "p") {
        e.preventDefault();
        if (btnPrintReport) btnPrintReport.click();
      } else if (e.key.toLowerCase() === "m") {
        e.preventDefault();
        toggleChartMode();
      }
    }
  });

  // Autocomplete Live Search
  tickerInput.addEventListener("input", () => {
    clearTimeout(debounceTimer);
    const query = tickerInput.value.trim();
    if (query.length === 0) {
      searchDropdown.classList.add("hidden");
      return;
    }

    debounceTimer = setTimeout(async () => {
      try {
        const resp = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        if (!resp.ok) return;
        const matches = await resp.json();
        renderSearchDropdown(matches);
      } catch (err) {
        console.error("Autocomplete error:", err);
      }
    }, 120);
  });

  // Keyboard navigation for search dropdown
  tickerInput.addEventListener("keydown", (e) => {
    const items = searchDropdown.querySelectorAll(".search-item");
    if (searchDropdown.classList.contains("hidden") || items.length === 0) return;

    if (e.key === "ArrowDown") {
      e.preventDefault();
      selectedDropdownIndex = (selectedDropdownIndex + 1) % items.length;
      updateDropdownSelection(items);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      selectedDropdownIndex = (selectedDropdownIndex - 1 + items.length) % items.length;
      updateDropdownSelection(items);
    } else if (e.key === "Enter" && selectedDropdownIndex >= 0) {
      e.preventDefault();
      const selected = items[selectedDropdownIndex];
      const ticker = selected.getAttribute("data-ticker");
      tickerInput.value = ticker;
      searchDropdown.classList.add("hidden");
      runAnalysis(ticker);
    } else if (e.key === "Escape") {
      searchDropdown.classList.add("hidden");
    }
  });

  function updateDropdownSelection(items) {
    items.forEach((item, idx) => {
      if (idx === selectedDropdownIndex) {
        item.classList.add("selected");
        item.scrollIntoView({ block: "nearest" });
      } else {
        item.classList.remove("selected");
      }
    });
  }

  function renderSearchDropdown(matches) {
    searchDropdown.innerHTML = "";
    selectedDropdownIndex = -1;

    if (matches.length === 0) {
      searchDropdown.classList.add("hidden");
      return;
    }

    matches.forEach(item => {
      const div = document.createElement("div");
      div.className = "search-item";
      div.setAttribute("data-ticker", item.ticker);
      div.innerHTML = `
        <div class="item-left">
          <span class="item-ticker">${item.ticker}</span>
          <span class="item-name">${item.name}</span>
        </div>
        <span class="item-sector">${item.sector || ''}</span>
      `;

      div.addEventListener("click", () => {
        tickerInput.value = item.ticker;
        searchDropdown.classList.add("hidden");
        runAnalysis(item.ticker);
      });

      searchDropdown.appendChild(div);
    });

    searchDropdown.classList.remove("hidden");
  }

  // Close dropdown on outside click
  document.addEventListener("click", (e) => {
    if (!tickerForm.contains(e.target)) {
      searchDropdown.classList.add("hidden");
    }
  });

  // Form submit
  tickerForm.addEventListener("submit", (e) => {
    e.preventDefault();
    searchDropdown.classList.add("hidden");
    const ticker = tickerInput.value.trim().toUpperCase();
    if (ticker) {
      runAnalysis(ticker);
    }
  });

  // Copy Executive Brief to Clipboard
  btnCopyBrief.addEventListener("click", () => {
    if (!currentReportData) return;
    const mkt = currentReportData.market_data || {};
    const f = currentReportData.forensics || {};
    const b = f.beneish_m_score || {};
    const z = f.altman_z_score || {};
    const pi = f.piotroski_f_score || {};
    const val = currentReportData.valuation_model || {};

    const brief = [
      `[VETTR EXECUTIVE FORENSIC BRIEF: ${currentTicker}]`,
      `Price: $${(mkt.current_price || 0).toFixed(2)} | Market Cap: ${formatMoney(mkt.market_cap)}`,
      `Composite Forensic Risk: ${currentReportData.risk_score} / 100`,
      `Beneish M-Score: ${b.score || 'N/A'} (${b.status || 'N/A'})`,
      `Altman Z-Score: ${z.score || 'N/A'} (${z.zone || 'N/A'})`,
      `Piotroski F-Score: ${pi.score || 'N/A'}/9 (${pi.rating || 'N/A'})`,
      `Implied 10-Yr FCF Growth: ${val.implied_growth_10yr_pct || 'N/A'}% (${val.valuation_verdict || 'N/A'})`,
      `Accrual Anomalies: ${(f.anomalies || []).length} surfaced`,
      `Generated by VETTR Terminal (https://github.com/simpmix/vettr)`
    ].join("\n");

    navigator.clipboard.writeText(brief).then(() => {
      const orig = btnCopyBrief.textContent;
      btnCopyBrief.textContent = "COPIED ✓";
      setTimeout(() => { btnCopyBrief.textContent = orig; }, 1800);
    }).catch(err => {
      alert("Failed to copy brief: " + err);
    });
  });

  // Print / PDF Button
  if (btnPrintReport) {
    btnPrintReport.addEventListener("click", () => {
      window.print();
    });
  }

  // Export CSV
  btnExportCsv.addEventListener("click", () => {
    if (currentTicker) {
      window.location.href = `/api/export-csv/${currentTicker}`;
    }
  });

  // Export Dossier Markdown
  btnExportDossier.addEventListener("click", () => {
    if (currentTicker) {
      window.location.href = `/api/dossier/${currentTicker}`;
    }
  });

  // Export JSON Data
  btnExportJson.addEventListener("click", () => {
    if (!currentReportData) return;
    const blob = new Blob([JSON.stringify(currentReportData, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${currentTicker}_FORENSIC_DATA.json`;
    a.click();
    URL.revokeObjectURL(url);
  });

  // Screener preset buttons
  presetBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      presetBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const preset = btn.getAttribute("data-preset");
      loadScreener(preset);
    });
  });

  // Run Comparison
  if (btnRunCompare) {
    btnRunCompare.addEventListener("click", () => {
      loadComparison(compareInput.value);
    });
  }

  // Reverse DCF Scenario Control Click Handlers
  document.querySelectorAll(".scenario-pill-btn[data-rate]").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".scenario-pill-btn[data-rate]").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      selectedDiscountRate = parseFloat(btn.getAttribute("data-rate"));
      recalculateInteractiveDcf();
    });
  });

  document.querySelectorAll(".scenario-pill-btn[data-term]").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".scenario-pill-btn[data-term]").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      selectedTerminalGrowth = parseFloat(btn.getAttribute("data-term"));
      recalculateInteractiveDcf();
    });
  });

  function recalculateInteractiveDcf() {
    if (!currentReportData) return;
    const mkt = currentReportData.market_data || {};
    const mcap = mkt.market_cap || 0;
    const valModel = currentReportData.valuation_model || {};
    const fcfEst = valModel.fcf_estimate || 0;

    const fcfYield = mcap > 0 ? (fcfEst / mcap * 100) : 0;
    const implied = Math.max(0.0, selectedDiscountRate - (fcfYield * 1.2) + (selectedTerminalGrowth - 3.0) * 0.6 + 4.0);

    const growthEl = document.getElementById("val-implied-growth");
    const paramsEl = document.getElementById("val-params-display");
    const verdictEl = document.getElementById("valuation-verdict-badge");

    if (growthEl) growthEl.textContent = `${implied.toFixed(1)}%`;
    if (paramsEl) paramsEl.textContent = `${selectedDiscountRate}% / ${selectedTerminalGrowth}%`;

    let verdict = "MODERATE GROWTH EXPECTATIONS";
    if (implied > 20) {
      verdict = "PRICED FOR AGGRESSIVE GROWTH";
      if (verdictEl) verdictEl.className = "pill-badge red";
    } else if (implied > 8) {
      verdict = "MODERATE GROWTH PRICED IN";
      if (verdictEl) verdictEl.className = "pill-badge green";
    } else {
      verdict = "LOW GROWTH / VALUE PRICING";
      if (verdictEl) verdictEl.className = "pill-badge green";
    }
    if (verdictEl) verdictEl.textContent = verdict;

    // Highlight active cell in sensitivity matrix
    document.querySelectorAll(".matrix-table td").forEach(td => td.classList.remove("highlight"));
    const activeCellId = `m-${parseInt(selectedDiscountRate)}-${parseInt(selectedTerminalGrowth)}`;
    const activeCell = document.getElementById(activeCellId);
    if (activeCell) activeCell.classList.add("highlight");
  }

  function updateDcfMatrix(mcap, fcfEst) {
    const rates = [8.0, 10.0, 12.0];
    const terms = [2.0, 3.0, 4.0];
    const fcfYield = mcap > 0 ? (fcfEst / mcap * 100) : 0.0;

    rates.forEach(r => {
      terms.forEach(g => {
        const implied = Math.max(0.0, r - (fcfYield * 1.2) + (g - 3.0) * 0.6 + 4.0);
        const cell = document.getElementById(`m-${parseInt(r)}-${parseInt(g)}`);
        if (cell) {
          cell.textContent = `${implied.toFixed(1)}%`;
        }
      });
    });

    const activeCellId = `m-${parseInt(selectedDiscountRate)}-${parseInt(selectedTerminalGrowth)}`;
    const activeCell = document.getElementById(activeCellId);
    if (activeCell) activeCell.classList.add("highlight");
  }

  // Formatting helpers
  function formatMoney(num) {
    if (num === null || num === undefined) return "N/A";
    const abs = Math.abs(num);
    if (abs >= 1e12) return `$${(num / 1e12).toFixed(2)}T`;
    if (abs >= 1e9) return `$${(num / 1e9).toFixed(2)}B`;
    if (abs >= 1e6) return `$${(num / 1e6).toFixed(2)}M`;
    if (abs >= 1e3) return `$${(num / 1e3).toFixed(2)}K`;
    return `$${Number(num).toFixed(2)}`;
  }

  // --- Quick Navigation & Search History ---
  const RECENT_KEY = "vettr_recent_searches";

  function getRecentSearches() {
    try {
      return JSON.parse(localStorage.getItem(RECENT_KEY)) || ["NVDA", "AAPL", "MSFT", "TSLA", "AMD"];
    } catch {
      return ["NVDA", "AAPL", "MSFT", "TSLA", "AMD"];
    }
  }

  function saveRecentSearch(ticker) {
    if (!ticker) return;
    try {
      const clean = ticker.toUpperCase();
      let recents = getRecentSearches().filter(t => t.toUpperCase() !== clean);
      recents.unshift(clean);
      recents = recents.slice(0, 8);
      localStorage.setItem(RECENT_KEY, JSON.stringify(recents));
      renderRecentPills();
    } catch (e) {
      console.warn("Storage write error:", e);
    }
  }

  function renderRecentPills() {
    const container = document.getElementById("recent-pills");
    if (!container) return;
    container.innerHTML = "";
    const recents = getRecentSearches();
    recents.forEach(t => {
      const btn = document.createElement("button");
      btn.className = "pill-ticker-btn recent";
      btn.setAttribute("data-ticker", t);
      btn.textContent = t;
      btn.addEventListener("click", () => {
        tickerInput.value = t;
        runAnalysis(t);
      });
      container.appendChild(btn);
    });
  }

  // Setup Watchlist Pills
  document.querySelectorAll("#trending-pills .pill-ticker-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const t = btn.getAttribute("data-ticker");
      if (t) {
        tickerInput.value = t;
        runAnalysis(t);
      }
    });
  });

  // --- In-Terminal SEC Document Reader Modal ---
  const secModal = document.getElementById("sec-modal");
  const modalFormBadge = document.getElementById("modal-form-badge");
  const modalDocTitle = document.getElementById("modal-doc-title");
  const modalDocAcc = document.getElementById("modal-doc-acc");
  const modalSecExtLink = document.getElementById("modal-sec-ext-link");
  const modalCloseBtn = document.getElementById("modal-close-btn");
  const modalFilterInput = document.getElementById("modal-filter-input");
  const modalStatusText = document.getElementById("modal-status-text");
  const modalContentPre = document.getElementById("modal-content-pre");
  const modalLoadingIndicator = document.getElementById("modal-loading-indicator");

  let modalFullContent = "";

  function openSecModal(url, formType, docTitle, accession) {
    if (!secModal) return;
    secModal.classList.remove("hidden");
    if (modalFormBadge) modalFormBadge.textContent = formType || "SEC FILING";
    if (modalDocTitle) modalDocTitle.textContent = docTitle || "SEC Official Document";
    if (modalDocAcc) modalDocAcc.textContent = accession ? `ACC: ${accession}` : "";
    if (modalSecExtLink) modalSecExtLink.href = url || "#";
    if (modalStatusText) modalStatusText.textContent = "Connecting to SEC archive...";
    if (modalContentPre) modalContentPre.textContent = "";
    if (modalLoadingIndicator) modalLoadingIndicator.classList.remove("hidden");
    if (modalFilterInput) modalFilterInput.value = "";

    fetch(`/api/sec-doc?url=${encodeURIComponent(url)}`)
      .then(res => res.json())
      .then(data => {
        if (modalLoadingIndicator) modalLoadingIndicator.classList.add("hidden");
        modalFullContent = data.content || "Empty document received.";
        renderModalContent(modalFullContent);
        if (modalStatusText) {
          modalStatusText.textContent = `Retrieved ${Math.round((data.length || 0) / 1024)} KB ${data.truncated ? '(Preview Truncated)' : ''}`;
        }
      })
      .catch(err => {
        if (modalLoadingIndicator) modalLoadingIndicator.classList.add("hidden");
        if (modalContentPre) modalContentPre.textContent = `Failed to stream document: ${err.message}\n\nPlease click "OPEN ON SEC.GOV ↗" to view directly.`;
        if (modalStatusText) modalStatusText.textContent = "Error";
      });
  }

  function closeSecModal() {
    if (secModal) secModal.classList.add("hidden");
  }

  function renderModalContent(text) {
    if (!modalContentPre) return;
    // Strip heavy inline script/style tags if raw HTML
    let cleaned = text
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, "")
      .replace(/<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>/gi, "")
      .replace(/<br\s*[\/]?>/gi, "\n")
      .replace(/<\/p>/gi, "\n\n")
      .replace(/<\/div>/gi, "\n")
      .replace(/<\/tr>/gi, "\n")
      .replace(/<td[^>]*>/gi, "  ")
      .replace(/<[^>]+>/g, " ")
      .replace(/&nbsp;/g, " ")
      .replace(/&amp;/g, "&")
      .replace(/&lt;/g, "<")
      .replace(/&gt;/g, ">")
      .replace(/[ \t]+/g, " ")
      .replace(/\n\s*\n\s*\n/g, "\n\n")
      .trim();

    modalContentPre.textContent = cleaned || text;
  }

  if (modalCloseBtn) modalCloseBtn.addEventListener("click", closeSecModal);
  if (secModal) {
    secModal.addEventListener("click", (e) => {
      if (e.target === secModal) closeSecModal();
    });
  }

  if (modalFilterInput) {
    modalFilterInput.addEventListener("input", () => {
      const q = modalFilterInput.value.toLowerCase().trim();
      if (!q) {
        renderModalContent(modalFullContent);
        return;
      }
      const lines = (modalContentPre.textContent || modalFullContent).split("\n");
      const matched = lines.filter(l => l.toLowerCase().includes(q));
      modalContentPre.textContent = matched.length > 0
        ? `--- MATCHED ${matched.length} LINES FOR QUERY "${q.toUpperCase()}" ---\n\n` + matched.join("\n")
        : `--- ZERO OCCURRENCES FOUND FOR "${q.toUpperCase()}" IN THIS DOCUMENT ---`;
    });
  }

  // --- Institutional Omnibar Command Palette ---
  async function loadCommandPaletteCatalog() {
    try {
      const resp = await fetch("/api/commands");
      if (!resp.ok) return;
      const data = await resp.json();
      const tabs = (data.tabs || []).map(t => ({
        type: "tab",
        id: t.id,
        title: t.title,
        category: "FORENSIC NAVIGATION",
        badge: "JUMP"
      }));
      const actions = (data.actions || []).map(a => ({
        type: "action",
        id: a.id,
        title: a.title,
        category: "WORKFLOW ACTION",
        badge: a.shortcut ? `[${a.shortcut}]` : "EXEC"
      }));

      const topTickers = [
        { ticker: "NVDA", name: "NVIDIA Corp (Semiconductors)" },
        { ticker: "AAPL", name: "Apple Inc (Consumer Hardware & Services)" },
        { ticker: "MSFT", name: "Microsoft Corp (Cloud & Enterprise Software)" },
        { ticker: "TSLA", name: "Tesla Inc (Electric Vehicles & Autonomous)" },
        { ticker: "AMD", name: "Advanced Micro Devices (Computing & AI)" },
        { ticker: "PLTR", name: "Palantir Technologies (Intelligence AI Platforms)" },
        { ticker: "MSTR", name: "MicroStrategy (Bitcoin Treasury Reserve)" },
        { ticker: "SMCI", name: "Super Micro Computer (AI Server Infrastructure)" },
        { ticker: "AMZN", name: "Amazon.com Inc (E-Commerce & AWS)" },
        { ticker: "GOOGL", name: "Alphabet Inc (Search & Cloud AI)" },
        { ticker: "META", name: "Meta Platforms (Social Ecosystem & AI)" }
      ].map(c => ({
        type: "ticker",
        id: c.ticker,
        title: `Analyze ${c.ticker} — ${c.name}`,
        category: "SECURITY DIRECTORY",
        badge: c.ticker
      }));

      cmdPaletteItems = [...tabs, ...actions, ...topTickers];
    } catch (err) {
      console.warn("Command palette catalog load error:", err);
    }
  }

  function openCommandPalette() {
    if (!cmdPalette) return;
    cmdPalette.classList.remove("hidden");
    if (cmdPaletteInput) {
      cmdPaletteInput.value = "";
      cmdPaletteInput.focus();
    }
    renderCommandPaletteResults("");
  }

  function closeCommandPalette() {
    if (!cmdPalette) return;
    cmdPalette.classList.add("hidden");
  }

  function toggleCommandPalette() {
    if (!cmdPalette) return;
    if (cmdPalette.classList.contains("hidden")) {
      openCommandPalette();
    } else {
      closeCommandPalette();
    }
  }

  function renderCommandPaletteResults(query) {
    if (!cmdPaletteResults) return;
    cmdPaletteResults.innerHTML = "";
    selectedCmdIndex = -1;

    const q = (query || "").trim().toLowerCase();
    const filtered = cmdPaletteItems.filter(item => {
      if (!q) return true;
      return item.title.toLowerCase().includes(q) ||
             item.category.toLowerCase().includes(q) ||
             (item.id && item.id.toLowerCase().includes(q));
    });

    if (filtered.length === 0) {
      // If user typed a potential ticker not in top list
      if (q && q.length <= 6 && !q.includes(" ")) {
        const customTicker = q.toUpperCase();
        cmdPaletteResults.innerHTML = `
          <div class="cmd-item selected" data-type="ticker" data-id="${customTicker}">
            <div class="cmd-item-left">
              <span class="cmd-item-cat">SECURITY DIRECTORY</span>
              <span class="cmd-item-title">Interrogate SEC EDGAR archives for <strong>${customTicker}</strong></span>
            </div>
            <span class="cmd-item-badge">${customTicker}</span>
          </div>
        `;
        selectedCmdIndex = 0;
        bindCmdItemClicks();
        return;
      }
      cmdPaletteResults.innerHTML = `<div class="cmd-empty">No matching commands or tickers found for "${query}"</div>`;
      return;
    }

    filtered.slice(0, 16).forEach((item, idx) => {
      const div = document.createElement("div");
      div.className = `cmd-item ${idx === 0 ? 'selected' : ''}`;
      div.setAttribute("data-type", item.type);
      div.setAttribute("data-id", item.id);
      div.innerHTML = `
        <div class="cmd-item-left">
          <span class="cmd-item-cat">${item.category}</span>
          <span class="cmd-item-title">${item.title}</span>
        </div>
        <span class="cmd-item-badge">${item.badge || ''}</span>
      `;
      cmdPaletteResults.appendChild(div);
    });

    if (filtered.length > 0) selectedCmdIndex = 0;
    bindCmdItemClicks();
  }

  function bindCmdItemClicks() {
    if (!cmdPaletteResults) return;
    cmdPaletteResults.querySelectorAll(".cmd-item").forEach((el, idx) => {
      el.addEventListener("mouseenter", () => {
        selectedCmdIndex = idx;
        updateCmdSelection();
      });
      el.addEventListener("click", () => {
        executeCommandItem(el);
      });
    });
  }

  function updateCmdSelection() {
    if (!cmdPaletteResults) return;
    const items = cmdPaletteResults.querySelectorAll(".cmd-item");
    items.forEach((item, idx) => {
      if (idx === selectedCmdIndex) {
        item.classList.add("selected");
        item.scrollIntoView({ block: "nearest" });
      } else {
        item.classList.remove("selected");
      }
    });
  }

  function executeCommandItem(el) {
    if (!el) return;
    const type = el.getAttribute("data-type");
    const id = el.getAttribute("data-id");
    closeCommandPalette();

    if (type === "tab") {
      const targetBtn = document.querySelector(`.tab-btn[data-tab="${id}"]`);
      if (targetBtn) targetBtn.click();
    } else if (type === "ticker") {
      tickerInput.value = id;
      runAnalysis(id);
    } else if (type === "action") {
      if (id === "copy_brief") btnCopyBrief.click();
      else if (id === "print_pdf") { if (btnPrintReport) btnPrintReport.click(); }
      else if (id === "export_dossier") btnExportDossier.click();
      else if (id === "export_csv") btnExportCsv.click();
      else if (id === "export_json") btnExportJson.click();
      else if (id === "toggle_chart") toggleChartMode();
    }
  }

  if (btnOpenCmd) {
    btnOpenCmd.addEventListener("click", openCommandPalette);
  }

  if (cmdPalette) {
    cmdPalette.addEventListener("click", (e) => {
      if (e.target === cmdPalette) closeCommandPalette();
    });
  }

  if (cmdPaletteInput) {
    cmdPaletteInput.addEventListener("input", () => {
      renderCommandPaletteResults(cmdPaletteInput.value);
    });

    cmdPaletteInput.addEventListener("keydown", (e) => {
      const items = cmdPaletteResults ? cmdPaletteResults.querySelectorAll(".cmd-item") : [];
      if (items.length === 0) return;

      if (e.key === "ArrowDown") {
        e.preventDefault();
        selectedCmdIndex = (selectedCmdIndex + 1) % items.length;
        updateCmdSelection();
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        selectedCmdIndex = (selectedCmdIndex - 1 + items.length) % items.length;
        updateCmdSelection();
      } else if (e.key === "Enter") {
        e.preventDefault();
        if (selectedCmdIndex >= 0 && items[selectedCmdIndex]) {
          executeCommandItem(items[selectedCmdIndex]);
        }
      }
    });
  }

  // --- Metric Deep-Dive Formula Inspector Modal ---
  async function openMetricInspector(metricId, curVal, curStatus, customTitle) {
    if (!metricInspectorModal) return;
    metricInspectorModal.classList.remove("hidden");

    if (inspBadge) inspBadge.textContent = "ACADEMIC FORENSICS";
    if (inspTitle) inspTitle.textContent = customTitle || "Metric Deep-Dive";
    if (inspCitation) inspCitation.textContent = "Querying Methodology Library...";
    if (inspFormula) inspFormula.textContent = "Loading mathematical derivation...";
    if (inspVal) inspVal.textContent = curVal !== undefined && curVal !== null ? String(curVal) : "--";
    if (inspBenchmark) inspBenchmark.textContent = "Loading benchmarks...";
    if (inspStatus) inspStatus.textContent = curStatus || "SURFACED";
    if (inspDesc) inspDesc.textContent = "Loading economic rationale...";
    if (inspCase) inspCase.textContent = "Loading fraud case studies...";

    try {
      const resp = await fetch(`/api/methodology/${encodeURIComponent(metricId)}`);
      if (!resp.ok) throw new Error("Methodology unavailable");
      const meta = await resp.json();

      if (inspTitle && !customTitle) inspTitle.textContent = meta.name || metricId;
      if (inspCitation) inspCitation.textContent = meta.author || "Peer-Reviewed Accounting Literature";
      if (inspFormula) inspFormula.textContent = meta.formula || "Mathematical derivation unavailable";
      if (inspBenchmark) inspBenchmark.textContent = meta.benchmark || "--";
      if (inspDesc) inspDesc.textContent = meta.importance || "--";
      if (inspCase) inspCase.textContent = meta.case_study || "No historical precedent logged.";
    } catch (err) {
      if (inspCitation) inspCitation.textContent = "VETTR Quantitative Forensics Engine";
      if (inspDesc) inspDesc.textContent = `Telemetry details for ${metricId}.`;
    }
  }

  function closeMetricInspector() {
    if (metricInspectorModal) metricInspectorModal.classList.add("hidden");
  }

  if (inspCloseBtn) inspCloseBtn.addEventListener("click", closeMetricInspector);
  if (metricInspectorModal) {
    metricInspectorModal.addEventListener("click", (e) => {
      if (e.target === metricInspectorModal) closeMetricInspector();
    });
  }

  // --- URL Hash Synchronization ---
  function updateUrlHash(ticker, tabId) {
    const t = (ticker || currentTicker || "NVDA").toUpperCase();
    const activeTab = tabId || (document.querySelector(".tab-btn.active") ? document.querySelector(".tab-btn.active").getAttribute("data-tab") : "tab-models");
    const targetHash = `#${t}/${activeTab}`;
    if (window.location.hash !== targetHash) {
      try {
        history.replaceState(null, "", targetHash);
      } catch (e) {
        window.location.hash = targetHash;
      }
    }
  }

  loadCommandPaletteCatalog();

  // --- Interactive Financial OHLCV Trajectory & Volume Chart ---
  let currentChartPeriod = "6mo";
  let isCandleMode = false;
  let currentCandles = [];

  const chartTfBtns = document.querySelectorAll(".chart-tf-btn");
  const chartToggleBtn = document.getElementById("chart-toggle-btn");
  const chartContainer = document.getElementById("chart-container");
  const chartGridLayer = document.getElementById("chart-grid-layer");
  const chartVolumeLayer = document.getElementById("chart-volume-layer");
  const chartAreaPath = document.getElementById("chart-area-path");
  const chartLinePath = document.getElementById("chart-line-path");
  const chartCandlesLayer = document.getElementById("chart-candles-layer");
  const chartCrosshairLayer = document.getElementById("chart-crosshair-layer");
  const crosshairV = document.getElementById("crosshair-v");
  const crosshairDot = document.getElementById("crosshair-dot");
  const chartTooltip = document.getElementById("chart-tooltip");
  const chartRangeStats = document.getElementById("chart-range-stats");

  chartTfBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      chartTfBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentChartPeriod = btn.getAttribute("data-period");
      loadChartData(currentTicker, currentChartPeriod);
    });
  });

  if (chartToggleBtn) {
    chartToggleBtn.addEventListener("click", toggleChartMode);
  }

  function toggleChartMode() {
    isCandleMode = !isCandleMode;
    if (chartToggleBtn) {
      chartToggleBtn.querySelector("span").textContent = isCandleMode ? "AREA LINE" : "CANDLES";
    }
    renderSvgChart(currentCandles);
  }

  async function loadChartData(ticker, period) {
    try {
      const resp = await fetch(`/api/chart/${encodeURIComponent(ticker)}?period=${period}`);
      if (!resp.ok) return;
      const data = await resp.json();
      currentCandles = data.candles || [];
      renderSvgChart(currentCandles);
    } catch (err) {
      console.warn("Chart fetch error:", err);
    }
  }

  function renderSvgChart(candles) {
    if (!chartContainer || !chartGridLayer || !chartVolumeLayer) return;

    if (!candles || candles.length === 0) {
      if (chartAreaPath) chartAreaPath.setAttribute("d", "");
      if (chartLinePath) chartLinePath.setAttribute("d", "");
      if (chartRangeStats) chartRangeStats.textContent = "HISTORICAL QUOTES UNAVAILABLE";
      return;
    }

    const W = 1000;
    const padX = 24;
    const chartW = W - padX * 2;
    const priceTop = 15;
    const priceBottom = 175;
    const priceH = priceBottom - priceTop;
    const volBottom = 236;
    const volMaxH = 46;

    let minPrice = Infinity;
    let maxPrice = -Infinity;
    let maxVol = 0;

    candles.forEach(c => {
      if (c.low < minPrice) minPrice = c.low;
      if (c.high > maxPrice) maxPrice = c.high;
      if (c.volume > maxVol) maxVol = c.volume;
    });

    const padPrice = (maxPrice - minPrice) * 0.04 || 1;
    minPrice = Math.max(0, minPrice - padPrice);
    maxPrice = maxPrice + padPrice;
    const priceDelta = maxPrice - minPrice || 1;
    if (maxVol === 0) maxVol = 1;

    // Header stats
    const firstC = candles[0].close;
    const lastC = candles[candles.length - 1].close;
    const totalChgPct = ((lastC - firstC) / firstC) * 100;
    const isOverallPos = totalChgPct >= 0;

    if (chartRangeStats) {
      chartRangeStats.textContent = `Period: $${minPrice.toFixed(2)} - $${maxPrice.toFixed(2)} | Change: ${isOverallPos ? '+' : ''}${totalChgPct.toFixed(2)}%`;
      chartRangeStats.style.color = isOverallPos ? "var(--color-green)" : "var(--color-red)";
    }

    // Grid lines & labels
    chartGridLayer.innerHTML = "";
    for (let i = 0; i < 4; i++) {
      const y = priceTop + (i / 3) * priceH;
      const pVal = maxPrice - (i / 3) * priceDelta;
      
      const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
      line.setAttribute("x1", "0");
      line.setAttribute("y1", y.toFixed(1));
      line.setAttribute("x2", W.toString());
      line.setAttribute("y2", y.toFixed(1));
      chartGridLayer.appendChild(line);

      const txt = document.createElementNS("http://www.w3.org/2000/svg", "text");
      txt.setAttribute("x", (W - 8).toString());
      txt.setAttribute("y", (y - 3).toFixed(1));
      txt.setAttribute("text-anchor", "end");
      txt.setAttribute("fill", "#64748B");
      txt.setAttribute("font-size", "10");
      txt.setAttribute("class", "chart-price-label num");
      txt.textContent = `$${pVal.toFixed(2)}`;
      chartGridLayer.appendChild(txt);
    }

    // Volume Layer & Candle/Line coords
    chartVolumeLayer.innerHTML = "";
    chartCandlesLayer.innerHTML = "";

    const N = candles.length;
    let lineD = "";
    let areaD = "";

    candles.forEach((c, i) => {
      const x = padX + (i / Math.max(1, N - 1)) * chartW;
      const closeY = priceTop + (1 - (c.close - minPrice) / priceDelta) * priceH;
      const openY = priceTop + (1 - (c.open - minPrice) / priceDelta) * priceH;
      const highY = priceTop + (1 - (c.high - minPrice) / priceDelta) * priceH;
      const lowY = priceTop + (1 - (c.low - minPrice) / priceDelta) * priceH;
      const isUp = c.close >= c.open;
      const color = isUp ? "#10B981" : "#F43F5E";

      // Volume bar
      const volH = Math.max(2, (c.volume / maxVol) * volMaxH);
      const volY = volBottom - volH;
      const volRect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
      const barW = Math.max(1.5, (chartW / N) * 0.7);
      volRect.setAttribute("x", (x - barW / 2).toFixed(1));
      volRect.setAttribute("y", volY.toFixed(1));
      volRect.setAttribute("width", barW.toFixed(1));
      volRect.setAttribute("height", volH.toFixed(1));
      volRect.setAttribute("fill", color);
      volRect.setAttribute("opacity", "0.4");
      chartVolumeLayer.appendChild(volRect);

      // Line / Area path commands
      if (i === 0) {
        lineD = `M ${x.toFixed(1)} ${closeY.toFixed(1)}`;
        areaD = `M ${x.toFixed(1)} ${priceBottom} L ${x.toFixed(1)} ${closeY.toFixed(1)}`;
      } else {
        lineD += ` L ${x.toFixed(1)} ${closeY.toFixed(1)}`;
        areaD += ` L ${x.toFixed(1)} ${closeY.toFixed(1)}`;
      }

      // Candle shapes
      if (isCandleMode) {
        const wick = document.createElementNS("http://www.w3.org/2000/svg", "line");
        wick.setAttribute("x1", x.toFixed(1));
        wick.setAttribute("y1", highY.toFixed(1));
        wick.setAttribute("x2", x.toFixed(1));
        wick.setAttribute("y2", lowY.toFixed(1));
        wick.setAttribute("stroke", color);
        wick.setAttribute("stroke-width", "1");
        chartCandlesLayer.appendChild(wick);

        const bodyY = Math.min(openY, closeY);
        const bodyH = Math.max(2, Math.abs(closeY - openY));
        const bodyW = Math.max(3, (chartW / N) * 0.75);
        const body = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        body.setAttribute("x", (x - bodyW / 2).toFixed(1));
        body.setAttribute("y", bodyY.toFixed(1));
        body.setAttribute("width", bodyW.toFixed(1));
        body.setAttribute("height", bodyH.toFixed(1));
        body.setAttribute("fill", color);
        chartCandlesLayer.appendChild(body);
      }
    });

    if (N > 0) {
      const lastX = padX + chartW;
      areaD += ` L ${lastX.toFixed(1)} ${priceBottom} Z`;
    }

    if (isCandleMode) {
      chartAreaPath.setAttribute("d", "");
      chartLinePath.setAttribute("d", "");
      chartCandlesLayer.style.display = "block";
    } else {
      chartCandlesLayer.style.display = "none";
      chartAreaPath.setAttribute("d", areaD);
      chartLinePath.setAttribute("d", lineD);
      chartAreaPath.setAttribute("fill", isOverallPos ? "url(#chartAreaGrad)" : "url(#chartAreaGradNeg)");
      chartLinePath.setAttribute("stroke", isOverallPos ? "#38BDF8" : "#F43F5E");
    }
  }

  // Crosshair & Tooltip Interactive Hover
  if (chartContainer) {
    chartContainer.addEventListener("mousemove", (e) => {
      if (!currentCandles || currentCandles.length === 0) return;
      const rect = chartContainer.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const normX = (mouseX / rect.width) * 1000;

      const padX = 24;
      const chartW = 1000 - padX * 2;
      const N = currentCandles.length;

      let idx = Math.round(((normX - padX) / chartW) * (N - 1));
      if (idx < 0) idx = 0;
      if (idx >= N) idx = N - 1;

      const c = currentCandles[idx];
      const prevC = idx > 0 ? currentCandles[idx - 1] : c;
      const dChg = c.close - prevC.close;
      const dChgPct = prevC.close > 0 ? (dChg / prevC.close) * 100 : 0;
      const isPos = dChg >= 0;

      // Position crosshair
      const x = padX + (idx / Math.max(1, N - 1)) * chartW;
      let minP = Infinity, maxP = -Infinity;
      currentCandles.forEach(cd => {
        if (cd.low < minP) minP = cd.low;
        if (cd.high > maxP) maxP = cd.high;
      });
      const padP = (maxP - minP) * 0.04 || 1;
      minP = Math.max(0, minP - padP);
      maxP += padP;
      const pDelta = maxP - minP || 1;
      const closeY = 15 + (1 - (c.close - minP) / pDelta) * 160;

      if (crosshairV) {
        crosshairV.setAttribute("x1", x.toFixed(1));
        crosshairV.setAttribute("x2", x.toFixed(1));
      }
      if (crosshairDot) {
        crosshairDot.setAttribute("cx", x.toFixed(1));
        crosshairDot.setAttribute("cy", closeY.toFixed(1));
        crosshairDot.setAttribute("stroke", isPos ? "#10B981" : "#F43F5E");
      }
      if (chartCrosshairLayer) chartCrosshairLayer.style.display = "block";

      // Fill tooltip
      const ttDate = document.getElementById("tt-date");
      const ttClose = document.getElementById("tt-close");
      const ttChg = document.getElementById("tt-chg");
      const ttOpen = document.getElementById("tt-open");
      const ttHigh = document.getElementById("tt-high");
      const ttLow = document.getElementById("tt-low");
      const ttVol = document.getElementById("tt-vol");

      if (ttDate) ttDate.textContent = c.date;
      if (ttClose) ttClose.textContent = `$${c.close.toFixed(2)}`;
      if (ttChg) {
        ttChg.textContent = `${isPos ? '+' : ''}${dChgPct.toFixed(2)}%`;
        ttChg.style.color = isPos ? "var(--color-green)" : "var(--color-red)";
      }
      if (ttOpen) ttOpen.textContent = `$${c.open.toFixed(2)}`;
      if (ttHigh) ttHigh.textContent = `$${c.high.toFixed(2)}`;
      if (ttLow) ttLow.textContent = `$${c.low.toFixed(2)}`;
      if (ttVol) ttVol.textContent = c.volume.toLocaleString();

      if (chartTooltip) {
        chartTooltip.classList.remove("hidden");
        const ttW = chartTooltip.offsetWidth || 280;
        let leftPx = mouseX + 16;
        if (leftPx + ttW > rect.width) {
          leftPx = mouseX - ttW - 16;
        }
        chartTooltip.style.left = `${Math.max(12, leftPx)}px`;
      }
    });

    chartContainer.addEventListener("mouseleave", () => {
      if (chartCrosshairLayer) chartCrosshairLayer.style.display = "none";
      if (chartTooltip) chartTooltip.classList.add("hidden");
    });
  }

  // Core Analysis Runner
  async function runAnalysis(ticker) {
    currentTicker = ticker.toUpperCase();
    saveRecentSearch(currentTicker);
    updateUrlHash(currentTicker);
    loadChartData(currentTicker, currentChartPeriod);
    loadingCurtain.classList.remove("hidden");
    try {
      const resp = await fetch(`/api/analyze/${currentTicker}`);
      if (!resp.ok) {
        throw new Error(`Failed to load report for ${currentTicker}`);
      }
      currentReportData = await resp.json();
      renderDashboard(currentReportData);
    } catch (err) {
      alert(`VETTR Engine Error: ${err.message}`);
    } finally {
      loadingCurtain.classList.add("hidden");
    }
  }

  function renderDashboard(data) {
    const mkt = data.market_data || {};
    const forensics = data.forensics || {};
    const riskScore = data.risk_score || 0;
    const valModel = data.valuation_model || {};
    const gm = data.growth_metrics || {};

    // 1. Primary HUD Strip
    document.getElementById("hud-ticker").textContent = data.ticker || "UNKNOWN";
    document.getElementById("hud-name").textContent = mkt.name || data.ticker;
    document.getElementById("hud-cik").textContent = `CIK: ${data.cik || 'N/A'}`;
    document.getElementById("hud-sector").textContent = mkt.sector || 'N/A';
    document.getElementById("hud-industry").textContent = mkt.industry || 'N/A';

    document.getElementById("hud-price").textContent = `$${(mkt.current_price || 0).toFixed(2)}`;
    const chgEl = document.getElementById("hud-change");
    const chg = mkt.change_pct || 0;
    chgEl.textContent = `${chg >= 0 ? '+' : ''}${chg.toFixed(2)}%`;
    chgEl.className = `delta-badge ${chg >= 0 ? 'positive' : 'negative'}`;

    document.getElementById("hud-mcap").textContent = formatMoney(mkt.market_cap);
    document.getElementById("hud-pe").textContent = mkt.trailing_pe ? mkt.trailing_pe.toFixed(1) : "N/A";
    const low = mkt.fifty_two_week_low ? `$${mkt.fifty_two_week_low.toFixed(1)}` : "";
    const high = mkt.fifty_two_week_high ? `$${mkt.fifty_two_week_high.toFixed(1)}` : "";
    document.getElementById("hud-52w").textContent = (low && high) ? `${low} - ${high}` : "N/A";

    // Risk Meter
    const riskBadge = document.getElementById("risk-score-badge");
    const riskFill = document.getElementById("risk-bar-fill");
    const riskVerdict = document.getElementById("risk-verdict");

    riskBadge.textContent = `${riskScore} / 100`;
    riskFill.style.width = `${riskScore}%`;

    let riskClass = "low";
    let verdictText = "AUDITED / STABLE ACCOUNTING";
    if (riskScore >= 60) {
      riskClass = "high";
      verdictText = "CRITICAL / FORENSIC RED FLAGS SURFACED";
    } else if (riskScore >= 30) {
      riskClass = "medium";
      verdictText = "MODERATE SCRUTINY & ACCOUNTING FRICTION";
    }

    riskBadge.className = `risk-value ${riskClass}`;
    riskFill.className = `risk-bar-fill ${riskClass}`;
    riskVerdict.textContent = verdictText;

    // Secondary Quick Metrics Strip
    const revCagrEl = document.getElementById("hud-rev-cagr");
    const niCagrEl = document.getElementById("hud-ni-cagr");
    const cashConvEl = document.getElementById("hud-cash-conv");
    const roicEl = document.getElementById("hud-roic");
    const sloanEl = document.getElementById("hud-sloan");
    const dsoEl = document.getElementById("hud-dso");

    if (revCagrEl) revCagrEl.textContent = gm.cagr_revenue_3yr !== null && gm.cagr_revenue_3yr !== undefined ? `${gm.cagr_revenue_3yr >= 0 ? '+' : ''}${gm.cagr_revenue_3yr}%` : "N/A";
    if (niCagrEl) niCagrEl.textContent = gm.cagr_net_income_3yr !== null && gm.cagr_net_income_3yr !== undefined ? `${gm.cagr_net_income_3yr >= 0 ? '+' : ''}${gm.cagr_net_income_3yr}%` : "N/A";
    if (cashConvEl) cashConvEl.textContent = gm.cash_conversion_pct !== null && gm.cash_conversion_pct !== undefined ? `${gm.cash_conversion_pct}%` : "N/A";
    if (roicEl) roicEl.textContent = gm.roic_pct !== null && gm.roic_pct !== undefined ? `${gm.roic_pct}%` : "N/A";
    if (sloanEl) {
      const sVal = gm.sloan_accrual_pct;
      sloanEl.textContent = sVal !== null && sVal !== undefined ? `${sVal >= 0 ? '+' : ''}${sVal}%` : "N/A";
      sloanEl.style.cursor = "pointer";
      sloanEl.title = "Click to inspect Sloan Accrual formula & Sunbeam case study";
      sloanEl.onclick = () => openMetricInspector("sloan_accrual", `${sVal}%`, gm.sloan_status, "Sloan Accrual Anomaly");
    }
    if (dsoEl) dsoEl.textContent = gm.dso_days !== null && gm.dso_days !== undefined ? `${gm.dso_days} Days` : "N/A";

    // Executive Synthesis Insight
    const synthTextEl = document.getElementById("executive-synthesis-text");
    if (synthTextEl) {
      synthTextEl.textContent = data.executive_synthesis || "Verified public SEC filings. No severe regulatory or accounting red flags surfaced.";
    }

    // 2. Tab 01: Forensic Models
    // Beneish M-Score
    const b = forensics.beneish_m_score;
    const bScore = document.getElementById("beneish-score");
    const bStatus = document.getElementById("beneish-status");
    const bProbEl = document.getElementById("beneish-prob");
    const bTable = document.querySelector("#beneish-table tbody");
    bTable.innerHTML = "";

    if (b) {
      bScore.textContent = b.score;
      bScore.className = `score-num ${b.is_manipulator ? 'red' : 'green'}`;
      bStatus.textContent = b.status;
      bStatus.className = `assessment-banner ${b.is_manipulator ? 'red' : 'green'}`;

      if (bProbEl) {
        const pVal = b.manipulation_probability_pct !== undefined ? b.manipulation_probability_pct : 0.0;
        bProbEl.textContent = `${pVal}%`;
        bProbEl.className = `prob-val num ${b.is_manipulator ? 'red' : 'green'}`;
      }

      if (b.variables) {
        for (const [k, v] of Object.entries(b.variables)) {
          const tr = document.createElement("tr");
          tr.className = "clickable";
          tr.innerHTML = `
            <td>${k}</td>
            <td class="num">${v}</td>
          `;
          tr.addEventListener("click", () => {
            openMetricInspector("beneish_m", `${k} = ${v}`, b.status, `Beneish Factor: ${k}`);
          });
          bTable.appendChild(tr);
        }
      }
    } else {
      bScore.textContent = "N/A";
      bStatus.textContent = "INSUFFICIENT HISTORICAL DATA";
    }

    // Altman Z-Score
    const z = forensics.altman_z_score;
    const zScore = document.getElementById("altman-score");
    const zStatus = document.getElementById("altman-status");
    const zDoubleEl = document.getElementById("altman-z-double");
    const zTable = document.querySelector("#altman-table tbody");
    zTable.innerHTML = "";

    if (z) {
      zScore.textContent = z.score;
      const zClass = z.risk_level === 'low' ? 'green' : (z.risk_level === 'medium' ? 'yellow' : 'red');
      zScore.className = `score-num ${zClass}`;
      zStatus.textContent = z.zone;
      zStatus.className = `assessment-banner ${zClass}`;

      if (zDoubleEl) {
        zDoubleEl.textContent = z.z_double_prime !== undefined ? z.z_double_prime : "--";
        zDoubleEl.className = `prob-val num ${zClass}`;
      }

      if (z.components) {
        for (const [k, v] of Object.entries(z.components)) {
          const tr = document.createElement("tr");
          tr.className = "clickable";
          tr.innerHTML = `
            <td>${k}</td>
            <td class="num">${v}</td>
          `;
          tr.addEventListener("click", () => {
            openMetricInspector("altman_z", `${k} = ${v}`, z.zone, `Altman Factor: ${k}`);
          });
          zTable.appendChild(tr);
        }
      }
    } else {
      zScore.textContent = "N/A";
      zStatus.textContent = "N/A";
    }

    // Piotroski F-Score
    const f = forensics.piotroski_f_score;
    const fScore = document.getElementById("piotroski-score");
    const fStatus = document.getElementById("piotroski-status");
    const piRatioEl = document.getElementById("piotroski-ratio");
    const fTable = document.querySelector("#piotroski-table tbody");
    fTable.innerHTML = "";

    if (f) {
      fScore.textContent = `${f.score} / ${f.max_score}`;
      const fClass = f.score >= 7 ? 'green' : (f.score >= 5 ? 'yellow' : 'red');
      fScore.className = `score-num ${fClass}`;
      fStatus.textContent = f.rating;
      fStatus.className = `assessment-banner ${fClass}`;

      if (piRatioEl) {
        piRatioEl.textContent = `${f.score} / ${f.max_score} PASSED`;
        piRatioEl.className = `prob-val num ${fClass}`;
      }

      if (f.signals) {
        for (const [k, v] of Object.entries(f.signals)) {
          const isPass = v === 1;
          const tr = document.createElement("tr");
          tr.className = "clickable";
          tr.innerHTML = `
            <td>${k}</td>
            <td class="num" style="color: ${isPass ? 'var(--color-green)' : 'var(--color-red)'}; font-weight:700;">${isPass ? 'PASS' : 'FAIL'}</td>
          `;
          tr.addEventListener("click", () => {
            openMetricInspector("piotroski_f", isPass ? "PASSED" : "FAILED", f.rating, `Piotroski Signal: ${k}`);
          });
          fTable.appendChild(tr);
        }
      }
    } else {
      fScore.textContent = "N/A";
      fStatus.textContent = "N/A";
    }

    // Montier C-Score
    const m = forensics.montier_c_score;
    const mScoreEl = document.getElementById("montier-score");
    const mStatusEl = document.getElementById("montier-status");
    const mFlagsEl = document.getElementById("montier-flags-count");
    const mTable = document.querySelector("#montier-table tbody");
    if (mTable) mTable.innerHTML = "";

    if (m) {
      const mClass = m.score >= 4 ? 'red' : (m.score >= 2 ? 'yellow' : 'green');
      if (mScoreEl) {
        mScoreEl.textContent = `${m.score} / ${m.max_score}`;
        mScoreEl.className = `score-num ${mClass}`;
      }
      if (mStatusEl) {
        mStatusEl.textContent = m.status;
        mStatusEl.className = `assessment-banner ${mClass}`;
      }
      if (mFlagsEl) {
        mFlagsEl.textContent = `${m.score} / ${m.max_score} TRIGGERED`;
        mFlagsEl.className = `prob-val num ${mClass}`;
      }

      if (m.flag_details && mTable) {
        for (const [k, d] of Object.entries(m.flag_details)) {
          const trig = d.triggered;
          const tr = document.createElement("tr");
          tr.className = "clickable";
          tr.innerHTML = `
            <td>${d.label}</td>
            <td class="num" style="color: ${trig ? 'var(--color-red)' : 'var(--color-green)'}; font-weight:700;">
              ${trig ? 'FLAG' : 'PASS'}
            </td>
          `;
          tr.addEventListener("click", () => {
            openMetricInspector("montier_c", trig ? "FLAGGED" : "PASS", m.status, `Montier Flag: ${d.label}`);
          });
          mTable.appendChild(tr);
        }
      }
    } else if (mScoreEl) {
      mScoreEl.textContent = "N/A";
      if (mStatusEl) mStatusEl.textContent = "N/A";
    }

    // 3. Tab 02: Capital & Liquidity Matrix
    const solv = data.solvency_liquidity || forensics.solvency_liquidity || {};
    const finSeries = data.financial_series || [];
    const latestFin = finSeries.length > 0 ? finSeries[finSeries.length - 1] : {};

    const solvBadge = document.getElementById("solvency-status-badge");
    const runwayBadge = document.getElementById("runway-status-badge");

    if (solvBadge) {
      solvBadge.textContent = solv.solvency_status || "FORTRESS BALANCE SHEET";
      const sClass = solv.solvency_rating === "HIGH_RISK" ? "red" : (solv.solvency_rating === "MODERATE" ? "yellow" : "green");
      solvBadge.className = `pill-badge ${sClass}`;
    }

    if (runwayBadge) {
      runwayBadge.textContent = solv.cash_runway_status || "SELF-FUNDING";
      const isBurn = typeof solv.cash_runway_months === "number" && solv.cash_runway_months < 12;
      runwayBadge.className = `pill-badge ${isBurn ? 'red' : 'green'}`;
    }

    const solvCurrentEl = document.getElementById("solv-current-ratio");
    const solvQuickEl = document.getElementById("solv-quick-ratio");
    const solvCashEl = document.getElementById("solv-cash-ratio");
    const solvZDoubleEl = document.getElementById("solv-z-double");

    if (solvCurrentEl) solvCurrentEl.textContent = solv.current_ratio !== undefined ? `${solv.current_ratio}x` : "--";
    if (solvQuickEl) solvQuickEl.textContent = solv.quick_ratio !== undefined ? `${solv.quick_ratio}x` : "--";
    if (solvCashEl) solvCashEl.textContent = solv.cash_ratio !== undefined ? `${solv.cash_ratio}x` : "--";
    if (solvZDoubleEl) solvZDoubleEl.textContent = solv.altman_z_double_prime !== undefined ? `${solv.altman_z_double_prime}` : "--";

    const solvCashAbs = document.getElementById("solv-cash-abs");
    const solvClAbs = document.getElementById("solv-cl-abs");
    const solvNwcAbs = document.getElementById("solv-nwc-abs");

    const caVal = Number(latestFin.current_assets || (latestFin.total_assets ? latestFin.total_assets * 0.4 : 0));
    const clVal = Number(latestFin.current_liabilities || (latestFin.total_liabilities ? latestFin.total_liabilities * 0.35 : 0));

    if (solvCashAbs) solvCashAbs.textContent = formatMoney(solv.estimated_cash);
    if (solvClAbs) solvClAbs.textContent = formatMoney(clVal);
    if (solvNwcAbs) solvNwcAbs.textContent = formatMoney(caVal - clVal);

    const solvNetDebtEbitda = document.getElementById("solv-net-debt-ebitda");
    const solvInterestCov = document.getElementById("solv-interest-cov");
    const solvCccDays = document.getElementById("solv-ccc-days");
    const solvRunwayMonths = document.getElementById("solv-runway-months");

    if (solvNetDebtEbitda) solvNetDebtEbitda.textContent = solv.net_debt_to_ebitda !== undefined ? `${solv.net_debt_to_ebitda}x` : "--";
    if (solvInterestCov) solvInterestCov.textContent = solv.interest_coverage_ratio !== undefined ? `${solv.interest_coverage_ratio}x` : "--";
    if (solvCccDays) solvCccDays.textContent = solv.cash_conversion_cycle_days !== undefined ? `${solv.cash_conversion_cycle_days} Days` : "--";
    if (solvRunwayMonths) solvRunwayMonths.textContent = solv.cash_runway_months === "INF" ? "Self-Funding" : (solv.cash_runway_months !== undefined ? `${solv.cash_runway_months} Mos` : "--");

    const solvDebtAbs = document.getElementById("solv-debt-abs");
    const solvNetDebtAbs = document.getElementById("solv-net-debt-abs");
    const solvDpoDays = document.getElementById("solv-dpo-days");
    const solvFcfAbs = document.getElementById("solv-fcf-abs");

    if (solvDebtAbs) solvDebtAbs.textContent = formatMoney(solv.total_debt);
    if (solvNetDebtAbs) solvNetDebtAbs.textContent = formatMoney(solv.net_debt);
    if (solvDpoDays) solvDpoDays.textContent = solv.dpo_days !== undefined ? `${solv.dpo_days} Days` : "--";
    if (solvFcfAbs) solvFcfAbs.textContent = formatMoney(solv.fcf_estimate);

    document.querySelectorAll(".solv-stat-card").forEach(card => {
      card.style.cursor = "pointer";
      card.onclick = () => {
        const label = card.querySelector(".solv-label") ? card.querySelector(".solv-label").textContent : "Capital Solvency";
        const val = card.querySelector(".solv-val") ? card.querySelector(".solv-val").textContent : "";
        openMetricInspector("altman_z", val, solv.solvency_status, `Solvency & Liquidity: ${label}`);
      };
    });

    // 4. Tab 03: Anomalies
    const anoContainer = document.getElementById("anomalies-container");
    const anoPill = document.getElementById("anomaly-count-pill");
    const anomalies = forensics.anomalies || [];
    anoPill.textContent = `${anomalies.length} FLAGGED`;
    anoPill.className = `pill-badge ${anomalies.length > 0 ? 'red' : 'green'}`;
    anoContainer.innerHTML = "";

    if (anomalies.length === 0) {
      anoContainer.innerHTML = `
        <div style="color: var(--color-green); font-size: 12px; padding: 14px; border: 1px solid var(--color-green-border); background: var(--color-green-bg); border-radius: 4px;">
          [VERIFIED] No severe balance sheet decoupling or operating cash flow divergences detected.
        </div>
      `;
    } else {
      anomalies.forEach(a => {
        anoContainer.innerHTML += `
          <div class="anomaly-item ${a.severity}">
            <div class="anomaly-title-row">
              <span class="anomaly-name">${a.title}</span>
              <span class="anomaly-metric-callout num">${a.metric || ''}</span>
            </div>
            <div class="anomaly-text">${a.description}</div>
          </div>
        `;
      });
    }

    // Regulatory Triggers
    const regContainer = document.getElementById("regulatory-container");
    const regFlags = forensics.regulatory_flags || [];
    regContainer.innerHTML = "";

    if (regFlags.length === 0) {
      regContainer.innerHTML = `
        <div style="color: var(--text-muted); font-size: 12px; padding: 8px 0;">
          No critical litigation, subpoena, or restatement triggers surfaced in recent section scans.
        </div>
      `;
    } else {
      regFlags.forEach(rf => {
        regContainer.innerHTML += `
          <div class="reg-item">
            <div class="reg-tag">[SEC 10-K DISCLOSURE] ${rf.title}</div>
            <div class="reg-quote">${rf.excerpt}</div>
          </div>
        `;
      });
    }

    // Sentiment
    const s = forensics.sentiment;
    if (s) {
      document.getElementById("sent-unc-val").textContent = `${s.uncertainty_pct}%`;
      document.getElementById("sent-lit-val").textContent = `${s.litigious_pct}%`;
      document.getElementById("sent-neg-val").textContent = `${s.negative_pct}%`;
      document.getElementById("sent-pos-val").textContent = `${s.positive_pct}%`;
    }

    // 4. Tab 03: Reverse DCF Valuation & Sensitivity Matrix
    if (valModel) {
      document.getElementById("val-implied-growth").textContent = `${valModel.implied_growth_10yr_pct || '0.0'}%`;
      document.getElementById("val-fcf-est").textContent = formatMoney(valModel.fcf_estimate);
      document.getElementById("val-fcf-yield").textContent = `${valModel.fcf_yield_pct || '0.0'}%`;
      const valBadge = document.getElementById("valuation-verdict-badge");
      valBadge.textContent = valModel.valuation_verdict || "STABLE VALUATION";
      valBadge.className = `pill-badge ${(valModel.valuation_verdict || '').includes('AGGRESSIVE') ? 'red' : 'green'}`;

      updateDcfMatrix(mkt.market_cap || 0, valModel.fcf_estimate || 0);
    }

    // 5. Tab 04: 10-K Diff
    const diff = data.diff_analysis;
    const addedList = document.getElementById("diff-added-list");
    const removedList = document.getElementById("diff-removed-list");
    addedList.innerHTML = "";
    removedList.innerHTML = "";

    if (diff) {
      document.getElementById("diff-sim").textContent = `Similarity: ${diff.similarity_pct}%`;
      document.getElementById("diff-added-count").textContent = `+${diff.added_count} Added`;
      document.getElementById("diff-removed-count").textContent = `-${diff.removed_count} Struck`;

      (diff.sample_added || []).forEach(sentence => {
        addedList.innerHTML += `<div class="diff-entry add">+ ${sentence}</div>`;
      });

      (diff.sample_removed || []).forEach(sentence => {
        removedList.innerHTML += `<div class="diff-entry del">- ${sentence}</div>`;
      });
    } else {
      addedList.innerHTML = "<div style='color:var(--text-muted); padding: 10px;'>No prior 10-K text diff available.</div>";
      removedList.innerHTML = "<div style='color:var(--text-muted); padding: 10px;'>No prior 10-K text diff available.</div>";
    }

    // 6. Tab 05: DuPont ROE
    const dupontList = data.dupont_series || [];
    const dupontTbody = document.querySelector("#dupont-table tbody");
    dupontTbody.innerHTML = "";

    if (dupontList.length > 0) {
      dupontList.forEach(d => {
        dupontTbody.innerHTML += `
          <tr>
            <td><strong>FY ${d.fiscal_year}</strong></td>
            <td class="num" style="color: var(--text-main); font-weight: 700;">${d.roe_pct}%</td>
            <td class="num">${d.roa_pct}%</td>
            <td class="num">${d.net_profit_margin_pct}%</td>
            <td class="num">${d.operating_margin_pct}%</td>
            <td class="num">${d.asset_turnover}x</td>
            <td class="num">${d.equity_multiplier}x</td>
            <td style="color: ${d.quality_verdict.includes('HIGH') ? 'var(--color-green)' : (d.quality_verdict.includes('LEVERAGE') ? 'var(--color-red)' : 'var(--text-secondary)')}; font-weight: 600;">
              ${d.quality_verdict}
            </td>
          </tr>
        `;
      });
    } else {
      dupontTbody.innerHTML = "<tr><td colspan='8'>No DuPont decomposition records available.</td></tr>";
    }

    // 7. Tab 06: Form 4 Insiders
    const insider = data.insider_activity || {};
    const insiderBadge = document.getElementById("insider-sentiment-badge");
    const insiderTbody = document.querySelector("#insiders-table tbody");
    insiderTbody.innerHTML = "";

    insiderBadge.textContent = insider.sentiment || "NEUTRAL";
    const isSelling = (insider.sentiment || '').includes("SELLING");
    insiderBadge.className = `pill-badge ${isSelling ? 'red' : 'green'}`;

    const trades = insider.trades || [];
    if (trades.length > 0) {
      trades.forEach(t => {
        const isBuy = t.transaction_type === "BUY";
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td class="num">${t.transaction_date}</td>
          <td><strong>${t.owner}</strong></td>
          <td>${t.title}</td>
          <td><span class="pill-badge ${isBuy ? 'green' : 'red'}">${t.transaction_type}</span></td>
          <td class="num">${t.shares.toLocaleString()}</td>
          <td class="num">${t.price_per_share > 0 ? '$' + t.price_per_share.toFixed(2) : '-'}</td>
          <td class="num" style="color: var(--text-main); font-weight: 700;">${formatMoney(t.total_value)}</td>
          <td><button class="btn-action sec-table-btn" title="Read Form 4 inside Terminal">READ FORM 4 ↗</button></td>
        `;
        const btn = tr.querySelector(".sec-table-btn");
        if (btn) {
          btn.addEventListener("click", () => {
            openSecModal(t.filing_url, "FORM 4", `${t.owner} (${t.title || 'Insider'})`, t.transaction_date);
          });
        }
        insiderTbody.appendChild(tr);
      });
    } else {
      insiderTbody.innerHTML = "<tr><td colspan='8'>No recent Form 4 insider transactions recorded.</td></tr>";
    }

    // 8. Tab 07: 8-K Material Events
    const events8kTbody = document.querySelector("#events-8k-table tbody");
    if (events8kTbody) {
      events8kTbody.innerHTML = "";
      const filings8k = (data.filings && data.filings.recent_8k) || [];

      if (filings8k.length > 0) {
        filings8k.forEach(ev => {
          const rawItem = ev.items || "8.01";
          const isHighAlert = rawItem.includes("5.02") || rawItem.includes("4.02") || rawItem.includes("1.03");
          const isMediumAlert = rawItem.includes("4.01") || rawItem.includes("3.01") || rawItem.includes("2.04");
          const alertClass = isHighAlert ? "high-alert" : (isMediumAlert ? "medium-alert" : "");

          const tr = document.createElement("tr");
          tr.innerHTML = `
            <td class="num">${ev.filing_date}</td>
            <td class="num">${ev.report_date || ev.filing_date}</td>
            <td><span class="item-badge-8k ${alertClass}">${ev.items ? 'Item ' + ev.items : '8-K Event'}</span></td>
            <td><strong style="color: var(--text-main);">${ev.description || 'Material Definitive Disclosure'}</strong></td>
            <td class="num" style="font-size: 11px;">${ev.accession_number}</td>
            <td><button class="btn-action sec-table-btn" title="Read 8-K inside Terminal">READ 8-K ↗</button></td>
          `;
          const btn = tr.querySelector(".sec-table-btn");
          if (btn) {
            btn.addEventListener("click", () => {
              openSecModal(ev.url, "FORM 8-K", ev.description || "Material Definitive Disclosure", ev.accession_number);
            });
          }
          events8kTbody.appendChild(tr);
        });
      } else {
        events8kTbody.innerHTML = "<tr><td colspan='6'>No recent Form 8-K filings surfaced in SEC archive.</td></tr>";
      }
    }

    // 9. Tab 10: Audited Financials
    const finSeries = data.financial_series || [];
    const finTable = document.getElementById("financials-table");
    const thead = finTable.querySelector("thead tr");
    const tbody = finTable.querySelector("tbody");
    
    thead.innerHTML = "<th>GAAP Line Item (USD)</th>";
    tbody.innerHTML = "";

    if (finSeries.length > 0) {
      finSeries.forEach(item => {
        thead.innerHTML += `<th class="num">FY ${item.fiscal_year}</th>`;
      });

      const metricsToDisplay = [
        { key: "revenue", label: "Total Revenues / Sales" },
        { key: "gross_profit", label: "Gross Profit" },
        { key: "operating_income", label: "Operating Income (EBIT)" },
        { key: "net_income", label: "Net Income / Profit" },
        { key: "operating_cash_flow", label: "Operating Cash Flow (CFO)" },
        { key: "total_assets", label: "Total Assets" },
        { key: "accounts_receivable", label: "Accounts Receivable" },
        { key: "inventory", label: "Inventories" },
        { key: "total_liabilities", label: "Total Liabilities" },
        { key: "long_term_debt", label: "Long-Term Debt" }
      ];

      metricsToDisplay.forEach(m => {
        let rowHtml = `<td><strong>${m.label}</strong></td>`;
        finSeries.forEach(item => {
          const val = item[m.key];
          rowHtml += `<td class="num">${formatMoney(val)}</td>`;
        });
        tbody.innerHTML += `<tr>${rowHtml}</tr>`;
      });
    } else {
      tbody.innerHTML = "<tr><td colspan='5'>No XBRL financial statement records found.</td></tr>";
    }

    // 10. Tab 11: SEC Archive
    const filingsList = (data.filings && data.filings.all_recent) || [];
    const filingsTbody = document.querySelector("#filings-table tbody");
    filingsTbody.innerHTML = "";

    if (filingsList.length > 0) {
      filingsList.forEach(f => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td><strong>${f.form}</strong></td>
          <td class="num">${f.filing_date}</td>
          <td class="num">${f.report_date || f.filing_date}</td>
          <td class="num" style="font-size: 11px;">${f.accession_number}</td>
          <td style="color: var(--text-muted); max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${f.primary_document}</td>
          <td><button class="btn-action sec-table-btn" title="Stream & Read in Terminal">READ FILING ↗</button></td>
        `;
        const btn = tr.querySelector(".sec-table-btn");
        if (btn) {
          btn.addEventListener("click", () => {
            openSecModal(f.url, f.form, f.primary_document, f.accession_number);
          });
        }
        filingsTbody.appendChild(tr);
      });
    } else {
      filingsTbody.innerHTML = "<tr><td colspan='6'>No recent filings found.</td></tr>";
    }
  }

  // Load Peer Comparison
  async function loadComparison(tickersStr) {
    const tbody = document.querySelector("#compare-table tbody");
    tbody.innerHTML = "<tr><td colspan='11' style='text-align:center; padding: 24px; color: var(--text-muted);'>Interrogating SEC EDGAR across peer group...</td></tr>";

    try {
      const resp = await fetch(`/api/compare?tickers=${encodeURIComponent(tickersStr)}`);
      if (!resp.ok) throw new Error("Failed to load peer comparison");
      const data = await resp.json();
      const comp = data.comparison || [];
      tbody.innerHTML = "";

      comp.forEach(r => {
        const risk = r.risk_score;
        const riskColor = risk >= 60 ? "var(--color-red)" : (risk >= 30 ? "var(--color-amber)" : "var(--color-green)");
        const b = r.beneish || {};
        const z = r.altman || {};
        const pi = r.piotroski || {};
        const m = r.montier || {};
        const solv = r.solvency || {};

        const bColor = b.is_manipulator ? "var(--color-red)" : "var(--color-green)";
        const mClass = m.score >= 4 ? "var(--color-red)" : (m.score >= 2 ? "var(--color-amber)" : "var(--color-green)");
        const solvClass = solv.solvency_rating === "HIGH_RISK" ? "red" : (solv.solvency_rating === "MODERATE" ? "yellow" : "green");

        const tr = document.createElement("tr");
        tr.className = "clickable";
        tr.innerHTML = `
          <td><strong style="color: var(--text-main); font-size: 13px;">${r.ticker}</strong></td>
          <td>${r.name}</td>
          <td class="num">$${(r.price || 0).toFixed(2)}</td>
          <td class="num">${formatMoney(r.market_cap)}</td>
          <td class="num" style="color: ${riskColor}; font-weight: 700;">${risk} / 100</td>
          <td class="num" style="color: ${bColor}; font-weight: 700;">${b.score || 'N/A'}</td>
          <td class="num">${z.score || 'N/A'}</td>
          <td class="num">${pi.score ? pi.score + '/9' : 'N/A'}</td>
          <td class="num" style="color: ${mClass}; font-weight: 700;">${m.score !== undefined ? m.score + '/6' : 'N/A'}</td>
          <td><span class="pill-badge ${solvClass}">${solv.solvency_status || 'STABLE'}</span></td>
          <td class="num">${r.anomalies_count > 0 ? '<span style="color:var(--color-red); font-weight:700;">' + r.anomalies_count + ' FLAGGED</span>' : '<span style="color:var(--color-green);">CLEAN</span>'}</td>
        `;

        tr.addEventListener("click", () => {
          tickerInput.value = r.ticker;
          runAnalysis(r.ticker);
          document.querySelector('[data-tab="tab-models"]').click();
        });

        tbody.appendChild(tr);
      });
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan='11' style='color:var(--color-red);'>Comparison Error: ${err.message}</td></tr>`;
    }
  }

  // Load Batch Screener
  async function loadScreener(preset) {
    const tbody = document.querySelector("#screener-table tbody");
    tbody.innerHTML = "<tr><td colspan='9' style='text-align:center; padding: 24px; color: var(--text-muted);'>Interrogating SEC EDGAR facts across watchlist...</td></tr>";

    try {
      const resp = await fetch(`/api/screen?preset=${preset}`);
      if (!resp.ok) throw new Error("Failed to load screener");
      const data = await resp.json();
      const results = data.results || [];
      tbody.innerHTML = "";

      results.forEach((r, idx) => {
        const risk = r.risk_score;
        const riskColor = risk >= 60 ? "var(--color-red)" : (risk >= 30 ? "var(--color-amber)" : "var(--color-green)");
        const bColor = r.is_manipulator ? "var(--color-red)" : "var(--color-green)";

        const tr = document.createElement("tr");
        tr.className = "clickable";
        tr.innerHTML = `
          <td class="num">#${idx + 1}</td>
          <td><strong style="color: var(--text-main); font-size: 13px;">${r.ticker}</strong></td>
          <td>${r.name}</td>
          <td class="num">$${r.price.toFixed(2)}</td>
          <td class="num" style="color: ${riskColor}; font-weight: 700;">${risk} / 100</td>
          <td class="num" style="color: ${bColor}; font-weight: 700;">${r.beneish_score || 'N/A'}</td>
          <td class="num">${r.altman_score || 'N/A'}</td>
          <td class="num">${r.piotroski_score ? r.piotroski_score + '/9' : 'N/A'}</td>
          <td class="num">${r.anomalies_count > 0 ? '<span style="color:var(--color-red); font-weight:700;">' + r.anomalies_count + ' FLAGGED</span>' : '<span style="color:var(--color-green);">CLEAN</span>'}</td>
        `;

        tr.addEventListener("click", () => {
          tickerInput.value = r.ticker;
          runAnalysis(r.ticker);
          document.querySelector('[data-tab="tab-models"]').click();
        });

        tbody.appendChild(tr);
      });
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan='9' style='color:var(--color-red);'>Screener Error: ${err.message}</td></tr>`;
    }
  }

  // Live Exchange Telemetry Ticker Tape
  async function fetchExchangePulse() {
    const track = document.getElementById("exchange-tape-track");
    const statusBadge = document.getElementById("market-status-badge");
    if (!track) return;

    try {
      const resp = await fetch("/api/market/pulse");
      if (!resp.ok) return;
      const data = await resp.json();

      if (statusBadge && data.market_status) {
        statusBadge.textContent = data.market_status;
      }

      track.innerHTML = "";

      // 1. Render Indices
      (data.indices || []).forEach(idx => {
        const isPos = idx.change >= 0;
        const div = document.createElement("div");
        div.className = "tape-item";
        div.innerHTML = `
          <span class="tape-sym" style="color: var(--color-cyan);">${idx.symbol}</span>
          <span class="tape-price num">$${idx.price.toFixed(2)}</span>
          <span class="tape-chg num ${isPos ? 'pos' : 'neg'}">${isPos ? '+' : ''}${idx.change_pct.toFixed(2)}%</span>
          <span class="tape-sep">•</span>
        `;
        track.appendChild(div);
      });

      // 2. Render Active Leaders (Clickable to switch ticker!)
      (data.leaders || []).forEach(lead => {
        const isPos = lead.change >= 0;
        const div = document.createElement("div");
        div.className = "tape-item";
        div.title = `Click to analyze ${lead.symbol}`;
        div.innerHTML = `
          <span class="tape-sym">${lead.symbol}</span>
          <span class="tape-price num">$${lead.price.toFixed(2)}</span>
          <span class="tape-chg num ${isPos ? 'pos' : 'neg'}">${isPos ? '+' : ''}${lead.change_pct.toFixed(2)}%</span>
          <span class="tape-sep">•</span>
        `;
        div.addEventListener("click", () => {
          tickerInput.value = lead.symbol;
          runAnalysis(lead.symbol);
          window.scrollTo({ top: 0, behavior: 'smooth' });
        });
        track.appendChild(div);
      });
    } catch (err) {
      console.warn("Exchange pulse poll error:", err);
    }
  }

  // Initial fetch and continuous 15-second live exchange poll
  fetchExchangePulse();
  setInterval(fetchExchangePulse, 15000);

  // Initial load with URL Hash state synchronization
  renderRecentPills();
  const rawHash = (window.location.hash || "").replace(/^#/, "").trim();
  let startupTicker = "NVDA";
  let startupTab = null;

  if (rawHash) {
    const parts = rawHash.split("/");
    if (parts[0]) startupTicker = parts[0].toUpperCase();
    if (parts[1]) startupTab = parts[1];
  }

  tickerInput.value = startupTicker;
  runAnalysis(startupTicker).then(() => {
    if (startupTab) {
      const btn = document.querySelector(`.tab-btn[data-tab="${startupTab}"]`);
      if (btn) btn.click();
    }
  });

  window.addEventListener("hashchange", () => {
    const h = (window.location.hash || "").replace(/^#/, "").trim();
    if (!h) return;
    const parts = h.split("/");
    const t = parts[0] ? parts[0].toUpperCase() : null;
    const tabId = parts[1] || null;

    if (t && t !== currentTicker) {
      tickerInput.value = t;
      runAnalysis(t).then(() => {
        if (tabId) {
          const btn = document.querySelector(`.tab-btn[data-tab="${tabId}"]`);
          if (btn) btn.click();
        }
      });
    } else if (tabId) {
      const btn = document.querySelector(`.tab-btn[data-tab="${tabId}"]`);
      if (btn) btn.click();
    }
  });
});
