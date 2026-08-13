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
  Layers
} from 'lucide-react';

const API_BASE = 'http://localhost:8000/api/v1';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<'generate' | 'execute' | 'self-healing' | 'admin'>('generate');
  const [role, setRole] = useState<'tester' | 'admin'>('tester');
  
  // State for Requirement Generator
  const [requirement, setRequirement] = useState<string>(
    "As a registered user, I want to navigate to https://example.com, verify the main page header is visible, check that the main container loads correctly, and click the primary action button."
  );
  const [targetUrl, setTargetUrl] = useState<string>("https://example.com");
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [generatedSuite, setGeneratedSuite] = useState<any>(null);

  // State for Test Executor
  const [isExecuting, setIsExecuting] = useState<boolean>(false);
  const [latestRun, setLatestRun] = useState<any>(null);

  // State for History & Admin Metrics
  const [historyData, setHistoryData] = useState<any>(null);
  const [adminMetrics, setAdminMetrics] = useState<any>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Load history on mount
  useEffect(() => {
    fetchHistory();
  }, []);

  // Fetch admin metrics when switching to admin tab
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
      console.warn("Could not fetch backend history. Server may be starting up.");
    }
  };

  const fetchAdminMetrics = async () => {
    try {
      const res = await fetch(`${API_BASE}/admin/metrics`, {
        headers: { 'X-User-Role': 'admin' }
      });
      if (res.ok) {
        const data = await res.json();
        setAdminMetrics(data);
      }
    } catch (err) {
      console.warn("Could not fetch admin metrics:", err);
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
          headless: true
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
              <span className="badge badge-healed">v1.0 Agentic</span>
            </div>
            <p className="text-sm text-slate-400">Autonomous AI Test Case Generator & Self-Healing Automation Engine</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* Engine Status Indicators */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/60 border border-slate-800 text-xs">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="text-slate-300 font-mono">Groq Llama-3.3 70B</span>
          </div>

          {/* Role Toggle Selector */}
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
              onClick={() => setRole('admin')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                role === 'admin' ? 'bg-purple-600 text-white shadow' : 'text-slate-400 hover:text-white'
              }`}
            >
              Admin Mode
            </button>
          </div>
        </div>
      </header>

      {/* Main Navigation Tabs */}
      <nav className="glass-panel p-2 flex gap-2">
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
          onClick={() => setActiveTab('admin')}
          className={`tab-btn flex items-center gap-2 ${activeTab === 'admin' ? 'active' : ''}`}
        >
          <Activity className="w-4 h-4 text-purple-400" />
          4. Admin Telemetry {role !== 'admin' && <Lock className="w-3 h-3 text-slate-500" />}
        </button>
      </nav>

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
          {/* Input Panel */}
          <div className="glass-panel p-6 space-y-4 flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-2 mb-3">
                <FileText className="w-5 h-5 text-indigo-400" />
                <h2 className="text-lg font-semibold text-white">Natural Language Requirement / Jira Story</h2>
              </div>
              
              <textarea
                value={requirement}
                onChange={(e) => setRequirement(e.target.value)}
                rows={6}
                className="w-full p-4 rounded-xl bg-slate-950/80 border border-slate-800 text-slate-200 text-sm focus:outline-none focus:border-indigo-500 transition-all font-mono"
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
            </div>

            <button
              onClick={handleGenerate}
              disabled={isGenerating || !requirement.trim()}
              className="glow-btn w-full justify-center py-3.5 mt-4"
            >
              {isGenerating ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  Analyzing Requirements via Groq LLM...
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5" />
                  Generate Structured BDD Test Cases
                </>
              )}
            </button>
          </div>

          {/* Generated BDD Preview Panel */}
          <div className="glass-panel p-6 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Layers className="w-5 h-5 text-purple-400" />
                <h2 className="text-lg font-semibold text-white">Generated BDD Scenario & Test Steps</h2>
              </div>
              {generatedSuite && (
                <button
                  onClick={handleExecute}
                  disabled={isExecuting}
                  className="glow-btn glow-btn-cyan text-xs py-2 px-3"
                >
                  {isExecuting ? "Launching..." : "Execute Test Suite"}
                </button>
              )}
            </div>

            {generatedSuite ? (
              <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2">
                <div className="p-3 rounded-lg bg-indigo-950/40 border border-indigo-800/40 text-xs">
                  <span className="font-bold text-indigo-300">Suite ID:</span> {generatedSuite.id} | <span className="font-bold text-indigo-300">Model:</span> {generatedSuite.metadata?.model_used || 'groq-llama-3.3-70b'}
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
                      <h4 className="text-xs font-bold text-slate-400 uppercase">Executable Playwright Steps ({sc.test_steps?.length})</h4>
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
                <p className="text-sm text-slate-400">Headless Chromium Runner with Dynamic DOM Inspection & Self-Healing Retry</p>
              </div>

              {latestRun && (
                <div className="flex items-center gap-3">
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
                {/* Summary Metric Cards */}
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

                {/* Execution Step Table */}
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

      {/* TAB 4: ADMIN TELEMETRY */}
      {activeTab === 'admin' && (
        <section className="glass-panel p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Activity className="w-6 h-6 text-purple-400" />
              Admin System Performance & API Audit Logs
            </h2>
            {role !== 'admin' && (
              <span className="badge badge-failed flex items-center gap-1">
                <Lock className="w-3 h-3" /> Access Restricted
              </span>
            )}
          </div>

          {role === 'admin' ? (
            <div className="space-y-6">
              {/* Telemetry Metric Cards */}
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

              {/* API Call Audit Log Table */}
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
                  System metrics, token consumption, and API latency audit logs are unlocked for Admin users.
                </p>
              </div>
              <button
                onClick={() => setRole('admin')}
                className="glow-btn py-2 px-4 text-xs"
              >
                Switch to Admin Mode
              </button>
            </div>
          )}
        </section>
      )}
    </main>
  );
}
