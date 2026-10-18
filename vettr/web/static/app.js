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
  const presetBtns = document.querySelectorAll(".screener-switcher .preset-btn");
  const btnRunCompare = document.getElementById("btn-run-compare");
  const compareInput = document.getElementById("compare-input");

  let currentTicker = "NVDA";
  let currentReportData = null;
  let debounceTimer = null;
  let selectedDropdownIndex = -1;

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

      if (targetId === "tab-screener") {
        const activePreset = document.querySelector(".screener-switcher .preset-btn.active");
        const preset = activePreset ? activePreset.getAttribute("data-preset") : "mega_tech";
        loadScreener(preset);
      } else if (targetId === "tab-compare") {
        loadComparison(compareInput ? compareInput.value : "NVDA, AMD, INTC");
      }
    });
  });

  // Global hotkey '/' to focus search
  document.addEventListener("keydown", (e) => {
    if (e.key === "/" && document.activeElement !== tickerInput && document.activeElement !== compareInput) {
      e.preventDefault();
      tickerInput.focus();
      tickerInput.select();
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

  // Core Analysis Runner
  async function runAnalysis(ticker) {
    currentTicker = ticker.toUpperCase();
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

    // 1. HUD Strip
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

    // 2. Tab 01: Forensic Models
    // Beneish
    const b = forensics.beneish_m_score;
    const bScore = document.getElementById("beneish-score");
    const bStatus = document.getElementById("beneish-status");
    const bTable = document.querySelector("#beneish-table tbody");
    bTable.innerHTML = "";

    if (b) {
      bScore.textContent = b.score;
      bScore.className = `score-num ${b.is_manipulator ? 'red' : 'green'}`;
      bStatus.textContent = b.status;
      bStatus.className = `assessment-banner ${b.is_manipulator ? 'red' : 'green'}`;

      if (b.variables) {
        for (const [k, v] of Object.entries(b.variables)) {
          bTable.innerHTML += `
            <tr>
              <td>${k}</td>
              <td class="num">${v}</td>
            </tr>
          `;
        }
      }
    } else {
      bScore.textContent = "N/A";
      bStatus.textContent = "INSUFFICIENT HISTORICAL DATA";
    }

    // Altman Z
    const z = forensics.altman_z_score;
    const zScore = document.getElementById("altman-score");
    const zStatus = document.getElementById("altman-status");
    const zTable = document.querySelector("#altman-table tbody");
    zTable.innerHTML = "";

    if (z) {
      zScore.textContent = z.score;
      const zClass = z.risk_level === 'low' ? 'green' : (z.risk_level === 'medium' ? 'yellow' : 'red');
      zScore.className = `score-num ${zClass}`;
      zStatus.textContent = z.zone;
      zStatus.className = `assessment-banner ${zClass}`;

      if (z.components) {
        for (const [k, v] of Object.entries(z.components)) {
          zTable.innerHTML += `
            <tr>
              <td>${k}</td>
              <td class="num">${v}</td>
            </tr>
          `;
        }
      }
    } else {
      zScore.textContent = "N/A";
      zStatus.textContent = "N/A";
    }

    // Piotroski F
    const f = forensics.piotroski_f_score;
    const fScore = document.getElementById("piotroski-score");
    const fStatus = document.getElementById("piotroski-status");
    const fTable = document.querySelector("#piotroski-table tbody");
    fTable.innerHTML = "";

    if (f) {
      fScore.textContent = `${f.score} / ${f.max_score}`;
      const fClass = f.score >= 7 ? 'green' : (f.score >= 5 ? 'yellow' : 'red');
      fScore.className = `score-num ${fClass}`;
      fStatus.textContent = f.rating;
      fStatus.className = `assessment-banner ${fClass}`;

      if (f.signals) {
        for (const [k, v] of Object.entries(f.signals)) {
          fTable.innerHTML += `
            <tr>
              <td>${k}</td>
              <td class="num" style="color: ${v === 1 ? 'var(--signal-green)' : 'var(--signal-red)'}; font-weight:700;">${v === 1 ? 'PASS' : 'FAIL'}</td>
            </tr>
          `;
        }
      }
    } else {
      fScore.textContent = "N/A";
      fStatus.textContent = "N/A";
    }

    // 3. Tab 02: Anomalies
    const anoContainer = document.getElementById("anomalies-container");
    const anoPill = document.getElementById("anomaly-count-pill");
    const anomalies = forensics.anomalies || [];
    anoPill.textContent = `${anomalies.length} FLAGGED`;
    anoPill.className = `pill-badge ${anomalies.length > 0 ? 'red' : 'green'}`;
    anoContainer.innerHTML = "";

    if (anomalies.length === 0) {
      anoContainer.innerHTML = `
        <div style="color: var(--signal-green); font-size: 12px; padding: 14px; border: 1px solid rgba(16,185,129,0.2); background: var(--signal-green-bg);">
          [VERIFIED] No severe balance sheet decoupling or operating cash flow divergences detected.
        </div>
      `;
    } else {
      anomalies.forEach(a => {
        anoContainer.innerHTML += `
          <div class="anomaly-item ${a.severity}">
            <div class="anomaly-title-row">
              <span class="anomaly-name">${a.title}</span>
              <span class="anomaly-metric-callout">${a.metric || ''}</span>
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

    // 4. Tab 03: Reverse DCF Valuation
    if (valModel) {
      document.getElementById("val-implied-growth").textContent = `${valModel.implied_growth_10yr_pct || '0.0'}%`;
      document.getElementById("val-fcf-est").textContent = formatMoney(valModel.fcf_estimate);
      document.getElementById("val-fcf-yield").textContent = `${valModel.fcf_yield_pct || '0.0'}%`;
      const valBadge = document.getElementById("valuation-verdict-badge");
      valBadge.textContent = valModel.valuation_verdict || "STABLE VALUATION";
      valBadge.className = `pill-badge ${(valModel.valuation_verdict || '').includes('AGGRESSIVE') ? 'red' : 'green'}`;
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
            <td class="num" style="color: var(--text-primary); font-weight: 700;">${d.roe_pct}%</td>
            <td class="num">${d.roa_pct}%</td>
            <td class="num">${d.net_profit_margin_pct}%</td>
            <td class="num">${d.operating_margin_pct}%</td>
            <td class="num">${d.asset_turnover}x</td>
            <td class="num">${d.equity_multiplier}x</td>
            <td style="color: ${d.quality_verdict.includes('HIGH') ? 'var(--signal-green)' : (d.quality_verdict.includes('LEVERAGE') ? 'var(--signal-red)' : 'var(--text-secondary)')}; font-weight: 600;">
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
        insiderTbody.innerHTML += `
          <tr>
            <td>${t.transaction_date}</td>
            <td><strong>${t.owner}</strong></td>
            <td>${t.title}</td>
            <td><span class="pill-badge ${isBuy ? 'green' : 'red'}">${t.transaction_type}</span></td>
            <td class="num">${t.shares.toLocaleString()}</td>
            <td class="num">${t.price_per_share > 0 ? '$' + t.price_per_share.toFixed(2) : '-'}</td>
            <td class="num" style="color: var(--text-primary); font-weight: 700;">${formatMoney(t.total_value)}</td>
            <td><a href="${t.filing_url}" target="_blank" rel="noopener noreferrer" style="color: var(--signal-cyan); text-decoration: none;">Form 4 ↗</a></td>
          </tr>
        `;
      });
    } else {
      insiderTbody.innerHTML = "<tr><td colspan='8'>No recent Form 4 insider transactions recorded.</td></tr>";
    }

    // 8. Tab 09: Audited Financials
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

    // 9. Tab 10: SEC Archive
    const filingsList = (data.filings && data.filings.all_recent) || [];
    const filingsTbody = document.querySelector("#filings-table tbody");
    filingsTbody.innerHTML = "";

    if (filingsList.length > 0) {
      filingsList.forEach(f => {
        filingsTbody.innerHTML += `
          <tr>
            <td><strong>${f.form}</strong></td>
            <td>${f.filing_date}</td>
            <td>${f.report_date || f.filing_date}</td>
            <td style="font-size: 11px;">${f.accession_number}</td>
            <td style="color: var(--text-muted); max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${f.primary_document}</td>
            <td><a href="${f.url}" target="_blank" rel="noopener noreferrer" style="color: var(--signal-cyan); text-decoration: none;">View Archive ↗</a></td>
          </tr>
        `;
      });
    } else {
      filingsTbody.innerHTML = "<tr><td colspan='6'>No recent filings found.</td></tr>";
    }
  }

  // Load Peer Comparison
  async function loadComparison(tickersStr) {
    const tbody = document.querySelector("#compare-table tbody");
    tbody.innerHTML = "<tr><td colspan='9' style='text-align:center; padding: 24px; color: var(--text-muted);'>Interrogating SEC EDGAR across peer group...</td></tr>";

    try {
      const resp = await fetch(`/api/compare?tickers=${encodeURIComponent(tickersStr)}`);
      if (!resp.ok) throw new Error("Failed to load peer comparison");
      const data = await resp.json();
      const comp = data.comparison || [];
      tbody.innerHTML = "";

      comp.forEach(r => {
        const risk = r.risk_score;
        const riskColor = risk >= 60 ? "var(--signal-red)" : (risk >= 30 ? "var(--signal-amber)" : "var(--signal-green)");
        const b = r.beneish || {};
        const z = r.altman || {};
        const pi = r.piotroski || {};
        const bColor = b.is_manipulator ? "var(--signal-red)" : "var(--signal-green)";

        const tr = document.createElement("tr");
        tr.className = "clickable";
        tr.innerHTML = `
          <td><strong style="color: var(--text-primary); font-size: 13px;">${r.ticker}</strong></td>
          <td>${r.name}</td>
          <td class="num">$${(r.price || 0).toFixed(2)}</td>
          <td class="num">${formatMoney(r.market_cap)}</td>
          <td class="num" style="color: ${riskColor}; font-weight: 700;">${risk} / 100</td>
          <td class="num" style="color: ${bColor}; font-weight: 700;">${b.score || 'N/A'}</td>
          <td class="num">${z.score || 'N/A'}</td>
          <td class="num">${pi.score ? pi.score + '/9' : 'N/A'}</td>
          <td class="num">${r.anomalies_count > 0 ? '<span style="color:var(--signal-red); font-weight:700;">' + r.anomalies_count + ' FLAGGED</span>' : '<span style="color:var(--signal-green);">CLEAN</span>'}</td>
        `;

        tr.addEventListener("click", () => {
          tickerInput.value = r.ticker;
          runAnalysis(r.ticker);
          document.querySelector('[data-tab="tab-models"]').click();
        });

        tbody.appendChild(tr);
      });
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan='9' style='color:var(--signal-red);'>Comparison Error: ${err.message}</td></tr>`;
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
        const riskColor = risk >= 60 ? "var(--signal-red)" : (risk >= 30 ? "var(--signal-amber)" : "var(--signal-green)");
        const bColor = r.is_manipulator ? "var(--signal-red)" : "var(--signal-green)";

        const tr = document.createElement("tr");
        tr.className = "clickable";
        tr.innerHTML = `
          <td>#${idx + 1}</td>
          <td><strong style="color: var(--text-primary); font-size: 13px;">${r.ticker}</strong></td>
          <td>${r.name}</td>
          <td class="num">$${r.price.toFixed(2)}</td>
          <td class="num" style="color: ${riskColor}; font-weight: 700;">${risk} / 100</td>
          <td class="num" style="color: ${bColor}; font-weight: 700;">${r.beneish_score || 'N/A'}</td>
          <td class="num">${r.altman_score || 'N/A'}</td>
          <td class="num">${r.piotroski_score ? r.piotroski_score + '/9' : 'N/A'}</td>
          <td class="num">${r.anomalies_count > 0 ? '<span style="color:var(--signal-red); font-weight:700;">' + r.anomalies_count + ' FLAGGED</span>' : '<span style="color:var(--signal-green);">CLEAN</span>'}</td>
        `;

        tr.addEventListener("click", () => {
          tickerInput.value = r.ticker;
          runAnalysis(r.ticker);
          document.querySelector('[data-tab="tab-models"]').click();
        });

        tbody.appendChild(tr);
      });
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan='9' style='color:var(--signal-red);'>Screener Error: ${err.message}</td></tr>`;
    }
  }

  // Initial load
  runAnalysis("NVDA");
});
