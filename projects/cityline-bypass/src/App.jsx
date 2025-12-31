import React, { useState, useEffect } from 'react';
import { 
  AlertTriangle, 
  CheckCircle2, 
  Copy, 
  ExternalLink, 
  Info,
  ShieldAlert,
  Loader2,
  Navigation,
  Search,
  Zap
} from 'lucide-react';
const SYRACUSE_LAT = 43.0481;
const SYRACUSE_LNG = -76.1474;

export default function App() {
  const [userInput, setUserInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [apiState, setApiState] = useState('idle'); 
  const [submittableCategories, setSubmittableCategories] = useState([]);
  const [blockedCategories, setBlockedCategories] = useState([]);
  const [result, setResult] = useState(null);
  const [copyFeedback, setCopyFeedback] = useState(false);

  useEffect(() => {
    fetchSyracuseCategories();
  }, []);

  const fetchSyracuseCategories = async () => {
    setApiState('fetching');
    try {
      const url = `https://seeclickfix.com/api/v2/issues/new?lat=${SYRACUSE_LAT}&lng=${SYRACUSE_LNG}`;
      const response = await fetch(url);
      const data = await response.json();
      
      const rawTypes = data.request_types || [];
      
      // Filter exactly by the 'title' field based on the block_submission flag
      const submittable = rawTypes
        .filter(t => t.block_submission === false)
        .map(t => t.title);
      
      const blocked = rawTypes
        .filter(t => t.block_submission === true)
        .map(t => t.title);

      setSubmittableCategories(submittable);
      setBlockedCategories(blocked);
      setApiState('ready');
    } catch (err) {
      console.error("API Audit failed", err);
      setApiState('error');
    }
  };

  const handleTranslate = async () => {
    if (!userInput.trim()) return;
    setLoading(true);
    setResult(null);

    const systemPrompt = `
      You are the "Syracuse Civic Strategist". 
      Your mission is to find an AVAILABLE category from the list below to bypass blocked paths.
      
      STRICT REQUIREMENTS:
      1. You MUST pick a "workaround_category" that exists EXACTLY as written in the SUBMITTABLE list.
      2. The user's intent might match a BLOCKED category. You must find the most effective SUBMITTABLE alternative.
      3. Use the 'title' field provided in the list.

      SUBMITTABLE 'TITLE' LIST (VERIFIED AVAILABLE):
      ${submittableCategories.join(" | ")}

      BLOCKED 'TITLE' LIST (DO NOT USE THESE):
      ${blockedCategories.join(" | ")}

      Respond in JSON:
      {
        "original_intent_blocked": true/false,
        "blocked_category_name": "string",
        "workaround_category": "EXACT TITLE FROM SUBMITTABLE LIST",
        "strategy_reasoning": "Why this specific available category works for this issue",
        "draft_text": "Professional, descriptive text for the user to copy"
      }
    `;

    try {
      const response = await fetch("https://api.datacuse.com/api/gemini", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contents: [{ parts: [{ text: `User Issue: ${userInput}` }] }],
          systemInstruction: { parts: [{ text: systemPrompt }] },
          generationConfig: { responseMimeType: "application/json" }
        })
      });


      const data = await response.json();
      const content = JSON.parse(data.candidates[0].content.parts[0].text);
      
      // Final JS Validation: Ensure the AI didn't hallucinate a category name
      if (!submittableCategories.includes(content.workaround_category)) {
        // Fallback to "Other" or similar if match fails
        const closest = submittableCategories.find(c => c.toLowerCase().includes("other")) || submittableCategories[0];
        content.workaround_category = closest;
      }

      setResult(content);
    } catch (err) {
      console.error("Translation error", err);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    const el = document.createElement('textarea');
    el.value = text;
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
    setCopyFeedback(true);
    setTimeout(() => setCopyFeedback(false), 2000);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans pb-12">
      <header className="bg-white border-b border-slate-200 px-6 py-4 sticky top-0 z-50">
        <div className="max-w-2xl mx-auto flex items-center justify-between">
          <a
            href="https://www.datacuse.com"
            className="flex items-center gap-2 hover:opacity-90 hover:underline underline-offset-4 transition-all"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Back to DataCuse"
          >
            <div className="bg-[#002D62] p-1.5 rounded-md">
              <Zap size={18} className="text-[#F76900]" />
            </div>
            <div>
              <h1 className="text-lg font-black tracking-tight uppercase leading-none text-[#002D62]">
                Cityline Bypass
              </h1>
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">
                Syracuse API Workaround Tool
              </span>
            </div>
          </a>
          
          <div className={`px-3 py-1 rounded-full border text-[10px] font-bold uppercase tracking-wider flex items-center gap-2 ${
            apiState === 'ready' ? 'bg-green-50 border-green-200 text-green-700' : 'bg-slate-100 border-slate-200 text-slate-500'
          }`}>
            {apiState === 'fetching' && <Loader2 size={10} className="animate-spin" />}
            {apiState === 'ready' ? `${submittableCategories.length} Categories Live` : 'Connecting...'}
          </div>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-6 pt-8">
        <section className="bg-white rounded-2xl shadow-sm border-2 border-slate-300 overflow-hidden focus-within:border-[#F76900] focus-within:shadow-lg transition-all">
          <div className="bg-slate-100 px-4 py-2 border-b border-slate-200 flex items-center justify-between">
            <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Describe Your Problem</span>
            <Search size={14} className="text-slate-400" />
          </div>
          <textarea
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="e.g., 'My trash was skipped' or 'Street wasn't plowed'"
            className="w-full h-32 p-4 text-xl font-medium text-slate-800 placeholder-slate-300 resize-none outline-none"
          />
          <div className="p-3 bg-white">
            <button
              onClick={handleTranslate}
              disabled={loading || apiState !== 'ready' || !userInput.trim()}
              className="w-full bg-[#F76900] hover:bg-[#E05E00] disabled:bg-slate-300 text-white font-black py-4 rounded-xl shadow-md transition-all flex items-center justify-center gap-3 uppercase tracking-wider"
            >
              {loading ? (
                <>
                  <Loader2 className="animate-spin" />
                  <span>Auditing Live Paths...</span>
                </>
              ) : (
                <>
                  <Navigation size={20} />
                  <span>Map to Available Category</span>
                </>
              )}
            </button>
          </div>
        </section>

        {result && (
          <div className="mt-8 space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-300">
            <div className="bg-white rounded-2xl shadow-2xl border-2 border-[#002D62] overflow-hidden">
              <div className="bg-[#002D62] p-4 flex items-center justify-between">
                <span className="text-white text-[11px] font-black uppercase tracking-widest flex items-center gap-2">
                  <CheckCircle2 size={16} className="text-green-400" />
                  Select this verified title in Cityline
                </span>
              </div>
              
              <div className="p-8 text-center bg-white border-b border-slate-100">
                <div className="text-sm font-bold text-slate-400 uppercase mb-2">Available Category:</div>
                <div className="text-3xl font-black text-[#002D62] leading-tight">
                  {result.workaround_category}
                </div>
              </div>

              <div className="p-6 bg-slate-50">
                <div className="flex items-start gap-3 text-slate-700 text-sm bg-white p-4 rounded-xl border border-slate-200 shadow-sm mb-6">
                  <Info size={20} className="shrink-0 text-[#F76900]" />
                  <div>
                    <span className="font-bold block text-xs uppercase text-slate-400 mb-1">Reason for Workaround</span>
                    {result.strategy_reasoning}
                  </div>
                </div>

                <div className="relative">
                  <div className="absolute -top-2 left-3 bg-slate-50 px-2 text-[10px] font-black text-slate-400 uppercase tracking-widest z-10">
                    Paste into Description
                  </div>
                  <div className="bg-white border-2 border-dashed border-slate-300 rounded-xl p-5 text-slate-700 text-sm leading-relaxed min-h-[100px] pt-6 italic relative shadow-inner">
                    {result.draft_text}
                  </div>
                  <button 
                    onClick={() => copyToClipboard(result.draft_text)}
                    className="absolute top-4 right-2 p-2 bg-slate-100 hover:bg-[#F76900] hover:text-white rounded-lg transition-all flex items-center gap-2 border border-slate-200 group"
                  >
                    {copyFeedback ? (
                      <span className="text-[10px] font-bold px-2">COPIED</span>
                    ) : (
                      <Copy size={16} />
                    )}
                  </button>
                </div>
              </div>

              <div className="p-4 bg-white flex gap-3">
                <a 
                  href="https://seeclickfix.com/syracuse" 
                  target="_blank" 
                  rel="noreferrer"
                  className="flex-1 py-4 bg-[#F76900] hover:bg-[#E05E00] text-white rounded-xl font-black flex items-center justify-center gap-2 transition-all shadow-lg uppercase tracking-tighter"
                >
                  Go to Syracuse Cityline <ExternalLink size={18} />
                </a>
              </div>
            </div>

            {result.original_intent_blocked && (
              <div className="bg-orange-100 border border-orange-200 p-4 flex gap-3 items-center rounded-xl">
                <ShieldAlert className="text-orange-600 shrink-0" size={20} />
                <p className="text-orange-900 text-xs font-bold">
                  The standard "{result.blocked_category_name}" path is restricted. This alternative is currently open.
                </p>
              </div>
            )}
          </div>
        )}

        {blockedCategories.length > 0 && (
          <div className="mt-12 p-6 bg-white rounded-2xl border border-slate-200">
            <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-2">
              <AlertTriangle size={12} className="text-orange-400" />
              API Restriction Log: Currently Blocked 'Titles'
            </h3>
            <div className="flex flex-wrap gap-2">
              {blockedCategories.slice(0, 20).map((cat, i) => (
                <div key={i} className="px-2 py-1 bg-slate-50 border border-slate-200 text-slate-400 text-[9px] font-bold rounded-md line-through opacity-60">
                  {cat}
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      <footer className="mt-12 text-center text-slate-400 text-[10px] font-medium px-6 py-8">
        <p>© {new Date().getFullYear()} CITYLINE BYPASS SYRACUSE</p>
        <p className="mt-1 opacity-60">Real-time audit of Syracuse Cityline request_types via SeeClickFix API.</p>
      </footer>
    </div>
  );
}