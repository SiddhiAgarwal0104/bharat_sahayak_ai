import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mic, Search, X, Volume2, Loader2, StopCircle } from 'lucide-react';
import { useVoice } from '../../hooks/useVoice';
import { queryAudio } from '../../api/api';
import { useAuth } from '../../context/AuthContext';
import { tr } from '../../utils/i18n';

export default function VoiceSearch({ isDashboard = false }) {
  const navigate = useNavigate();
  const { user } = useAuth();
  const lang = user?.language_pref || "en";
  const { recording, start, stop, getBlob, reset } = useVoice();
  const [transcript, setTranscript] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  // Sound bars simulation
  const [bars, setBars] = useState(Array(12).fill(10));

  useEffect(() => {
    let interval;
    if (recording) {
      interval = setInterval(() => {
        setBars(prev => prev.map(() => 10 + Math.random() * 40));
      }, 100);
    } else {
      setBars(Array(12).fill(10));
    }
    return () => clearInterval(interval);
  }, [recording]);

  const handleMicClick = async () => {
    if (recording) {
      stop();
      setIsProcessing(true);
      setErrorMsg(null);
      try {
        const blob = await getBlob();
        if (!blob || blob.size === 0) throw new Error("Audio empty");
        
        const res = await queryAudio(blob, lang);
        setTranscript(res.data?.text || "");
      } catch (err) {
        setErrorMsg(tr(lang, "search.error"));
      } finally {
        setIsProcessing(false);
        reset();
      }
    } else {
      setTranscript('');
      setErrorMsg(null);
      await start();
    }
  };

  const clearTranscript = () => {
    setTranscript('');
    setErrorMsg(null);
  };

  const handleSearch = () => {
    if (transcript.trim()) {
      navigate('/search', { state: { query: transcript.trim() } });
    }
  };

  const contentClass = isDashboard 
    ? "relative py-6 md:py-10 mb-8 isolate"
    : "relative py-32 overflow-hidden bg-gradient-to-br from-green-950 via-green-900 to-[#042f15] isolate";
    
  const titleText = isDashboard ? tr(lang, "dashboard.searchTitle") : "Speak. We'll find the";
  const titleSpan = isDashboard ? "" : "perfect scheme.";

  return (
    <section className={contentClass}>
      {/* Abstract Backgrounds for General Landing */}
      {!isDashboard && (
        <div className="absolute inset-0 bg-[url('https://images.pexels.com/photos/3183153/pexels-photo-3183153.jpeg?auto=compress&cs=tinysrgb&w=1920')] bg-cover bg-center opacity-5 mix-blend-screen z-[-2]"></div>
      )}
      
      {!isDashboard && (
        <>
          <div className="absolute top-[-20%] left-[-10%] w-[60%] h-[150%] bg-emerald-600/20 rounded-full blur-[180px] pointer-events-none z-[-1]"></div>
          <div className="absolute bottom-[-20%] right-[-10%] w-[40%] h-[120%] bg-green-500/20 rounded-[100px] rotate-45 blur-[150px] pointer-events-none z-[-1]"></div>
        </>
      )}

      {isDashboard && (
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-4xl h-[120%] bg-emerald-400/10 rounded-full blur-[120px] pointer-events-none z-[-1]"></div>
      )}

      <div className={`${isDashboard ? 'px-2 md:px-6' : 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'} relative z-10`}>
        
        {!isDashboard && (
          <div className="text-center mb-16 relative">
            <div className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-white/5 border border-white/10 shadow-sm backdrop-blur-md mb-8 ring-1 ring-white/20 text-emerald-200 uppercase tracking-widest text-sm font-bold">
              <Volume2 className="h-4 w-4 animate-pulse" /> Multilingual AI Voice Assistant
            </div>
            <h2 className="text-5xl md:text-7xl font-black text-white mb-6 drop-shadow-xl leading-tight">
              {titleText} <br/>
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-300 via-green-300 to-teal-200">{titleSpan}</span>
            </h2>
            <p className="text-xl md:text-2xl text-green-100 max-w-3xl mx-auto font-medium drop-shadow-md">
              Skip the complicated forms. Just tell our AI what you need in English, Hindi, Tamil, or your native language!
            </p>
          </div>
        )}

        {isDashboard && (
          <div className="text-center mb-8 relative">
            <h2 className="text-3xl md:text-4xl font-black text-green-950 mb-3 drop-shadow-sm">
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-600 to-green-600">
                {titleText}
              </span>
            </h2>
            <p className="text-lg text-green-800 font-bold max-w-xl mx-auto opacity-90 drop-shadow-sm">
              {tr(lang, "dashboard.searchSubtitle")}
            </p>
          </div>
        )}

        {/* Feature Highlight Card Container */}
        <div className="max-w-4xl mx-auto relative z-10">
          <div className={`relative rounded-[3rem] p-[3px] ${isDashboard ? 'bg-gradient-to-r from-white/80 via-white/40 to-white/80 shadow-[0_20px_60px_-15px_rgba(22,163,74,0.15)]' : 'bg-gradient-to-r from-green-400/30 via-emerald-200/50 to-teal-400/30 shadow-2xl'} overflow-visible`}>
            
            {/* Inner Glass Card */}
            <div className={`relative ${isDashboard ? 'bg-white/60 border-white/80' : 'bg-black/30 border-white/10 shadow-[0_20px_80px_rgba(0,0,0,0.5)]'} backdrop-blur-2xl rounded-[calc(3rem-3px)] p-6 md:p-10 border overflow-hidden`}>
              
              {isDashboard ? ( // Light delicate background elements for dashboard
                <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-green-200/40 rounded-full blur-[90px] -mr-40 -mt-20 mix-blend-multiply pointer-events-none"></div>
              ) : (
                <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-green-500/10 rounded-full blur-[100px] -mr-40 -mt-40 mix-blend-screen pointer-events-none"></div>
              )}
              
              <div className="relative z-10 flex flex-col md:flex-row items-center gap-10">
                
                {/* Visual Mic Focus */}
                <div className={`${isDashboard ? 'scale-95' : ''} flex-shrink-0 relative group`}>
                  {/* Glowing Rings */}
                  <div className={`absolute inset-[-60px] border-[2px] ${isDashboard ? 'border-green-400/30 group-hover:border-green-400/60' : 'border-emerald-400/20 group-hover:border-emerald-300/50'} rounded-full animate-[spin_10s_linear_infinite] transition-colors`}></div>
                  <div className={`absolute inset-[-100px] border-[1px] ${isDashboard ? 'border-green-300/20 group-hover:border-green-300/40' : 'border-green-300/10 group-hover:border-green-300/30'} rounded-full animate-[spin_15s_reverse_linear_infinite] transition-colors`}></div>
                  
                  {recording && (
                    <div className="absolute inset-0 bg-red-500/20 rounded-full animate-ping blur-md"></div>
                  )}
                  
                  <button
                    onClick={handleMicClick}
                    disabled={isProcessing}
                    className={`relative z-10 w-32 h-32 md:w-36 md:h-36 rounded-full flex items-center justify-center transition-all duration-500 shadow-[0_0_50px_rgba(16,185,129,0.3)] border-[5px] backdrop-blur-sm ${
                      recording 
                        ? 'bg-red-500 border-red-300 scale-110 shadow-[0_0_70px_rgba(239,68,68,0.6)]' 
                        : isProcessing
                        ? 'bg-emerald-700/50 border-emerald-500/50 cursor-not-allowed'
                        : isDashboard
                        ? 'bg-gradient-to-br from-green-500 to-emerald-600 hover:from-green-400 hover:to-emerald-500 hover:scale-105 border-white/60 shadow-[0_15px_35px_rgba(22,163,74,0.3)]'
                        : 'bg-gradient-to-br from-green-500 to-emerald-700 hover:from-green-400 hover:to-emerald-600 hover:scale-105 border-white/20'
                    }`}
                  >
                    {isProcessing ? (
                      <Loader2 className={`h-14 w-14 md:h-16 md:w-16 ${isDashboard ? 'text-white' : 'text-emerald-200'} animate-spin`} />
                    ) : recording ? (
                      <StopCircle className="h-14 w-14 md:h-16 md:w-16 text-white animate-pulse" />
                    ) : (
                      <Mic className={`h-14 w-14 md:h-16 md:w-16 ${isDashboard ? 'text-white' : 'text-emerald-50'}`} />
                    )}
                  </button>

                  <p className={`absolute -bottom-10 left-1/2 -translate-x-1/2 ${isDashboard ? 'text-green-800' : 'text-emerald-100'} font-bold tracking-widest uppercase text-xs whitespace-nowrap drop-shadow-sm`}>
                    {isProcessing ? "Transcribing..." : recording ? "Listening..." : "Tap Mic"}
                  </p>
                </div>

                {/* Input & Action Section */}
                <div className="flex-1 w-full space-y-5 relative mt-12 md:mt-0">
                  
                  {/* Audio Visualizer */}
                  <div className={`flex items-end justify-center gap-1.5 h-12 transition-all duration-500 ${recording ? 'opacity-100' : 'opacity-0 h-0 overflow-hidden'}`}>
                    {bars.map((height, i) => (
                      <div key={i} className={`w-2 rounded-t-sm ${isDashboard ? 'bg-gradient-to-t from-green-500 to-emerald-400' : 'bg-gradient-to-t from-green-400 to-emerald-200'}`} style={{ height: `${height}px`, transition: 'height 0.1s ease' }}></div>
                    ))}
                  </div>

                  <div className="relative rounded-3xl group transition-all duration-300">
                    <div className={`absolute inset-0 bg-gradient-to-r from-emerald-500 to-green-500 rounded-3xl blur ${isDashboard ? 'opacity-20 group-hover:opacity-30' : 'opacity-30 group-hover:opacity-50'} transition-opacity`}></div>
                    <textarea
                      value={transcript}
                      onChange={(e) => setTranscript(e.target.value)}
                      placeholder={recording ? "Listening..." : tr(lang, "dashboard.searchSubtitle")}
                      rows={isDashboard ? 2 : 3}
                      disabled={recording || isProcessing}
                      className={`relative w-full ${isDashboard ? 'bg-white/80 border-white/80' : 'bg-white/95 border-white/60'} backdrop-blur-xl border-2 text-emerald-950 ${isDashboard ? 'text-xl' : 'text-xl md:text-2xl'} rounded-[1.5rem] p-5 pr-14 focus:outline-none focus:ring-4 focus:ring-emerald-400/30 focus:bg-white focus:border-emerald-400 transition-all resize-none shadow-[0_8px_30px_rgba(22,163,74,0.1)] placeholder-emerald-900/40 font-bold disabled:opacity-80 disabled:cursor-not-allowed`}
                    />
                    {transcript && !recording && !isProcessing && (
                      <button 
                        onClick={clearTranscript}
                        className={`absolute top-5 right-5 ${isDashboard ? 'text-green-600/60 hover:text-green-700 bg-green-50 hover:bg-green-100' : 'text-emerald-600/50 hover:text-emerald-600 bg-emerald-50 hover:bg-emerald-100'} p-2 rounded-full transition-all border border-transparent shadow-sm`}
                      >
                        <X className="h-5 w-5 font-bold" />
                      </button>
                    )}
                  </div>

                  {errorMsg && (
                    <div className="text-red-500 font-bold text-sm text-center px-4 bg-red-50/80 rounded-2xl py-3 border border-red-200/50 backdrop-blur-sm shadow-sm">
                      {errorMsg}
                    </div>
                  )}
                  
                  <div className="flex gap-4 w-full pt-1">
                    <button 
                      onClick={handleSearch}
                      disabled={!transcript.trim() || recording || isProcessing}
                      className={`flex-1 flex justify-center items-center gap-3 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white px-8 py-4 rounded-2xl font-black text-lg transition-all duration-300 shadow-[0_10px_25px_rgba(22,163,74,0.3)] hover:shadow-[0_15px_35px_rgba(22,163,74,0.4)] hover:-translate-y-0.5 active:scale-95 disabled:scale-100 disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none disabled:translate-y-0`}
                    >
                      <Search className="h-6 w-6" />
                      {tr(lang, "search.searchBtn")}
                    </button>
                  </div>
                </div>

              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
