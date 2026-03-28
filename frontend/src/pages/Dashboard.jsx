import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowRight, Filter, Search, ShieldCheck, Sparkles, Loader2 } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { getRecommended } from "../api/api";
import { tr } from "../utils/i18n";
import VoiceSearch from "../components/ui/VoiceSearch";

const getSchemeImage = (title, category) => {
  const t = (title + " " + category).toLowerCase();
  if (t.includes("farm") || t.includes("kisan") || t.includes("krishi")) return "https://images.pexels.com/photos/10327341/pexels-photo-10327341.jpeg?auto=compress&cs=tinysrgb&w=600";
  if (t.includes("awas") || t.includes("house") || t.includes("home")) return "https://images.pexels.com/photos/106399/pexels-photo-106399.jpeg?auto=compress&cs=tinysrgb&w=600";
  if (t.includes("health") || t.includes("ayushman") || t.includes("medical")) return "https://images.pexels.com/photos/4386466/pexels-photo-4386466.jpeg?auto=compress&cs=tinysrgb&w=600";
  if (t.includes("business") || t.includes("mudra") || t.includes("finance")) return "https://images.pexels.com/photos/6863515/pexels-photo-6863515.jpeg?auto=compress&cs=tinysrgb&w=600";
  if (t.includes("education") || t.includes("scholar") || t.includes("vidya")) return "https://images.pexels.com/photos/4050291/pexels-photo-4050291.jpeg?auto=compress&cs=tinysrgb&w=600";
  return "https://images.pexels.com/photos/1598075/pexels-photo-1598075.jpeg?auto=compress&cs=tinysrgb&w=600"; 
};

export default function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const lang = user?.language_pref || "en";
  
  const [schemes, setSchemes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    const fetchSchemes = async () => {
      try {
        const res = await getRecommended();
        const data = res.data?.schemes || res.data || [];
        setSchemes(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error("Failed to fetch recommended schemes:", err);
      } finally {
        setLoading(false);
      }
    };
    if (user) {
      fetchSchemes();
    } else {
      setLoading(false);
    }
  }, [user]);

  const filteredSchemes = schemes.filter(s => 
    s.name?.toLowerCase().includes(searchQuery.toLowerCase()) || 
    s.category?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="bg-[#f0fdf4] min-h-screen pb-20 pt-[100px] relative">
      
      {/* Background elements */}
      <div className="absolute top-0 left-0 w-full h-[400px] bg-gradient-to-b from-green-100 to-[#f0fdf4] pointer-events-none z-0"></div>
      <div className="absolute top-20 right-10 w-[400px] h-[400px] bg-emerald-300/20 rounded-full blur-[120px] pointer-events-none z-0"></div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Render the Voice Search Assistant directly in the Dashboard */}
        <VoiceSearch isDashboard={true} />
        
        {/* Header Area for Recommendations */}
        <div className="bg-white/80 backdrop-blur-xl rounded-[2.5rem] p-8 md:p-10 mb-12 shadow-[0_20px_60px_-15px_rgba(22,163,74,0.15)] flex flex-col md:flex-row md:items-end justify-between gap-8 border border-white mt-4">
          <div className="flex-1">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-green-100 to-emerald-100 border border-green-200 text-green-800 text-xs font-black uppercase tracking-widest mb-4 shadow-sm">
              <Sparkles className="h-4 w-4 text-green-600" /> 
              {tr(lang, "dashboard.greeting", { name: user?.name?.split(' ')[0] || tr(lang, "dashboard.greetingFallback") })}
            </div>
            <h1 className="text-4xl md:text-5xl font-black text-green-950 mb-3 drop-shadow-sm tracking-tight">
              {tr(lang, "dashboard.recommended")}
            </h1>
            <p className="text-xl text-green-800/80 font-medium max-w-2xl">
              {tr(lang, "dashboard.subtitle")}
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-center gap-3 w-full md:w-auto">
            <div className="relative w-full sm:w-[320px] group">
              <div className="absolute inset-y-0 left-0 pl-5 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-green-600/50 group-focus-within:text-green-600 transition-colors" />
              </div>
              <input 
                type="text" 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder={tr(lang, "dashboard.searchSchemes")}
                className="w-full pl-12 pr-5 py-4 bg-white border-2 border-green-100 rounded-2xl focus:outline-none focus:bg-white focus:border-green-500 focus:ring-4 focus:ring-green-500/20 transition-all font-medium text-green-950 placeholder-green-800/40 shadow-sm"
              />
            </div>
          </div>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 text-green-600">
            <Loader2 className="h-12 w-12 animate-spin mb-4" />
            <h3 className="text-2xl font-bold">Analyzing your profile...</h3>
          </div>
        ) : filteredSchemes.length === 0 ? (
          <div className="bg-white/60 backdrop-blur-md border border-green-100 rounded-3xl p-16 text-center shadow-lg">
            <div className="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <ShieldCheck className="h-12 w-12 text-green-600" />
            </div>
            <h3 className="text-3xl font-black text-green-950 mb-4">{tr(lang, "dashboard.noRecommendations")}</h3>
            <button onClick={() => navigate('/search')} className="bg-gradient-to-r from-green-600 to-green-500 text-white px-8 py-4 rounded-2xl font-bold hover:shadow-lg transition-all active:scale-95 mt-4">
              {tr(lang, "dashboard.searchSchemes")}
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-8 lg:gap-10">
            {filteredSchemes.map((scheme, idx) => (
              <div 
                key={scheme.id || idx}
                className="group bg-white rounded-[2.5rem] p-4 shadow-[0_10px_30px_rgba(22,163,74,0.08)] hover:shadow-[0_20px_50px_rgba(22,163,74,0.2)] transition-all duration-500 border border-green-100 flex flex-col overflow-hidden"
              >
                {/* Custom Card logic mapped to scheme data... */}
                <div className="relative rounded-[2rem] overflow-hidden h-[240px] mb-6 border border-green-50 bg-green-50">
                  <div className="absolute inset-0 bg-green-900/10 group-hover:bg-transparent transition-colors duration-500 z-10 mix-blend-overlay"></div>
                  <img 
                    src={getSchemeImage(scheme.name, scheme.category)} 
                    alt={scheme.name} 
                    className="w-full h-full object-cover transform scale-100 group-hover:scale-110 transition-transform duration-700 ease-in-out"
                  />
                  
                  <div className="absolute top-4 left-4 z-20 flex flex-wrap gap-2">
                    <span className="px-4 py-2 bg-white/95 backdrop-blur-md text-green-900 text-xs font-black uppercase tracking-widest rounded-xl shadow-lg border border-green-100 flex items-center gap-2">
                      <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse"></span>
                      {scheme.category || "General"}
                    </span>
                  </div>
                  
                  <div className="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-white to-transparent z-10"></div>
                </div>

                <div className="px-4 pb-4 flex-1 flex flex-col relative z-20">
                  <h3 className="text-2xl font-black text-gray-900 mb-3 leading-tight group-hover:text-green-700 transition-colors">
                    {scheme.name}
                  </h3>
                  <p className="text-gray-600 font-medium text-lg leading-relaxed mb-8 flex-1 line-clamp-3">
                    {scheme.description || "A government initiative designed to provide financial independence and support to eligible beneficiaries across sectors."}
                  </p>

                  <div className="flex items-center justify-between pt-5 border-t-2 border-green-50">
                    <div className="flex items-center gap-3">
                      <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-green-100 to-emerald-50 border border-green-200 flex items-center justify-center shadow-inner">
                        <ShieldCheck className="h-6 w-6 text-green-600" />
                      </div>
                      <div className="flex flex-col">
                        <span className="text-[11px] font-black text-green-600 uppercase tracking-widest leading-none mb-1">Status</span>
                        <span className="text-base font-bold text-gray-900 leading-none">{tr(lang, "scheme.eligible")}</span>
                      </div>
                    </div>
                    
                    <button onClick={() => navigate(`/scheme/${scheme.id}`)} className="flex items-center gap-2 text-white bg-gradient-to-br from-green-600 to-emerald-600 px-6 py-3.5 rounded-2xl font-bold transition-all duration-300 shadow-[0_8px_20px_rgba(22,163,74,0.3)] hover:shadow-[0_12px_25px_rgba(22,163,74,0.4)] hover:-translate-y-0.5 active:scale-95 group/btn">
                      View
                      <span className="bg-white/20 p-1.5 rounded-full group-hover/btn:translate-x-1 transition-transform">
                        <ArrowRight className="h-4 w-4" />
                      </span>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  );
}