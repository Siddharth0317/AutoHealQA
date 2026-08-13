'use client';

import React, { useState, useEffect } from 'react';
import { 
  Sparkles, 
  Play, 
  ShieldCheck, 
  Activity, 
  Cpu, 
  FileText, 
  CheckCircle2, 
  AlertTriangle, 
  Wrench, 
  Clock, 
  Lock,
  ExternalLink,
  Layers,
  Download,
  Globe,
  Smartphone,
  Webhook,
  Code,
  Key,
  Unlock,
  X
} from 'lucide-react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<'generate' | 'execute' | 'self-healing' | 'webhooks' | 'admin'>('generate');
  const [role, setRole] = useState<'tester' | 'admin'>('tester');
  const [adminPasscode, setAdminPasscode] = useState<string>('');
  const [showAdminModal, setShowAdminModal] = useState<boolean>(false);
  const [passcodeInput, setPasscodeInput] = useState<string>('');
  const [passcodeError, setPasscodeError] = useState<string | null>(null);

  // Multi-Browser & Device & Execution Mode Controls
  const [browserType, setBrowserType] = useState<'chromium' | 'firefox' | 'webkit'>('chromium');
  const [devicePreset, setDevicePreset] = useState<'Desktop' | 'iPhone 14' | 'Pixel 7'>('Desktop');
  const [isHeadless, setIsHeadless] = useState<boolean>(false);

  // State for Requirement Generator
  const [requirement, setRequirement] = useState<string>(
    "As a registered user, I want to navigate to https://example.com, verify the main page header is visible, check that the main container loads correctly, and click the primary action button."
  );
  const [targetUrl, setTargetUrl] = useState<string>("https://example.com");
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [generatedSuite, setGeneratedSuite] = useState<any>(null);

  // State for Code Exporter
  const [exportedCode, setExportedCode] = useState<string | null>(null);
  const [exportedFormat, setExportedFormat] = useState<'python' | 'gherkin'>('python');

  // State for Test Executor
  const [isExecuting, setIsExecuting] = useState<boolean>(false);
  const [latestRun, setLatestRun] = useState<any>(null);

  // State for History & Admin Metrics
  const [historyData, setHistoryData] = useState<any>(null);
  const [adminMetrics, setAdminMetrics] = useState<any>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Jira Webhook Tester State
  const [jiraIssueKey, setJiraIssueKey] = useState<string>("QA-101");
  const [jiraSummary, setJiraSummary] = useState<string>("Verify payment checkout button");
  const [isWebhookTesting, setIsWebhookTesting] = useState<boolean>(false);
  const [webhookResult, setWebhookResult] = useState<any>(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  useEffect(() => {
    if (activeTab === 'admin' && role === 'admin') {
      fetchAdminMetrics();
    }
  }, [activeTab, role]);

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_BASE}/history`, {
        headers: { 'X-User-Role': role }
      });
      if (res.ok) {
        const data = await res.json();
        setHistoryData(data);
      }
    } catch (err) {
      console.warn("Could not fetch backend history.");
    }
  };

  const fetchAdminMetrics = async () => {
    try {
      const headers: Record<string, str> = { 'X-User-Role': 'admin' };
      if (adminPasscode) {
        headers['X-Admin-Passcode'] = adminPasscode;
      }
      const res = await fetch(`${API_BASE}/admin/metrics`, { headers });
      if (res.ok) {
        const data = await res.json();
        setAdminMetrics(data);
      } else {
        setRole('tester');
        setAdminMetrics(null);
      }
    } catch (err) {
      console.warn("Could not fetch admin metrics:", err);
    }
  };

  const handleVerifyPasscode = async () => {
    setPasscodeError(null);
    try {
      const res = await fetch(`${API_BASE}/admin/verify-passcode`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ passcode: passcodeInput })
      });

      if (res.ok) {
        setAdminPasscode(passcodeInput);
        setRole('admin');
        setShowAdminModal(false);
        setPasscodeInput('');
        if (activeTab === 'admin') {
          fetchAdminMetrics();
        }
      } else {
        setPasscodeError('Invalid Admin Passcode (Default: admin123)');
      }
    } catch (err: any) {
      setPasscodeError('Could not verify passcode with server.');
    }
  };

  const handleSwitchAdminClick = () => {
    if (role === 'admin') {
      // Lock Admin
      setRole('tester');
      setAdminPasscode('');
      setAdminMetrics(null);
    } else {
      setShowAdminModal(true);
    }
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    setErrorMsg(null);
    try {
      const res = await fetch(`${API_BASE}/generate-tests`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Role': role
        },
        body: JSON.stringify({
          requirement_text: requirement,
          target_url: targetUrl
        })
      });

      if (!res.ok) {
        throw new Error(`Server returned status ${res.status}`);
      }

      const data = await res.json();
      setGeneratedSuite(data);
      fetchHistory();
    } catch (err: any) {
      setErrorMsg(`Failed to generate test cases: ${err.message}`);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleExecute = async () => {
    if (!generatedSuite) return;
    setIsExecuting(true);
    setErrorMsg(null);
    try {
      const res = await fetch(`${API_BASE}/execute-tests`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Role': role
        },
        body: JSON.stringify({
          test_suite: generatedSuite,
          target_url_override: targetUrl,
          headless: isHeadless,
          browser_type: browserType,
          device_preset: devicePreset
        })
      });

      if (!res.ok) {
        throw new Error(`Execution error (${res.status})`);
      }

      const data = await res.json();
      setLatestRun(data);
      setActiveTab('execute');
      fetchHistory();
    } catch (err: any) {
      setErrorMsg(`Failed to execute test suite: ${err.message}`);
    } finally {
      setIsExecuting(false);
    }
  };

  const handleExportCode = async (fmt: 'python' | 'gherkin') => {
    if (!generatedSuite) return;
    try {
      const res = await fetch(`${API_BASE}/export-code`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          test_suite: generatedSuite,
          export_format: fmt
        })
      });
      if (res.ok) {
        const data = await res.json();
        setExportedCode(data.exported_code);
        setExportedFormat(fmt);
      }
    } catch (err) {
      console.error("Failed to export code:", err);
    }
  };

  const handleDownloadPdfReport = async () => {
    if (!generatedSuite) return;
    try {
      const res = await fetch(`${API_BASE}/export-pdf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          test_suite: generatedSuite,
          latest_run: latestRun
        })
      });
      if (res.ok) {
        const htmlText = await res.text();
        const win = window.open('', '_blank');
        if (win) {
          win.document.write(htmlText);
          win.document.close();
        }
      }
    } catch (err) {
      console.error("Failed to generate PDF report:", err);
    }
  };

  const handleExportZip = async () => {
    if (!generatedSuite) return;
    try {
      const res = await fetch(`${API_BASE}/export-zip`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          test_suite: generatedSuite,
          latest_run: latestRun
        })
      });
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `AutoHealQA_Suite_${generatedSuite.id || 'export'}.zip`;
        document.body.appendChild(a);
        a.click();
        a.remove();
      }
    } catch (err) {
      console.error("Failed to export zip bundle:", err);
    }
  };

  const handleTestJiraWebhook = async () => {
    setIsWebhookTesting(true);
    try {
      const res = await fetch(`${API_BASE}/webhooks/jira`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          issue_key: jiraIssueKey,
          summary: jiraSummary,
          description: "Auto-ingested ticket from Jira Automation Rule",
          target_url: targetUrl
        })
      });
      if (res.ok) {
        const data = await res.json();
        setWebhookResult(data);
        fetchHistory();
      }
    } catch (err: any) {
      setErrorMsg(`Webhook simulation failed: ${err.message}`);
    } finally {
      setIsWebhookTesting(false);
    }
  };

  return (
    <main className="space-y-6">
      {/* Header Bar */}
      <header className="glass-panel p-6 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 shadow-lg shadow-indigo-500/30">
            <Cpu className="w-7 h-7 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold tracking-tight text-white">AutoHealQA</h1>
              <span className="badge badge-healed">v1.0</span>
            </div>
            <p className="text-sm text-slate-400">Autonomous QA Engine • Multi-Browser • Visual Regression • Jira/GitHub Webhooks</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/60 border border-slate-800 text-xs">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="text-slate-300 font-mono">AutoHeal Neural Engine (70B)</span>
          </div>

          <div className="flex items-center gap-2 bg-slate-900/80 p-1 rounded-xl border border-slate-800">
            <button
              onClick={() => setRole('tester')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                role === 'tester' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-white'
              }`}
            >
              Tester Mode
            </button>
            <button
              onClick={handleSwitchAdminClick}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1 ${
                role === 'admin' ? 'bg-purple-600 text-white shadow' : 'text-slate-400 hover:text-white'
              }`}
            >
              {role === 'admin' ? (
                <>
                  <Unlock className="w-3 h-3" /> Admin Unlocked
                </>
              ) : (
                <>
                  <Lock className="w-3 h-3 text-slate-400" /> Admin Mode
                </>
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Main Navigation Tabs */}
      <nav className="glass-panel p-2 flex flex-wrap gap-2">
        <button
          onClick={() => setActiveTab('generate')}
          className={`tab-btn flex items-center gap-2 ${activeTab === 'generate' ? 'active' : ''}`}
        >
          <Sparkles className="w-4 h-4" />
          1. Requirements Analyzer
        </button>

        <button
          onClick={() => setActiveTab('execute')}
          className={`tab-btn flex items-center gap-2 ${activeTab === 'execute' ? 'active' : ''}`}
        >
          <Play className="w-4 h-4" />
          2. Live Test Executor
        </button>

        <button
          onClick={() => setActiveTab('self-healing')}
          className={`tab-btn flex items-center gap-2 ${activeTab === 'self-healing' ? 'active' : ''}`}
        >
          <Wrench className="w-4 h-4 text-amber-400" />
          3. Self-Healing Audit Logs
        </button>

        <button
          onClick={() => setActiveTab('webhooks')}
          className={`tab-btn flex items-center gap-2 ${activeTab === 'webhooks' ? 'active' : ''}`}
        >
          <Webhook className="w-4 h-4 text-cyan-400" />
          4. Jira / GitHub Webhooks
        </button>

        <button
          onClick={() => {
            if (role !== 'admin') {
              setShowAdminModal(true);
            } else {
              setActiveTab('admin');
            }
          }}
          className={`tab-btn flex items-center gap-2 ${activeTab === 'admin' ? 'active' : ''}`}
        >
          <Activity className="w-4 h-4 text-purple-400" />
          5. Admin Telemetry {role !== 'admin' && <Lock className="w-3 h-3 text-slate-500" />}
        </button>
      </nav>

      {/* ADMIN PASSCODE AUTHENTICATION MODAL */}
      {showAdminModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="glass-panel p-6 max-w-md w-full space-y-4 border-purple-500/40 relative animate-in fade-in zoom-in-95">
            <button
              onClick={() => setShowAdminModal(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-3">
              <div className="p-3 rounded-xl bg-purple-600/20 border border-purple-500/30 text-purple-400">
                <Key className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white">Admin Security Access</h3>
                <p className="text-xs text-slate-400">Enter Admin Security Passcode to unlock metrics</p>
              </div>
            </div>

            {passcodeError && (
              <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
                <AlertTriangle className="w-4 h-4" />
                {passcodeError}
              </div>
            )}

            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300">Admin Passcode</label>
              <input
                type="password"
                value={passcodeInput}
                onChange={(e) => setPasscodeInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleVerifyPasscode()}
                placeholder="Enter passcode (Default: admin123)"
                className="w-full p-3 rounded-xl bg-slate-950 border border-slate-800 text-white font-mono text-sm focus:border-purple-500 focus:outline-none"
              />
            </div>

            <div className="flex gap-2 pt-2">
              <button
                onClick={() => setShowAdminModal(false)}
                className="w-1/2 py-2.5 rounded-xl border border-slate-800 text-slate-400 hover:bg-slate-800 text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                onClick={handleVerifyPasscode}
                className="w-1/2 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold shadow-lg shadow-purple-600/30"
              >
                Authenticate Admin
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Global Error Banner */}
      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <span className="text-sm">{errorMsg}</span>
        </div>
      )}

      {/* TAB 1: REQUIREMENTS ANALYZER */}
      {activeTab === 'generate' && (
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="glass-panel p-6 space-y-4 flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-2 mb-3">
                <FileText className="w-5 h-5 text-indigo-400" />
                <h2 className="text-lg font-semibold text-white">Natural Language Requirement / Jira Story</h2>
              </div>
              
              <textarea
                value={requirement}
                onChange={(e) => setRequirement(e.target.value)}
                rows={5}
                className="w-full p-4 rounded-xl bg-slate-950/80 border border-slate-800 text-slate-200 text-sm focus:outline-none focus:border-indigo-500 font-mono"
                placeholder="Enter user story or raw requirement..."
              />

              <div className="mt-4 space-y-2">
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Target Application URL</label>
                <input
                  type="url"
                  value={targetUrl}
                  onChange={(e) => setTargetUrl(e.target.value)}
                  className="w-full p-3 rounded-xl bg-slate-950/80 border border-slate-800 text-slate-200 text-sm focus:outline-none focus:border-indigo-500 font-mono"
                  placeholder="https://example.com"
                />
              </div>

              <div className="mt-4 pt-4 border-t border-slate-800 grid grid-cols-3 gap-3">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-400 flex items-center gap-1">
                    <Globe className="w-3.5 h-3.5 text-cyan-400" /> Browser Engine
                  </label>
                  <select
                    value={browserType}
                    onChange={(e: any) => setBrowserType(e.target.value)}
                    className="w-full p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-white"
                  >
                    <option value="chromium">Chromium (Chrome)</option>
                    <option value="firefox">Firefox</option>
                    <option value="webkit">WebKit (Safari)</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-400 flex items-center gap-1">
                    <Smartphone className="w-3.5 h-3.5 text-purple-400" /> Device Viewport
                  </label>
                  <select
                    value={devicePreset}
                    onChange={(e: any) => setDevicePreset(e.target.value)}
                    className="w-full p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-white"
                  >
                    <option value="Desktop">Desktop (1280x720)</option>
                    <option value="iPhone 14">iPhone 14 (390x844)</option>
                    <option value="Pixel 7">Pixel 7 (412x915)</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-400 flex items-center gap-1">
                    <Activity className="w-3.5 h-3.5 text-emerald-400" /> Execution Mode
                  </label>
                  <select
                    value={isHeadless ? "headless" : "headed"}
                    onChange={(e: any) => setIsHeadless(e.target.value === "headless")}
                    className="w-full p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-white"
                  >
                    <option value="headed">👀 Open Live Browser Window</option>
                    <option value="headless">⚡ Background Headless Mode</option>
                  </select>
                </div>
              </div>
            </div>

            <button
              onClick={handleGenerate}
              disabled={isGenerating || !requirement.trim()}
              className="glow-btn w-full justify-center py-3.5 mt-4"
            >
              {isGenerating ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  Analyzing Requirements via AutoHeal Neural Engine...
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5" />
                  Generate Structured BDD Test Cases
                </>
              )}
            </button>
          </div>

          <div className="glass-panel p-6 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Layers className="w-5 h-5 text-purple-400" />
                <h2 className="text-lg font-semibold text-white">Generated BDD Scenario & Test Steps</h2>
              </div>
              {generatedSuite && (
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleDownloadPdfReport}
                    className="px-2.5 py-1.5 rounded-lg bg-indigo-600/30 hover:bg-indigo-600/50 text-xs text-indigo-200 flex items-center gap-1 border border-indigo-500/40 font-semibold"
                  >
                    <Download className="w-3.5 h-3.5 text-indigo-300" /> Download PDF Report
                  </button>
                  <button
                    onClick={() => handleExportCode('python')}
                    className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-200 flex items-center gap-1 border border-slate-700"
                  >
                    <Code className="w-3.5 h-3.5 text-emerald-400" /> Pytest .py
                  </button>
                  <button
                    onClick={handleExecute}
                    disabled={isExecuting}
                    className="glow-btn glow-btn-cyan text-xs py-2 px-3"
                  >
                    {isExecuting ? "Launching..." : "Execute Test Suite"}
                  </button>
                </div>
              )}
            </div>

            {exportedCode ? (
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                  <span className="text-xs font-mono font-bold text-emerald-400 uppercase">
                    Exported {exportedFormat.toUpperCase()} Code:
                  </span>
                  <button
                    onClick={() => setExportedCode(null)}
                    className="text-xs text-slate-400 hover:text-white"
                  >
                    Close Preview
                  </button>
                </div>
                <pre className="p-3 rounded-lg bg-slate-900 text-xs font-mono text-slate-200 overflow-x-auto max-h-[350px]">
                  {exportedCode}
                </pre>
              </div>
            ) : generatedSuite ? (
              <div className="space-y-4 max-h-[480px] overflow-y-auto pr-2">
                <div className="p-3 rounded-lg bg-indigo-950/40 border border-indigo-800/40 text-xs">
                  <span className="font-bold text-indigo-300">Suite ID:</span> {generatedSuite.id} | <span className="font-bold text-indigo-300">Model:</span> {generatedSuite.metadata?.model_used || 'AutoHeal-Neural-70B'}
                </div>

                {generatedSuite.scenarios?.map((sc: any, idx: number) => (
                  <div key={idx} className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="badge badge-passed">{sc.id}</span>
                      <h3 className="text-sm font-semibold text-slate-100">{sc.title}</h3>
                    </div>

                    <pre className="p-3 rounded-lg bg-slate-950 text-xs text-emerald-400 font-mono overflow-x-auto">
                      {sc.gherkin_text}
                    </pre>

                    <div className="space-y-2">
                      <h4 className="text-xs font-bold text-slate-400 uppercase">Executable Steps ({sc.test_steps?.length})</h4>
                      {sc.test_steps?.map((step: any, sIdx: number) => (
                        <div key={sIdx} className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/60 text-xs flex items-center justify-between gap-2">
                          <span className="font-mono text-indigo-400 font-semibold">#{step.step_number}</span>
                          <span className="badge bg-slate-800 text-slate-300">{step.action}</span>
                          <span className="text-slate-300 flex-1 truncate">{step.target_description}</span>
                          <span className="font-mono text-slate-500 text-[10px] truncate max-w-[120px]">{step.selector_hint || 'auto'}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="h-[380px] flex flex-col items-center justify-center text-center p-6 text-slate-500 space-y-3 border-2 border-dashed border-slate-800 rounded-xl">
                <Sparkles className="w-10 h-10 text-slate-600 animate-pulse" />
                <p className="text-sm">Click "Generate Structured BDD Test Cases" to process natural language requirements into Playwright test scripts.</p>
              </div>
            )}
          </div>
        </section>
      )}

      {/* TAB 2: LIVE TEST EXECUTOR */}
      {activeTab === 'execute' && (
        <section className="space-y-6">
          <div className="glass-panel p-6 space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <Play className="w-6 h-6 text-emerald-400" />
                  Live Playwright Test Execution Hub
                </h2>
                <p className="text-sm text-slate-400">Engine: <span className="font-mono text-cyan-400">{browserType}</span> | Device: <span className="font-mono text-purple-400">{devicePreset}</span></p>
              </div>

              {latestRun && (
                <div className="flex flex-wrap items-center gap-3">
                  <a
                    href={`${API_BASE}/test-runs/${latestRun.run_id}/report`}
                    target="_blank"
                    rel="noreferrer"
                    className="glow-btn text-xs py-2 px-3 flex items-center gap-1.5"
                  >
                    <Download className="w-3.5 h-3.5" /> Download PDF/HTML Report
                  </a>
                  {latestRun.trace_url && (
                    <a
                      href={`http://localhost:8000${latestRun.trace_url}`}
                      download
                      className="px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-200 flex items-center gap-1 border border-slate-700"
                    >
                      <Download className="w-3.5 h-3.5 text-cyan-400" /> Playwright Trace .zip
                    </a>
                  )}
                  <span className={`badge ${
                    latestRun.status === 'passed' ? 'badge-passed' :
                    latestRun.status === 'healed' ? 'badge-healed' : 'badge-failed'
                  }`}>
                    {latestRun.status.toUpperCase()}
                  </span>
                  <span className="text-xs text-slate-400 font-mono flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5" />
                    {latestRun.duration_ms} ms
                  </span>
                </div>
              )}
            </div>

            {latestRun ? (
              <div className="space-y-6">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
                    <span className="text-xs text-slate-400 font-medium">Total Steps</span>
                    <p className="text-2xl font-bold text-white font-mono mt-1">{latestRun.total_steps}</p>
                  </div>
                  <div className="p-4 rounded-xl bg-emerald-950/30 border border-emerald-800/40 text-center">
                    <span className="text-xs text-emerald-400 font-medium">Steps Passed</span>
                    <p className="text-2xl font-bold text-emerald-400 font-mono mt-1">{latestRun.steps_passed}</p>
                  </div>
                  <div className="p-4 rounded-xl bg-amber-950/30 border border-amber-800/40 text-center">
                    <span className="text-xs text-amber-400 font-medium">Auto-Healed Steps</span>
                    <p className="text-2xl font-bold text-amber-400 font-mono mt-1">{latestRun.steps_healed}</p>
                  </div>
                  <div className="p-4 rounded-xl bg-rose-950/30 border border-rose-800/40 text-center">
                    <span className="text-xs text-rose-400 font-medium">Steps Failed</span>
                    <p className="text-2xl font-bold text-rose-400 font-mono mt-1">{latestRun.steps_failed}</p>
                  </div>
                </div>

                <div className="rounded-xl border border-slate-800 overflow-hidden">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-900 text-slate-400 border-b border-slate-800 uppercase text-[10px]">
                      <tr>
                        <th className="p-3">#</th>
                        <th className="p-3">Action</th>
                        <th className="p-3">Target Description</th>
                        <th className="p-3">Selector Used</th>
                        <th className="p-3">Status</th>
                        <th className="p-3">Duration</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 bg-slate-950/60">
                      {latestRun.step_logs?.map((log: any, idx: number) => (
                        <tr key={idx} className="hover:bg-slate-900/40">
                          <td className="p-3 font-mono text-indigo-400 font-semibold">{log.step_number}</td>
                          <td className="p-3"><span className="badge bg-slate-800 text-slate-200">{log.action}</span></td>
                          <td className="p-3 text-slate-200">{log.target_description}</td>
                          <td className="p-3 font-mono text-slate-400">{log.selector_used || 'auto'}</td>
                          <td className="p-3">
                            <span className={`badge ${
                              log.status === 'passed' ? 'badge-passed' :
                              log.status === 'healed' ? 'badge-healed' : 'badge-failed'
                            }`}>
                              {log.status}
                            </span>
                          </td>
                          <td className="p-3 font-mono text-slate-400">{log.execution_time_ms}ms</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {latestRun.screenshots?.length > 0 && (
                  <div className="space-y-3 pt-2">
                    <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                      <Download className="w-4 h-4 text-indigo-400" /> Captured Step Screenshots ({latestRun.screenshots.length})
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {latestRun.screenshots.map((shotUrl: string, sIdx: number) => (
                        <div key={sIdx} className="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
                          <img
                            src={`http://localhost:8000${shotUrl}`}
                            alt={`Step ${sIdx + 1} screenshot`}
                            className="w-full h-36 object-cover rounded-lg border border-slate-800 bg-slate-950"
                          />
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-slate-400 font-mono">Step #{sIdx + 1}</span>
                            <a
                              href={`http://localhost:8000${shotUrl}`}
                              download={`step_${sIdx + 1}_screenshot.png`}
                              target="_blank"
                              rel="noreferrer"
                              className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold flex items-center gap-1"
                            >
                              <Download className="w-3 h-3" /> Download
                            </a>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="p-12 text-center text-slate-500 space-y-3">
                <Play className="w-10 h-10 mx-auto text-slate-600 animate-pulse" />
                <p>No active execution run. Generate test cases first and click "Execute Test Suite".</p>
              </div>
            )}
          </div>
        </section>
      )}

      {/* TAB 3: SELF-HEALING AUDIT LOGS */}
      {activeTab === 'self-healing' && (
        <section className="glass-panel p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Wrench className="w-6 h-6 text-amber-400" />
              Self-Healing Selector Repair Engine Logs
            </h2>
            <span className="badge badge-healed">AI Powered Repair</span>
          </div>

          {latestRun?.self_healing_events?.length > 0 ? (
            <div className="space-y-4">
              {latestRun.self_healing_events.map((event: any, idx: number) => (
                <div key={idx} className="p-4 rounded-xl bg-amber-950/20 border border-amber-500/30 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="badge badge-healed">Step #{event.step_number} Healed</span>
                    <span className="text-xs text-amber-300 font-mono">Confidence: {(event.confidence_score * 100).toFixed(0)}%</span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                    <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                      <span className="text-rose-400 font-bold block mb-1">❌ Failed Original Selector:</span>
                      <code className="text-rose-300 font-mono">{event.original_selector}</code>
                    </div>

                    <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                      <span className="text-emerald-400 font-bold block mb-1">✨ AI Healed Selector:</span>
                      <code className="text-emerald-300 font-mono">{event.healed_selector}</code>
                    </div>
                  </div>

                  <p className="text-xs text-slate-300 bg-slate-950/60 p-3 rounded-lg border border-slate-800/80 font-mono">
                    <span className="text-amber-400 font-semibold">Reasoning:</span> {event.reasoning}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-12 text-center text-slate-500 space-y-2">
              <CheckCircle2 className="w-10 h-10 mx-auto text-emerald-500" />
              <p className="text-slate-300 font-semibold">No selector failures detected in recent run.</p>
              <p className="text-xs text-slate-500">When Playwright locators fail, the Groq LLM Agent automatically inspects the DOM and repairs selectors live.</p>
            </div>
          )}
        </section>
      )}

      {/* TAB 4: JIRA & GITHUB WEBHOOKS */}
      {activeTab === 'webhooks' && (
        <section className="glass-panel p-6 space-y-6">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Webhook className="w-6 h-6 text-cyan-400" />
              CI/CD Automation Webhook Integration Hub
            </h2>
            <p className="text-sm text-slate-400">Trigger hands-free AI test generation & Playwright execution straight from Jira or GitHub PRs</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-5 rounded-xl bg-slate-900/90 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <span className="font-bold text-white text-sm">Jira Webhook Listener</span>
                <span className="badge badge-passed">Active Endpoint</span>
              </div>
              <code className="p-2.5 rounded-lg bg-slate-950 text-xs font-mono text-cyan-300 block truncate">
                POST http://localhost:8000/api/v1/webhooks/jira
              </code>

              <div className="space-y-2 pt-2">
                <span className="text-xs font-semibold text-slate-400">Simulate Jira Ticket Ingestion:</span>
                <div className="grid grid-cols-3 gap-2">
                  <input
                    type="text"
                    value={jiraIssueKey}
                    onChange={(e) => setJiraIssueKey(e.target.value)}
                    className="p-2 rounded bg-slate-950 border border-slate-800 text-xs text-white font-mono"
                    placeholder="Issue Key"
                  />
                  <input
                    type="text"
                    value={jiraSummary}
                    onChange={(e) => setJiraSummary(e.target.value)}
                    className="col-span-2 p-2 rounded bg-slate-950 border border-slate-800 text-xs text-white"
                    placeholder="Summary"
                  />
                </div>
                <button
                  onClick={handleTestJiraWebhook}
                  disabled={isWebhookTesting}
                  className="glow-btn glow-btn-cyan text-xs py-2 w-full justify-center"
                >
                  {isWebhookTesting ? "Processing Webhook..." : "Trigger Jira Webhook Event"}
                </button>
              </div>
            </div>

            <div className="p-5 rounded-xl bg-slate-900/90 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <span className="font-bold text-white text-sm">GitHub PR Webhook Listener</span>
                <span className="badge badge-passed">Active Endpoint</span>
              </div>
              <code className="p-2.5 rounded-lg bg-slate-950 text-xs font-mono text-purple-300 block truncate">
                POST http://localhost:8000/api/v1/webhooks/github
              </code>

              <p className="text-xs text-slate-400 leading-relaxed">
                Connect your GitHub repository webhooks for <code className="text-purple-300 font-mono">pull_request.opened</code> events. Auto-reads PR details and runs Playwright tests against preview URLs.
              </p>
            </div>
          </div>

          {webhookResult && (
            <div className="p-4 rounded-xl bg-cyan-950/30 border border-cyan-500/30 space-y-2">
              <span className="text-xs font-bold text-cyan-300 uppercase">Webhook Execution Response:</span>
              <pre className="p-3 rounded-lg bg-slate-950 text-xs font-mono text-slate-200 overflow-x-auto">
                {JSON.stringify(webhookResult, null, 2)}
              </pre>
            </div>
          )}
        </section>
      )}

      {/* TAB 5: ADMIN TELEMETRY */}
      {activeTab === 'admin' && (
        <section className="glass-panel p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Activity className="w-6 h-6 text-purple-400" />
              Admin System Performance & API Audit Logs
            </h2>
            {role === 'admin' && (
              <button
                onClick={() => {
                  setRole('tester');
                  setAdminPasscode('');
                  setAdminMetrics(null);
                }}
                className="px-3 py-1.5 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/40 text-rose-300 text-xs font-semibold flex items-center gap-1.5"
              >
                <Lock className="w-3.5 h-3.5" /> Lock Admin Session
              </button>
            )}
          </div>

          {role === 'admin' && adminMetrics ? (
            <div className="space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                  <span className="text-xs text-slate-400 font-medium">Generations</span>
                  <p className="text-xl font-bold text-white font-mono mt-1">{adminMetrics?.total_test_generations || 0}</p>
                </div>
                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                  <span className="text-xs text-slate-400 font-medium">Executions</span>
                  <p className="text-xl font-bold text-white font-mono mt-1">{adminMetrics?.total_test_executions || 0}</p>
                </div>
                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                  <span className="text-xs text-slate-400 font-medium">Total Steps</span>
                  <p className="text-xl font-bold text-white font-mono mt-1">{adminMetrics?.total_steps_executed || 0}</p>
                </div>
                <div className="p-4 rounded-xl bg-amber-950/40 border border-amber-800/40">
                  <span className="text-xs text-amber-400 font-medium">Heal Events</span>
                  <p className="text-xl font-bold text-amber-400 font-mono mt-1">{adminMetrics?.total_self_healing_events || 0}</p>
                </div>
                <div className="p-4 rounded-xl bg-emerald-950/40 border border-emerald-800/40">
                  <span className="text-xs text-emerald-400 font-medium">Heal Success</span>
                  <p className="text-xl font-bold text-emerald-400 font-mono mt-1">{adminMetrics?.self_healing_success_rate || 100}%</p>
                </div>
                <div className="p-4 rounded-xl bg-purple-950/40 border border-purple-800/40">
                  <span className="text-xs text-purple-400 font-medium">Tokens Used</span>
                  <p className="text-xl font-bold text-purple-400 font-mono mt-1">{adminMetrics?.total_llm_tokens_consumed || 0}</p>
                </div>
              </div>

              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-slate-200">Recent API Requests & Latency Logs</h3>
                <div className="rounded-xl border border-slate-800 overflow-hidden">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-900 text-slate-400 border-b border-slate-800 uppercase text-[10px]">
                      <tr>
                        <th className="p-3">Endpoint</th>
                        <th className="p-3">Method</th>
                        <th className="p-3">Status</th>
                        <th className="p-3">User Role</th>
                        <th className="p-3">Duration</th>
                        <th className="p-3">Timestamp</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 bg-slate-950/60">
                      {adminMetrics?.api_call_logs?.map((log: any, idx: number) => (
                        <tr key={idx} className="hover:bg-slate-900/40">
                          <td className="p-3 font-mono text-indigo-400">{log.endpoint}</td>
                          <td className="p-3"><span className="badge bg-slate-800 text-slate-300">{log.method}</span></td>
                          <td className="p-3"><span className="badge badge-passed">{log.status_code}</span></td>
                          <td className="p-3 text-slate-300">{log.user_role}</td>
                          <td className="p-3 font-mono text-slate-400">{log.duration_ms}ms</td>
                          <td className="p-3 font-mono text-slate-500 text-[10px]">{log.timestamp}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-12 text-center text-slate-400 space-y-4 bg-slate-950/60 rounded-xl border border-slate-800">
              <Lock className="w-12 h-12 mx-auto text-purple-400" />
              <div className="space-y-1">
                <h3 className="text-lg font-semibold text-white">Admin Privileges Required</h3>
                <p className="text-sm text-slate-400 max-w-md mx-auto">
                  System metrics, token consumption, and API latency audit logs require Admin passcode verification.
                </p>
              </div>
              <button
                onClick={() => setShowAdminModal(true)}
                className="glow-btn py-2 px-4 text-xs"
              >
                Authenticate Admin Security
              </button>
            </div>
          )}
        </section>
      )}
    </main>
  );
}
