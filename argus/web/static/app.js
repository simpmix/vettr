document.addEventListener("DOMContentLoaded", () => {
  const tickerForm = document.getElementById("ticker-form");
  const tickerInput = document.getElementById("ticker-input");
  const loadingOverlay = document.getElementById("loading-overlay");
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabPanels = document.querySelectorAll(".tab-panel");
  const quickPills = document.querySelectorAll(".ticker-pill");
  const btnExportDossier = document.getElementById("btn-export-dossier");
  const screenerPills = document.querySelectorAll(".screener-pill");

  let currentTicker = "NVDA";

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

      // If screener tab opened for the first time, load screener
      if (targetId === "tab-screener") {
        const activePreset = document.querySelector(".screener-pill.active");
        const preset = activePreset ? activePreset.getAttribute("data-preset") : "mega_tech";
        loadScreener(preset);
      }
    });
  });

  // Global hotkey '/' to focus search
  document.addEventListener("keydown", (e) => {
    if (e.key === "/" && document.activeElement !== tickerInput) {
      e.preventDefault();
      tickerInput.focus();
      tickerInput.select();
    }
  });

  // Quick ticker pill click
  quickPills.forEach(pill => {
    pill.addEventListener("click", () => {
      const ticker = pill.getAttribute("data-ticker");
      tickerInput.value = ticker;
      runAnalysis(ticker);
    });
  });

  // Export Dossier Markdown download
  btnExportDossier.addEventListener("click", () => {
    if (currentTicker) {
      window.location.href = `/api/dossier/${currentTicker}`;
    }
  });

  // Screener preset buttons
  screenerPills.forEach(pill => {
    pill.addEventListener("click", () => {
      screenerPills.forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      const preset = pill.getAttribute("data-preset");
      loadScreener(preset);
    });
  });

  // Form submit
  tickerForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const ticker = tickerInput.value.trim().toUpperCase();
    if (ticker) {
      runAnalysis(ticker);
    }
  });

  // Number formatting helpers
  function formatMoney(num) {
    if (num === null || num === undefined) return "N/A";
    const abs = Math.abs(num);
    if (abs >= 1e12) return `$${(num / 1e12).toFixed(2)}T`;
    if (abs >= 1e9) return `$${(num / 1e9).toFixed(2)}B`;
    if (abs >= 1e6) return `$${(num / 1e6).toFixed(2)}M`;
    if (abs >= 1e3) return `$${(num / 1e3).toFixed(2)}K`;
    return `$${num.toFixed(2)}`;
  }

  // Load and render analysis
  async function runAnalysis(ticker) {
    currentTicker = ticker.toUpperCase();
    loadingOverlay.classList.remove("hidden");
    try {
      const resp = await fetch(`/api/analyze/${currentTicker}`);
      if (!resp.ok) {
        throw new Error(`Failed to fetch report for ${currentTicker}`);
      }
      const data = await resp.json();
      renderDashboard(data);
    } catch (err) {
      alert(`Error loading analysis: ${err.message}`);
    } finally {
      loadingOverlay.classList.add("hidden");
    }
  }

  function renderDashboard(data) {
    const mkt = data.market_data || {};
    const forensics = data.forensics || {};
    const riskScore = data.risk_score || 0;

    // 1. Hero HUD
    document.getElementById("hud-ticker").textContent = data.ticker || "UNKNOWN";
    document.getElementById("hud-name").textContent = mkt.name || data.ticker;
    document.getElementById("hud-cik").textContent = `CIK: ${data.cik || 'N/A'}`;
    document.getElementById("hud-sector").textContent = `Sector: ${mkt.sector || 'N/A'}`;
    document.getElementById("hud-industry").textContent = `Industry: ${mkt.industry || 'N/A'}`;

    document.getElementById("hud-price").textContent = `$${(mkt.current_price || 0).toFixed(2)}`;
    const chgEl = document.getElementById("hud-change");
    const chg = mkt.change_pct || 0;
    chgEl.textContent = `${chg >= 0 ? '+' : ''}${chg.toFixed(2)}%`;
    chgEl.className = `price-change-pill ${chg >= 0 ? 'positive' : 'negative'}`;

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
    let verdictText = "LOW / AUDITED HEALTH";
    if (riskScore >= 60) {
      riskClass = "high";
      verdictText = "CRITICAL / FORENSIC RED FLAGS";
    } else if (riskScore >= 30) {
      riskClass = "medium";
      verdictText = "MODERATE SCRUTINY & RISKS";
    }

    riskBadge.className = `risk-score-badge ${riskClass}`;
    riskFill.className = `risk-bar-fill ${riskClass}`;
    riskVerdict.textContent = verdictText;

    // 2. TAB 1: Quantitative Models
    // Beneish
    const b = forensics.beneish_m_score;
    const bScore = document.getElementById("beneish-score");
    const bStatus = document.getElementById("beneish-status");
    const bVars = document.getElementById("beneish-vars");
    bVars.innerHTML = "";

    if (b) {
      bScore.textContent = b.score;
      bScore.className = `metric-value ${b.is_manipulator ? 'red' : 'green'}`;
      bStatus.textContent = b.status;
      bStatus.className = `model-badge ${b.is_manipulator ? 'badge-red' : 'badge-green'}`;

      if (b.variables) {
        for (const [k, v] of Object.entries(b.variables)) {
          bVars.innerHTML += `
            <div class="var-row">
              <span class="var-label">${k}</span>
              <span class="var-val">${v}</span>
            </div>
          `;
        }
      }
    } else {
      bScore.textContent = "N/A";
      bStatus.textContent = "Insufficient Historical Filings";
    }

    // Altman Z
    const z = forensics.altman_z_score;
    const zScore = document.getElementById("altman-score");
    const zStatus = document.getElementById("altman-status");
    const zVars = document.getElementById("altman-vars");
    zVars.innerHTML = "";

    if (z) {
      zScore.textContent = z.score;
      const zClass = z.risk_level === 'low' ? 'green' : (z.risk_level === 'medium' ? 'yellow' : 'red');
      zScore.className = `metric-value ${zClass}`;
      zStatus.textContent = z.zone;
      zStatus.className = `model-badge badge-${zClass}`;

      if (z.components) {
        for (const [k, v] of Object.entries(z.components)) {
          zVars.innerHTML += `
            <div class="var-row">
              <span class="var-label">${k}</span>
              <span class="var-val">${v}</span>
            </div>
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
    const fVars = document.getElementById("piotroski-vars");
    fVars.innerHTML = "";

    if (f) {
      fScore.textContent = `${f.score} / ${f.max_score}`;
      const fClass = f.score >= 7 ? 'green' : (f.score >= 5 ? 'yellow' : 'red');
      fScore.className = `metric-value ${fClass}`;
      fStatus.textContent = f.rating;
      fStatus.className = `model-badge badge-${fClass}`;

      if (f.signals) {
        for (const [k, v] of Object.entries(f.signals)) {
          fVars.innerHTML += `
            <div class="var-row">
              <span class="var-label">${k}</span>
              <span class="var-val" style="color: ${v === 1 ? 'var(--accent-green)' : 'var(--accent-red)'}">${v === 1 ? '✓ PASS' : '✗ FAIL'}</span>
            </div>
          `;
        }
      }
    } else {
      fScore.textContent = "N/A";
      fStatus.textContent = "N/A";
    }

    // Anomalies Feed
    const anoContainer = document.getElementById("anomalies-container");
    const anoPill = document.getElementById("anomaly-count-pill");
    const anomalies = forensics.anomalies || [];
    anoPill.textContent = `${anomalies.length} ALERTS`;
    anoContainer.innerHTML = "";

    if (anomalies.length === 0) {
      anoContainer.innerHTML = `
        <div style="color: var(--accent-green); padding: 12px; background: rgba(0, 230, 118, 0.05); border: 1px solid rgba(0,230,118,0.2); border-radius: 4px; font-size: 12px;">
          ✓ No significant balance sheet decoupling or cash flow divergences detected.
        </div>
      `;
    } else {
      anomalies.forEach(a => {
        anoContainer.innerHTML += `
          <div class="anomaly-item ${a.severity}">
            <div class="anomaly-top">
              <span class="anomaly-title">${a.title}</span>
              <span class="anomaly-sev ${a.severity}">${a.severity}</span>
            </div>
            <div class="anomaly-desc">${a.description}</div>
            <div class="anomaly-metric">${a.metric || ''}</div>
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
        <div style="color: var(--text-muted); font-size: 11px; padding: 6px 0;">
          No critical disclosure phrases (subpoena, material weakness, restatement) surfaced in latest section scans.
        </div>
      `;
    } else {
      regFlags.forEach(rf => {
        regContainer.innerHTML += `
          <div class="reg-item">
            <div class="reg-title">⚠️ ${rf.title}</div>
            <div class="reg-excerpt">${rf.excerpt}</div>
          </div>
        `;
      });
    }

    // Sentiment
    const s = forensics.sentiment;
    if (s) {
      document.getElementById("sentiment-tone").textContent = s.tone || "BALANCED";
      document.getElementById("sent-unc").style.width = `${Math.min(100, (s.uncertainty_pct || 0) * 20)}%`;
      document.getElementById("sent-unc-val").textContent = `${s.uncertainty_pct}%`;
      document.getElementById("sent-lit").style.width = `${Math.min(100, (s.litigious_pct || 0) * 20)}%`;
      document.getElementById("sent-lit-val").textContent = `${s.litigious_pct}%`;
      document.getElementById("sent-neg").style.width = `${Math.min(100, (s.negative_pct || 0) * 20)}%`;
      document.getElementById("sent-neg-val").textContent = `${s.negative_pct}%`;
      document.getElementById("sent-pos").style.width = `${Math.min(100, (s.positive_pct || 0) * 20)}%`;
      document.getElementById("sent-pos-val").textContent = `${s.positive_pct}%`;
    }

    // 3. TAB 2: Filing Diff
    const diff = data.diff_analysis;
    const addedList = document.getElementById("diff-added-list");
    const removedList = document.getElementById("diff-removed-list");
    addedList.innerHTML = "";
    removedList.innerHTML = "";

    if (diff) {
      document.getElementById("diff-sim").textContent = `Similarity: ${diff.similarity_pct}%`;
      document.getElementById("diff-added-count").textContent = `+${diff.added_count} Added Sentences`;
      document.getElementById("diff-removed-count").textContent = `-${diff.removed_count} Removed Sentences`;

      (diff.sample_added || []).forEach(sentence => {
        addedList.innerHTML += `<div class="diff-sentence added">+ ${sentence}</div>`;
      });

      (diff.sample_removed || []).forEach(sentence => {
        removedList.innerHTML += `<div class="diff-sentence removed">- ${sentence}</div>`;
      });
    } else {
      addedList.innerHTML = "<div style='color:var(--text-muted); padding: 10px;'>No prior 10-K diff available.</div>";
      removedList.innerHTML = "<div style='color:var(--text-muted); padding: 10px;'>No prior 10-K diff available.</div>";
    }

    // 4. TAB 3: DuPont ROE Decomposition
    const dupontList = data.dupont_series || [];
    const dupontTbody = document.querySelector("#dupont-table tbody");
    dupontTbody.innerHTML = "";

    if (dupontList.length > 0) {
      dupontList.forEach(d => {
        dupontTbody.innerHTML += `
          <tr>
            <td><strong>FY ${d.fiscal_year}</strong></td>
            <td style="color: var(--accent-cyan); font-weight: 700;">${d.roe_pct}%</td>
            <td>${d.roa_pct}%</td>
            <td>${d.net_profit_margin_pct}%</td>
            <td>${d.operating_margin_pct}%</td>
            <td>${d.asset_turnover}x</td>
            <td>${d.equity_multiplier}x</td>
            <td style="color: ${d.quality_verdict.includes('HIGH') ? 'var(--accent-green)' : (d.quality_verdict.includes('LEVERAGE') ? 'var(--accent-red)' : 'var(--text-secondary)')}; font-weight: 600;">
              ${d.quality_verdict}
            </td>
          </tr>
        `;
      });
    } else {
      dupontTbody.innerHTML = "<tr><td colspan='8'>No DuPont decomposition records available.</td></tr>";
    }

    // 5. TAB 4: Form 4 Insider Radar
    const insider = data.insider_activity || {};
    const insiderBadge = document.getElementById("insider-sentiment-badge");
    const insiderTbody = document.querySelector("#insiders-table tbody");
    insiderTbody.innerHTML = "";

    insiderBadge.textContent = insider.sentiment || "NEUTRAL";
    const sentClass = (insider.sentiment || '').includes("SELLING") ? "red" : ((insider.sentiment || '').includes("ACCUMULATION") ? "green" : "");
    insiderBadge.className = `stat-badge ${sentClass}`;

    const trades = insider.trades || [];
    if (trades.length > 0) {
      trades.forEach(t => {
        const isBuy = t.transaction_type === "BUY";
        insiderTbody.innerHTML += `
          <tr>
            <td>${t.transaction_date}</td>
            <td><strong>${t.owner}</strong></td>
            <td style="color: var(--text-secondary);">${t.title}</td>
            <td><span class="anomaly-sev ${isBuy ? 'MEDIUM' : 'HIGH'}" style="background: ${isBuy ? 'rgba(0,230,118,0.2)' : 'rgba(255,56,92,0.2)'}; color: ${isBuy ? 'var(--accent-green)' : 'var(--accent-red)'}; font-weight: 700;">${t.transaction_type}</span></td>
            <td>${t.shares.toLocaleString()}</td>
            <td>${t.price_per_share > 0 ? '$' + t.price_per_share.toFixed(2) : '-'}</td>
            <td style="color: #FFF; font-weight: 600;">${formatMoney(t.total_value)}</td>
            <td><a href="${t.filing_url}" target="_blank" rel="noopener noreferrer" class="edgar-link">Form 4 ↗</a></td>
          </tr>
        `;
      });
    } else {
      insiderTbody.innerHTML = "<tr><td colspan='8'>No recent Form 4 insider transactions recorded.</td></tr>";
    }

    // 6. TAB 6: Audited Financials
    const finSeries = data.financial_series || [];
    const finTable = document.getElementById("financials-table");
    const thead = finTable.querySelector("thead tr");
    const tbody = finTable.querySelector("tbody");
    
    thead.innerHTML = "<th>Financial Metric (USD)</th>";
    tbody.innerHTML = "";

    if (finSeries.length > 0) {
      finSeries.forEach(item => {
        thead.innerHTML += `<th>FY ${item.fiscal_year}</th>`;
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
          rowHtml += `<td>${formatMoney(val)}</td>`;
        });
        tbody.innerHTML += `<tr>${rowHtml}</tr>`;
      });
    } else {
      tbody.innerHTML = "<tr><td colspan='5'>No XBRL financial statement records found.</td></tr>";
    }

    // 7. TAB 7: Official EDGAR Archive
    const filingsList = (data.filings && data.filings.all_recent) || [];
    const filingsTbody = document.querySelector("#filings-table tbody");
    filingsTbody.innerHTML = "";

    if (filingsList.length > 0) {
      filingsList.forEach(f => {
        filingsTbody.innerHTML += `
          <tr>
            <td><strong style="color: var(--accent-cyan);">${f.form}</strong></td>
            <td>${f.filing_date}</td>
            <td>${f.report_date || f.filing_date}</td>
            <td style="font-family: var(--font-mono); font-size: 11px;">${f.accession_number}</td>
            <td style="color: var(--text-secondary); max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${f.primary_document}</td>
            <td><a href="${f.url}" target="_blank" rel="noopener noreferrer" class="edgar-link">View SEC Filing ↗</a></td>
          </tr>
        `;
      });
    } else {
      filingsTbody.innerHTML = "<tr><td colspan='6'>No recent filings found.</td></tr>";
    }
  }

  // Load Batch Screener
  async function loadScreener(preset) {
    const tbody = document.querySelector("#screener-table tbody");
    tbody.innerHTML = "<tr><td colspan='9' style='text-align:center; padding: 20px; color: var(--accent-cyan);'>Screening EDGAR archives for watchlist...</td></tr>";

    try {
      const resp = await fetch(`/api/screen?preset=${preset}`);
      if (!resp.ok) throw new Error("Failed to load screener");
      const data = await resp.json();
      const results = data.results || [];
      tbody.innerHTML = "";

      results.forEach((r, idx) => {
        const risk = r.risk_score;
        const riskColor = risk >= 60 ? "var(--accent-red)" : (risk >= 30 ? "var(--accent-amber)" : "var(--accent-green)");
        const bColor = r.is_manipulator ? "var(--accent-red)" : "var(--accent-green)";

        tbody.innerHTML += `
          <tr style="cursor: pointer;" onclick="document.getElementById('ticker-input').value='${r.ticker}'; document.getElementById('ticker-form').dispatchEvent(new Event('submit')); document.querySelector('[data-tab=\\'tab-forensics\\']').click();">
            <td><strong>#${idx + 1}</strong></td>
            <td><strong style="color: var(--accent-cyan);">${r.ticker}</strong></td>
            <td>${r.name}</td>
            <td>$${r.price.toFixed(2)}</td>
            <td style="color: ${riskColor}; font-weight: 700;">${risk} / 100</td>
            <td style="color: ${bColor}; font-weight: 600;">${r.beneish_score || 'N/A'}</td>
            <td>${r.altman_score || 'N/A'}</td>
            <td>${r.piotroski_score ? r.piotroski_score + '/9' : 'N/A'}</td>
            <td>${r.anomalies_count > 0 ? '<span style="color:var(--accent-red); font-weight:700;">' + r.anomalies_count + ' Flags</span>' : '<span style="color:var(--accent-green);">0</span>'}</td>
          </tr>
        `;
      });
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan='9' style='color:var(--accent-red);'>Error running screener: ${err.message}</td></tr>`;
    }
  }

  // Initial load with default NVDA
  runAnalysis("NVDA");
});
