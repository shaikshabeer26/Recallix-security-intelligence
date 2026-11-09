
import {
  getBackendHealth,
  getAllIncidents,
  getIncident,
  analyzeIncident,
  verifyIncident
} from './services/api';
import { useEffect, useState } from 'react';
import {
  Activity, AlertTriangle, BrainCircuit, Network, CheckCircle2, ChevronRight,
  Clock3, Database, FileSearch, LayoutDashboard, LoaderCircle,
  Plus, RefreshCw, Shield, ShieldAlert, Sparkles, Terminal, ListChecks
} from 'lucide-react';


const panel = 'rounded-2xl border border-white/10 bg-[#0c1422]/80 backdrop-blur-md shadow-2xl shadow-cyan-950/20 transition-all hover:border-cyan-500/20';
// const field = 'w-full rounded-xl border border-white/10 bg-[#080f1b] px-4 py-3 text-sm text-slate-200 outline-none focus:border-cyan-400/50';
const field = 'w-full rounded-xl border border-white/10 bg-[#080f1b] px-4 py-3 text-sm text-slate-200 outline-none transition-all duration-200 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400/30';
const label = 'mb-2 block text-xs font-medium text-slate-400';



function MemoryCard({ memory, index, onOpenSource }) {
  const metadata = memory.metadata || {};
  const sourceId = metadata.incident_id;

  const isVerified =
    metadata.verification_status === 'analyst_verified';

  const verificationStatus = isVerified
    ? 'Analyst verified'
    : metadata.verification_status
      ? 'Not verified'
      : 'Verification status unavailable';

  const sourceFacts = Array.isArray(memory.source_facts)
    ? memory.source_facts
    : [];

  return (
    <div className="rounded-xl border border-cyan-400/10 bg-[#080f1b] p-4">
      {/* Memory type and verification */}
      <div className="flex flex-wrap items-center justify-between gap-2">
        <span className="text-[10px] uppercase tracking-widest text-cyan-300">
          {memory.type || 'Historical memory'}
        </span>

        <span
          className={`rounded-full px-2.5 py-1 text-[10px] ${
            isVerified
              ? 'bg-emerald-400/10 text-emerald-300'
              : 'bg-amber-400/10 text-amber-300'
          }`}
        >
          {verificationStatus}
        </span>
      </div>

      {/* Main memory */}
      <p className="mt-3 text-sm leading-6 text-slate-300">
        {memory.text || 'No memory text available.'}
      </p>

      {/* Memory metadata */}
      <div className="mt-4 flex flex-wrap items-center gap-x-4 gap-y-2 border-t border-white/5 pt-3 text-xs text-slate-500">
        {sourceId && (
          <span>Source: INC-{sourceId}</span>
        )}

        {metadata.incident_type && (
          <span>Category: {metadata.incident_type}</span>
        )}

        {metadata.source && (
          <span>Memory source: {metadata.source}</span>
        )}
      </div>

      {/* Original incident link */}
      {sourceId && onOpenSource && (
        <button
          onClick={() => onOpenSource(sourceId)}
          className="mt-3 text-xs font-medium text-cyan-300 hover:text-cyan-200"
        >
          View source incident →
        </button>
      )}

      {/* Supporting source evidence */}
      {sourceFacts.length > 0 && (
        <details className="mt-4 rounded-lg border border-white/10 bg-white/[0.02]">
          <summary className="cursor-pointer px-3 py-3 text-xs font-medium text-cyan-300 hover:text-cyan-200">
            Supporting Evidence ({sourceFacts.length})
          </summary>

          <div className="space-y-3 border-t border-white/5 p-3">
            {sourceFacts.map((fact, factIndex) => {
              const factMetadata = fact.metadata || {};
              const factSourceId =
                factMetadata.incident_id || sourceId;

              return (
                <div
                  key={fact.id || factIndex}
                  className="rounded-lg border border-white/5 bg-[#050b14] p-3"
                >
                  <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
                    <span className="text-[10px] uppercase tracking-wider text-slate-500">
                      {fact.type || 'Original fact'}
                    </span>

                    {factSourceId && (
                      <span className="text-[10px] text-slate-500">
                        Source: INC-{factSourceId}
                      </span>
                    )}
                  </div>

                  <p className="text-xs leading-6 text-slate-300">
                    {fact.text || 'No source text available.'}
                  </p>

                  {factSourceId && onOpenSource && (
                    <button
                      onClick={() => onOpenSource(factSourceId)}
                      className="mt-2 text-[11px] text-cyan-300 hover:text-cyan-200"
                    >
                      Open original incident →
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        </details>
      )}
    </div>
  );
}

function AIInvestigationReport({ analysis, status, error, model }) {
  const statusDetails = {
    completed: {
      label: 'AI analysis completed',
      style: 'border-emerald-400/20 bg-emerald-400/10 text-emerald-300'
    },
    quota_limited: {
      label: 'Provider quota reached',
      style: 'border-amber-400/20 bg-amber-400/10 text-amber-300'
    },
    timeout: {
      label: 'AI request timed out',
      style: 'border-amber-400/20 bg-amber-400/10 text-amber-300'
    },
    connection_error: {
      label: 'AI connection unavailable',
      style: 'border-amber-400/20 bg-amber-400/10 text-amber-300'
    },
    configuration_error: {
      label: 'AI configuration issue',
      style: 'border-rose-400/20 bg-rose-400/10 text-rose-300'
    },
    unavailable: {
      label: 'AI analysis unavailable',
      style: 'border-amber-400/20 bg-amber-400/10 text-amber-300'
    },
    failed: {
      label: 'AI analysis failed',
      style: 'border-rose-400/20 bg-rose-400/10 text-rose-300'
    }
  };

  const currentStatus = statusDetails[status] || statusDetails.unavailable;

  const errorMessage = typeof error === 'string'
    ? error
    : error?.message || 'No additional error information is available.';

  const sections = [
    {
      title: 'Evidence analysis',
      icon: FileSearch,
      items: analysis?.evidence_analysis,
      color: 'text-cyan-300'
    },
    {
      title: 'Historical comparison',
      icon: BrainCircuit,
      items: analysis?.historical_comparison,
      color: 'text-violet-300'
    },
    {
      title: 'Uncertainties and evidence gaps',
      icon: AlertTriangle,
      items: analysis?.uncertainties,
      color: 'text-amber-300'
    },
    {
      title: 'Next investigation steps',
      icon: ListChecks,
      items: analysis?.next_investigation_steps,
      color: 'text-emerald-300'
    }
  ];

  return (
    <div className={panel + ' p-6'}>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="rounded-xl bg-violet-400/10 p-2 text-violet-300">
            <Sparkles size={21} />
          </div>

          <div>
            <h3 className="font-semibold">AI Investigation Report</h3>
            <p className="mt-1 text-xs text-slate-500">
              Groq LLM · Evidence-based investigative reasoning
            </p>
          </div>
        </div>

        <span className={`rounded-full border px-3 py-1.5 text-xs font-semibold ${currentStatus.style}`}>
          {currentStatus.label}
        </span>
      </div>

      {analysis ? (
        <div className="mt-6 space-y-5">
          <div className="rounded-xl border border-violet-400/15 bg-violet-400/[0.04] p-5">
            <h4 className="text-sm font-semibold text-violet-200">
              Executive summary
            </h4>
            <p className="mt-3 text-sm leading-7 text-slate-300">
              {analysis.executive_summary || 'No summary provided.'}
            </p>
          </div>

          {sections.map(({ title, icon: Icon, items, color }) => (
            <div key={title}>
              <h4 className={`flex items-center gap-2 text-sm font-semibold ${color}`}>
                <Icon size={17} />
                {title}
              </h4>

              {Array.isArray(items) && items.length > 0 ? (
                <ul className="mt-3 space-y-3">
                  {items.map((item, index) => (
                    <li key={index} className="flex gap-3 text-sm leading-6 text-slate-300">
                      <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-md bg-white/5 text-[10px] text-slate-400">
                        {index + 1}
                      </span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="mt-2 text-sm text-slate-500">
                  No information provided.
                </p>
              )}
            </div>
          ))}

          <div className="rounded-xl border border-cyan-400/15 bg-cyan-400/[0.04] p-5">
            <h4 className="text-sm font-semibold text-cyan-200">
              Analyst guidance
            </h4>
            <p className="mt-3 text-sm leading-7 text-slate-300">
              {analysis.analyst_guidance || 'No analyst guidance provided.'}
            </p>
          </div>

          {model && (
            <p className="text-xs text-slate-500">
              Model: {model}
            </p>
          )}

          <p className="border-t border-white/5 pt-4 text-xs leading-5 text-slate-500">
            AI-generated guidance is not proof of an incident. Validate findings
            against available evidence. Risk score and severity are calculated
            separately by the RECALLIX risk assessment engine.
          </p>
        </div>
      ) : (
        <div className="mt-5 rounded-xl border border-amber-400/10 bg-amber-400/[0.04] p-4">
          <p className="text-sm text-amber-200">
            The AI investigation report could not be generated.
          </p>

          <p className="mt-2 break-words text-xs leading-5 text-slate-400">
            {errorMessage}
          </p>

          <p className="mt-2 text-xs text-slate-500">
            The rule-based risk assessment remains available. No AI-generated
            conclusions should be assumed.
          </p>
        </div>
      )}
    </div>
  );
}

function App() {
  const [selectedIncident, setSelectedIncident] = useState(null);
const [detailLoading, setDetailLoading] = useState(false);
const [detailVerification, setDetailVerification] = useState({});
  const [page, setPage] = useState('dashboard');
  const [backend, setBackend] = useState(false);
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [verification, setVerification] = useState(null);
  const [notes, setNotes] = useState('');

  const [form, setForm] = useState({
    title: '',
    incident_type: 'auth',
    description: '',
    evidence: ''
  });
  const openIncident = async (id) => {
  setDetailLoading(true);
  setError('');
  setSelectedIncident(null);
  setPage('detail');

  try {
    const data = await getIncident(id);
    setSelectedIncident(data);
  } catch (err) {
    setError(
      err.response?.data?.detail ||
      'Could not load incident details.'
    );
    setPage('dashboard');
  } finally {
    setDetailLoading(false);
  }
};

  const refresh = async () => {
    setLoading(true);
    try {
      const [health, data] = await Promise.all([
        getBackendHealth(),
        getAllIncidents()
      ]);
      setBackend(health.success ===  true);
      setIncidents(data.incidents || []);
      setError('');
    } catch (err) {
      setBackend(false);
      setError(err.response?.data?.detail || 'Backend connection failed.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const updateForm = (key, value) => {
    setForm(previous => ({ ...previous, [key]: value }));
  };

  const submitIncident = async (event) => {
    event.preventDefault();
    setAnalyzing(true);
    setError('');
    setResult(null);
    setVerification(null);

    try {
      const payload = {
        title: form.title,
        incident_type: form.incident_type,
        description: form.description,
        evidence: form.evidence
          .split('\n')
          .map(item => item.trim())
          .filter(Boolean)
      };

      // const data = await analyzeIncident(payload);
      // setResult(data);
      const data = await analyzeIncident(payload);

setResult({
  ...data.investigation,
  incident_id: data.incident_id,
  title: data.incident?.title || form.title,
  incident_type: data.incident?.incident_type || form.incident_type,
  description: data.incident?.description || form.description,
  evidence: data.incident?.evidence || payload.evidence,
  storage: data.storage,
  created_at: data.created_at
});
      setNotes('');
      await refresh();
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        'Investigation failed. Check the FastAPI terminal.'
      );
    } finally {
      setAnalyzing(false);
    }
  };

  const confirmFindings = async () => {
    const id = result?.incident_id || result?.id;
    if (!id) {
      setError('Incident ID missing from the analysis response.');
      return;
    }

    setVerifying(true);
    setError('');

    try {
      const response = await verifyIncident(id, true, notes);
      setVerification(response);
      setDetailVerification(previous => ({
  ...previous,
  [id]: {
    verified: response.verified === true,
    retained: response.retained === true
  }
}));
      await refresh();
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        'Verification or Hindsight retention failed.'
      );
    } finally {
      setVerifying(false);
    }
  };

  const stats = {
    total: incidents.length,
    high: incidents.filter(i =>
      ['HIGH', 'CRITICAL'].includes((i.severity || '').toUpperCase())
    ).length,
    memory: incidents.filter(i => i.memory_used).length,
    average: incidents.length
      ? Math.round(incidents.reduce((sum, i) =>
          sum + Number(i.risk_score || 0), 0) / incidents.length)
      : 0
  };

  const riskColor = (severity) => {
    const value = (severity || '').toUpperCase();
    if (value === 'CRITICAL' || value === 'HIGH') return 'text-rose-300';
    if (value === 'MEDIUM') return 'text-amber-300';
    return 'text-emerald-300';
  };

  const memories = result?.historical_context || [];

  return (
    <div className="min-h-screen bg-[#070b14] text-slate-100">
      <div className="flex min-h-screen">
        <aside className="hidden w-64 shrink-0 flex-col border-r border-white/10 bg-[#0a101c] lg:flex">
          <div className="border-b border-white/10 p-6">
            <div className="flex items-center gap-3">
              <div className="rounded-xl bg-cyan-400/10 p-2 text-cyan-300">
                <Shield size={23} />
              </div>
              <div>
                <h1 className="font-bold tracking-[0.18em]">RECALLIX</h1>
                <p className="text-[9px] tracking-widest text-slate-500">
                  SECURITY INTELLIGENCE
                </p>
              </div>
            </div>
          </div>

          <nav className="space-y-2 p-4">
            <button onClick={() => setPage('dashboard')}
              className={`flex w-full items-center gap-3 rounded-xl p-3 text-sm ${page === 'dashboard' ? 'bg-cyan-400/10 text-cyan-200' : 'text-slate-400 hover:bg-white/5'}`}>
              <LayoutDashboard size={18} /> Dashboard
            </button>
            <button onClick={() => { setPage('investigate'); setResult(null); setVerification(null); }}
              className={`flex w-full items-center gap-3 rounded-xl p-3 text-sm ${page === 'investigate' ? 'bg-cyan-400/10 text-cyan-200' : 'text-slate-400 hover:bg-white/5'}`}>
              <Plus size={18} /> New investigation
            </button>
          </nav>

          <div className="mt-auto p-4">
            <div className={panel + ' p-4'}>
              <div className="flex items-center gap-2 text-sm text-cyan-300">
                <BrainCircuit size={17} /> Hindsight Memory
              </div>
              <p className="mt-2 text-xs leading-5 text-slate-500">
                Recall previous investigation lessons and retain verified findings.
              </p>
              <p className="mt-3 text-xs text-emerald-300">
                ● Local integration
              </p>
            </div>
            <p className="mt-4 text-[10px] text-slate-600">RECALLIX v1.0.0</p>
          </div>
        </aside>

        <main className="min-w-0 flex-1">
          <header className="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 px-5 py-5 sm:px-8">
            <div>
              <p className="text-sm font-semibold">
                {page === 'dashboard' ? 'Security overview' : 'Incident investigation'}
              </p>
              <p className="mt-1 text-xs text-slate-500">
                AI Security Incident Intelligence
              </p>
            </div>
            <div className="flex items-center gap-3">
              <span className={`text-xs ${backend ? 'text-emerald-300' : 'text-rose-300'}`}>
                ● {backend ? 'System online' : 'Backend offline'}
              </span>
              <button onClick={refresh} className="rounded-lg border border-white/10 p-2 text-slate-300 hover:bg-white/5" title="Refresh">
                <RefreshCw size={16} />
              </button>
            </div>
          </header>

          <div className="mx-auto max-w-6xl space-y-6 p-5 sm:p-8">
            {error && (
              <div className="flex items-center gap-3 rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-200">
                <AlertTriangle size={18} /> {error}
              </div>
            )}

            {page === 'dashboard' && (
              <>
                <section>
                  <p className="mb-2 flex items-center gap-2 text-xs font-semibold tracking-widest text-cyan-300">
                    <Activity size={15} /> SECURITY OPERATIONS CENTER
                  </p>
                  <h2 className="text-3xl font-semibold">Intelligence dashboard</h2>
                  <p className="mt-2 text-sm text-slate-400">
                    Investigate threats. Learn from history. Improve every response.
                  </p>
                </section>

                <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                  {[
                    ['Total incidents', stats.total, Database],
                    ['High-risk incidents', stats.high, AlertTriangle],
                    ['Memory-assisted', stats.memory, BrainCircuit],
                    ['Average risk', `${stats.average}/100`, Activity]
                  ].map(([title, value, Icon]) => (
                    <div className={panel + ' p-5'} key={title}>
                      <div className="flex justify-between">
                        <p className="text-sm text-slate-400">{title}</p>
                        <Icon size={19} className="text-cyan-300" />
                      </div>
                      <p className="mt-4 text-3xl font-semibold">{loading ? '...' : value}</p>
                    </div>
                  ))}
                </section>

                <section className={panel + ' p-6'}>
                  <div className="flex flex-wrap items-center justify-between gap-4">
                    <div>
                      <p className="flex items-center gap-2 text-xs font-semibold tracking-widest text-cyan-300">
                        <BrainCircuit size={16} /> CONTINUOUS LEARNING
                      </p>
                      <h3 className="mt-3 text-xl font-semibold">
                        Every investigation makes the next one smarter.
                      </h3>
                      <p className="mt-2 text-sm text-slate-400">
                        Hindsight recalls past lessons and retains analyst-verified findings.
                      </p>
                    </div>
                    <button onClick={() => { setPage('investigate'); setResult(null); setVerification(null); }}
                      className="flex items-center gap-2 rounded-xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 hover:bg-cyan-300">
                      <Plus size={17} /> Investigate incident
                    </button>
                  </div>
                </section>

                <section className={panel + ' overflow-hidden'}>
                  <div className="flex items-center justify-between border-b border-white/10 p-5">
                    <div>
                      <h3 className="font-semibold">Recent investigations</h3>
                      <p className="mt-1 text-xs text-slate-500">Live records from SQLite</p>
                    </div>
                    <button onClick={refresh} className="text-xs text-cyan-300">Refresh data</button>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full min-w-[650px] text-left text-sm">
                      <thead className="text-[10px] uppercase tracking-widest text-slate-500">
                        <tr className="border-b border-white/10">
                          <th className="p-4">Incident</th>
                          <th className="p-4">Category</th>
                          <th className="p-4">Severity</th>
                          <th className="p-4">Risk</th>
                          <th className="p-4">Hindsight</th>
                        </tr>
                      </thead>
                <tbody>
                {incidents.map(item => (
                  <tr
                    key={item.id}
                    onClick={() => openIncident(item.id)}
                    className="cursor-pointer border-b border-white/5 transition hover:bg-cyan-400/5"
                    title="Open incident details"
                  >
                    {/* Incident */}
                    <td className="max-w-sm p-4">
                      <div className="flex items-center gap-2">
                        <p className="truncate font-medium text-slate-200">
                          {item.title}
                        </p>
                        <ChevronRight
                          size={14}
                          className="shrink-0 text-cyan-400"
                        />
                      </div>
                      <p className="mt-1 text-xs text-slate-500">
                        INC-{item.id}
                      </p>
                    </td>

                    {/* Category */}
                    <td className="p-4 text-xs capitalize text-slate-400">
                      {item.incident_type}
                    </td>

                    {/* Severity */}
                    <td className={`p-4 text-xs font-semibold ${riskColor(item.severity)}`}>
                      {item.severity}
                    </td>

                    {/* Risk */}
                    <td className="p-4 text-xs font-semibold tabular-nums">
                      {item.risk_score}/100
                    </td>

                    {/* Hindsight */}
                    <td className="p-4">
                      {item.memory_used ? (
                        <span className="text-xs font-medium text-cyan-300">
                          ● Recalled
                        </span>
                      ) : (
                        <span className="text-xs text-slate-500">
                          Not used
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
                    </table>
                  </div>
                  {!incidents.length && !loading && (
                    <p className="p-8 text-center text-sm text-slate-500">No incidents yet.</p>
                  )}
                </section>
              </>
            )}

            {page === 'detail' && (
  <section className="space-y-5">
    <button
      onClick={() => setPage('dashboard')}
      className="flex items-center gap-2 text-sm text-cyan-300 hover:text-cyan-200"
    >
      ← Back to dashboard
    </button>

    {detailLoading && (
      <div className={panel + ' p-8 text-center text-slate-400'}>
        <LoaderCircle className="mx-auto mb-3 animate-spin" />
        Loading investigation details...
      </div>
    )}

    {selectedIncident && (() => {
      const item = selectedIncident.incident;
      const isVerified = item.verified === true;
      const isRetained = item.memory_retained === true;
      return (
        <>
          <div className={panel + ' p-6'}>
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="text-xs tracking-widest text-cyan-300">
                  INCIDENT INVESTIGATION · INC-{item.id}
                </p>
                <h2 className="mt-3 text-2xl font-semibold">
                  {item.title}
                </h2>
                <p className="mt-2 text-sm text-slate-400">
                  {item.incident_type} · {new Date(item.created_at).toLocaleString()}
                </p>
              </div>

              <span className={`rounded-full border border-white/10 px-4 py-2 text-sm font-bold ${riskColor(item.severity)}`}>
                {item.severity}
              </span>
            </div>

            <div className="mt-6 grid gap-4 sm:grid-cols-3">
              <div className="rounded-xl bg-[#080f1b] p-4">
                <p className="text-xs text-slate-500">Risk score</p>
                <p className="mt-2 text-3xl font-bold">{item.risk_score}/100</p>
              </div>

              <div className="rounded-xl bg-[#080f1b] p-4">
                <p className="text-xs text-slate-500">Hindsight during analysis</p>
                <p className="mt-2 font-semibold text-cyan-300">
                  {item.memory_used ? 'Memory assisted' : 'Not used'}
                </p>
              </div>
              <div className="rounded-xl bg-[#080f1b] p-4">
              <p className="text-xs text-slate-500">Analyst verification</p>

              <p className={`mt-2 font-semibold ${
                isVerified ? 'text-emerald-300' : 'text-amber-300'
              }`}>
                {isVerified ? 'Verified' : 'Pending verification'}
              </p>

              <p className={`mt-1 text-xs ${
                isRetained ? 'text-emerald-400' : 'text-slate-500'
              }`}>
                {isRetained
                  ? 'Lesson retained in Hindsight'
                  : 'No retained lesson confirmed'}
              </p>
            </div>
              
            </div>
          </div>

          <div className={panel + ' p-6'}>
            <h3 className="font-semibold">Incident description</h3>
            <p className="mt-3 text-sm leading-7 text-slate-300">
              {item.description}
            </p>

            <h3 className="mt-6 font-semibold">Submitted evidence</h3>
            <ul className="mt-3 space-y-2">
              {(item.evidence || []).map((evidence, index) => (
                <li key={index} className="flex gap-3 text-sm text-slate-300">
                  <CheckCircle2 size={17} className="shrink-0 text-cyan-300" />
                  {evidence}
                </li>
              ))}
            </ul>
          </div>

          <div className={panel + ' p-6'}>
            <h3 className="font-semibold">Risk assessment</h3>

            <p className="mt-5 text-sm font-medium text-slate-400">
              Risk factors
            </p>
            <div className="mt-2 flex flex-wrap gap-2">
              {(item.risk_factors || []).map((factor, index) => (
                <span key={index} className="rounded-lg bg-rose-400/10 px-3 py-2 text-xs text-rose-200">
                  {factor}
                </span>
              ))}
            </div>

            <p className="mt-5 text-sm font-medium text-slate-400">
              Indicators
            </p>
            <ul className="mt-2 space-y-2 text-sm text-slate-300">
              {(item.indicators || []).map((indicator, index) => (
                <li key={index}>• {indicator}</li>
              ))}
            </ul>

            <p className="mt-5 text-sm font-medium text-slate-400">
              Recommended actions
            </p>
            <ol className="mt-2 space-y-3">
              {(item.recommendations || []).map((action, index) => (
                <li key={index} className="flex gap-3 text-sm leading-6 text-slate-300">
                  <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-lg bg-cyan-400/10 text-xs text-cyan-300">
                    {index + 1}
                  </span>
                  {action}
                </li>
              ))}
            </ol>
          </div>
          
          {/* Persistent AI Investigation Report */}
          <AIInvestigationReport
            analysis={item.llm_analysis}
            status={item.llm_status}
            error={item.llm_error}
            model={item.llm_model}
          />
        
          
          <div className={panel + ' p-6'}>
            <div className="flex items-center gap-2">
              <BrainCircuit size={20} className="text-cyan-300" />
              <h3 className="font-semibold">Hindsight historical context</h3>
            </div>

            <p className="mt-2 text-xs leading-5 text-slate-500">
              Related historical memories retrieved for this incident.
              These are reference material, not proof of the current incident.
            </p>

            {selectedIncident.historical_context?.length ? (
              <div className="mt-4 space-y-3">
                {selectedIncident.historical_context.map((memory, index) => (
                <MemoryCard
                  key={memory.id || index}
                  memory={memory}
                  index={index}
                  onOpenSource={(id) => openIncident(id)}
                />
              ))}
              </div>
            ) : (
              <p className="mt-4 text-sm text-slate-500">
                No historical memories were returned for this detail request.
              </p>
            )}

            <p className="mt-4 text-xs text-slate-500">
              Memory retrieval status: {selectedIncident.memory_status || 'Unknown'}
            </p>
          </div>
          
        {/* Related Incident Intelligence */}
        {(() => {
          const relatedIncidents = (
            selectedIncident.historical_context || []
          ).reduce((groups, memory) => {
            const metadata = memory.metadata || {};
            const incidentId = metadata.incident_id;

            // Only show memories with a real source incident ID.
            if (!incidentId || String(incidentId) === String(item.id)) {
              return groups;
            }

            const existing = groups.find(
              (item) => String(item.id) === String(incidentId)
            );

            if (existing) {
              existing.memories.push(memory);
            } else {
              groups.push({
                id: incidentId,
                category: metadata.incident_type || 'Unknown',
                verified: metadata.verification_status === 'analyst_verified',
                memories: [memory],
              });
            }

            return groups;
          }, []);

          return (
            <div className={panel + ' mt-4 p-6'}>
              <div className="flex items-center gap-2">
                <Network size={20} className="text-cyan-300" />
                <h3 className="font-semibold">
                  Related Incident Intelligence
                </h3>
              </div>

              <p className="mt-2 text-xs leading-5 text-slate-500">
                Historical incidents linked through retained Hindsight
                memories. These relationships provide context, not proof.
              </p>

              {relatedIncidents.length > 0 ? (
                <div className="mt-4 space-y-3">
                  {relatedIncidents.map((related) => (
                    <div
                      key={related.id}
                      className="rounded-xl border border-cyan-400/10 bg-[#080f1b] p-4"
                    >
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <span className="text-sm font-semibold text-slate-200">
                          INC-{related.id}
                        </span>

                        <span
                          className={`rounded-full px-2.5 py-1 text-[10px] ${
                            related.verified
                              ? 'bg-emerald-400/10 text-emerald-300'
                              : 'bg-amber-400/10 text-amber-300'
                          }`}
                        >
                          {related.verified
                            ? 'Analyst verified'
                            : 'Verification not established'}
                        </span>
                      </div>

                      <p className="mt-2 text-xs capitalize text-slate-400">
                        Category: {related.category}
                      </p>

                      <p className="mt-2 text-xs text-slate-500">
                        {related.memories.length} related historical
                        {related.memories.length === 1 ? ' memory' : ' memories'}
                      </p>

                      <div className="mt-3 space-y-2">
                        {related.memories.map((memory, memoryIndex) => (
                          <p
                            key={memory.id || memoryIndex}
                            className="rounded-lg bg-white/[0.03] p-3 text-xs leading-5 text-slate-300"
                          >
                            {memory.text}
                          </p>
                        ))}
                      </div>

                      <button
                        onClick={() => openIncident(related.id)}
                        className="mt-3 text-xs font-medium text-cyan-300 hover:text-cyan-200"
                      >
                        Open historical incident →
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="mt-4 rounded-lg border border-white/5 bg-white/[0.02] p-4 text-sm text-slate-500">
                  No historical memories with traceable source incident IDs
                  were found for this investigation.
                </p>
              )}
            </div>
          );
        })()}

        </>
      );
    })()}
  </section>
)}
            {page === 'investigate' && (
              <>
                <section>
                  <p className="mb-2 flex items-center gap-2 text-xs font-semibold tracking-widest text-cyan-300">
                    <FileSearch size={15} /> AI-POWERED INVESTIGATION
                  </p>
                  <h2 className="text-3xl font-semibold">Investigate an incident</h2>
                  <p className="mt-2 text-sm text-slate-400">
                    Submit evidence for risk analysis and historical memory recall.
                  </p>
                </section>

                <form onSubmit={submitIncident} className={panel + ' space-y-5 p-5 sm:p-7'}>
                  <div>
                    <label className={label}>Incident title</label>
                    <input required className={field} value={form.title}
                      onChange={e => updateForm('title', e.target.value)}
                      placeholder="e.g. Suspicious account access after phishing email" />
                  </div>

                  <div>
                    <label className={label}>Incident category</label>
                    <select className={field} value={form.incident_type}
                      onChange={e => updateForm('incident_type', e.target.value)}>
                      <option value="auth">Authentication attack</option>
                      <option value="network">Network incident</option>
                      <option value="malware">Malware</option>
                      <option value="phishing">Phishing</option>
                    </select>
                  </div>

                  <div>
                    <label className={label}>Incident description</label>
                    <textarea required rows={4} className={field} value={form.description}
                      onChange={e => updateForm('description', e.target.value)}
                      placeholder="Describe what happened, affected systems, suspicious activity..." />
                  </div>

                  <div>
                    <label className={label}>Evidence (one item per line)</label>
                    <textarea required rows={5} className={field} value={form.evidence}
                      onChange={e => updateForm('evidence', e.target.value)}
                      placeholder={'Phishing email received\nMalicious link clicked\nCredentials submitted\nSuccessful login from unfamiliar IP'} />
                  </div>

                  <button disabled={analyzing}
                    className="flex w-full items-center justify-center gap-2 rounded-xl bg-cyan-400 px-5 py-3.5 font-semibold text-slate-950 hover:bg-cyan-300 disabled:opacity-60">
                    {analyzing ? <><LoaderCircle className="animate-spin" size={18} /> Investigating and recalling memory...</> : <><Sparkles size={18} /> Analyze incident with RECALLIX</>}
                  </button>
                </form>

                {result && (
                  <section className="space-y-5">
                    <div className={panel + ' p-6'}>
                      <div className="flex flex-wrap items-center justify-between gap-3">
                        <div>
                          <p className="text-xs font-semibold tracking-widest text-emerald-300">INVESTIGATION COMPLETE</p>
                          <h3 className="mt-2 text-xl font-semibold">{result.title || form.title}</h3>
                          <p className="mt-1 text-xs text-slate-500">
                            Incident ID: {result.incident_id || result.id || 'See API response'}
                          </p>
                        </div>
                        <span className={`rounded-full border border-white/10 px-3 py-2 text-sm font-bold ${riskColor(result.severity)}`}>
                          {result.severity || 'ASSESSED'}
                        </span>
                      </div>

                      <div className="mt-6 grid gap-4 sm:grid-cols-3">
                        <div className="rounded-xl bg-[#080f1b] p-4">
                          <p className="text-xs text-slate-500">Risk score</p>
                          <p className="mt-2 text-2xl font-bold">{result.risk_score ?? '—'}/100</p>
                        </div>
                        <div className="rounded-xl bg-[#080f1b] p-4">
                          <p className="text-xs text-slate-500">Hindsight recall</p>
                          <p className="mt-2 text-lg font-semibold text-cyan-300">
                            {result.memory_used ? 'Memory used' : 'No memory used'}
                          </p>
                        </div>
                        <div className="rounded-xl bg-[#080f1b] p-4">
                          <p className="text-xs text-slate-500">Storage</p>
                          <p className="mt-2 text-lg font-semibold text-emerald-300">
                            {result.storage || 'Saved'}
                          </p>
                        </div>
                      </div>

                      <div className="mt-5">
                        <h4 className="mb-2 text-sm font-semibold">Risk factors</h4>
                        <ul className="list-inside list-disc space-y-1 text-sm text-slate-300">
                          {(result.risk_factors || []).map((item, index) => <li key={index}>{typeof item === 'string' ? item : JSON.stringify(item)}</li>)}
                        </ul>
                      </div>

                      <div className="mt-5">
                        <h4 className="mb-2 text-sm font-semibold">Indicators</h4>
                        <div className="flex flex-wrap gap-2">
                          {(result.indicators || []).map((item, index) => (
                            <span key={index} className="rounded-lg border border-cyan-400/20 bg-cyan-400/5 px-3 py-2 text-xs text-cyan-200">
                              {typeof item === 'string' ? item : JSON.stringify(item)}
                            </span>
                          ))}
                        </div>
                      </div>

                      <div className="mt-5">
                        <h4 className="mb-2 text-sm font-semibold">Recommended actions</h4>
                        <ul className="list-inside list-disc space-y-1 text-sm text-slate-300">
                          {(result.recommendations || []).map((item, index) => <li key={index}>{typeof item === 'string' ? item : JSON.stringify(item)}</li>)}
                        </ul>
                      </div>
                    </div>
                   <AIInvestigationReport
                      analysis={result.llm_analysis}
                      status={result.llm_status}
                      error={result.llm_error}
                      model={result.llm_model}
                    />
                    <div className={panel + ' p-6'}>
                      <div className="flex items-center gap-2">
                        <BrainCircuit className="text-cyan-300" size={20} />
                        <h3 className="font-semibold">Hindsight historical context</h3>
                      </div>
                      <p className="mt-2 text-xs text-slate-500">
                        Previous memories retrieved for this investigation. Historical context is reference material, not proof of the current incident.
                      </p>

                      {memories.length ? (
                        <div className="mt-4 space-y-3">
                          {memories.map((memory, index) => (
                          <MemoryCard
                            key={memory.id || index}
                            memory={memory}
                            index={index}
                            onOpenSource={(id) => openIncident(id)}
                          />
                        ))}
                        </div>
                      ) : (
                        <p className="mt-4 text-sm text-slate-500">No historical context was returned.</p>
                      )}
                    </div>

                    <div className={panel + ' p-6'}>
                      <h3 className="font-semibold">Analyst verification</h3>
                      <p className="mt-2 text-sm text-slate-400">
                        Review the findings. Only confirm them if they are verified. Confirmation sends the lesson to Hindsight.
                      </p>
                      <label className={label + ' mt-4'}>Analyst notes</label>
                      <textarea rows={3} className={field} value={notes}
                        onChange={e => setNotes(e.target.value)}
                        placeholder="Explain what you verified and why..." />

                      {verification ? (
                        <div className="mt-4 rounded-xl border border-emerald-500/20 bg-emerald-500/10 p-4 text-sm text-emerald-200">
                          <CheckCircle2 className="mb-2" size={20} />
                          {verification.retained
                            ? 'Verified lesson successfully retained in Hindsight.'
                            : 'Verification response received. Check the result below.'}
                          <pre className="mt-3 overflow-x-auto whitespace-pre-wrap text-xs text-emerald-100/70">
                            {JSON.stringify(verification, null, 2)}
                          </pre>
                        </div>
                      ) : (
                        <button onClick={confirmFindings} disabled={verifying}
                          className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-400 px-5 py-3 font-semibold text-slate-950 hover:bg-emerald-300 disabled:opacity-60">
                          {verifying ? <><LoaderCircle className="animate-spin" size={18} /> Retaining lesson...</> : <><CheckCircle2 size={18} /> Confirm findings & retain lesson</>}
                        </button>
                      )}
                    </div>
                  </section>
                )}
              </>
            )}

            <footer className="flex flex-wrap items-center justify-between gap-2 pb-5 text-[11px] text-slate-600">
              <span>RECALLIX · AI Security Incident Intelligence</span>
              <span className="flex items-center gap-2"><Terminal size={13} /> Every investigation makes the next one smarter.</span>
            </footer>
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
