import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Search, Globe, LogIn, Menu, User, LayoutDashboard, LogOut } from "lucide-react";
import { useAuth } from "../../context/AuthContext";

export default function Navbar() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <nav className="fixed w-full top-0 z-50 bg-white/80 backdrop-blur-xl border-b border-green-100/50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-[84px] items-center">
          
          {/* Logo Section */}
          <Link to="/" className="flex items-center gap-4 group">
            <div className="relative">
              <div className="absolute inset-0 bg-green-400 rounded-full blur-md opacity-30 group-hover:opacity-60 transition-opacity"></div>
              <div className="w-12 h-12 rounded-full flex items-center justify-center relative shadow-[0_4px_15px_rgba(0,0,0,0.1)] transform group-hover:scale-105 transition-transform duration-300 overflow-hidden border-[2.5px] border-white bg-gradient-to-b from-[#FF9933] via-white to-[#138808]">
                {/* Ashoka Chakra SVG */}
                <svg className="w-4 h-4 text-[#000080]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.2">
                  <circle cx="12" cy="12" r="10" />
                  <path d="M12 2v20M2 12h20M4.93 4.93l14.14 14.14M4.93 19.07L19.07 4.93M8.46 3.54l7.08 16.92M3.54 8.46l16.92 7.08M3.54 15.54l16.92-7.08M8.46 20.46l7.08-16.92" />
                </svg>
              </div>
            </div>
            <div>
              <div className="font-extrabold text-2xl text-green-900 tracking-tight leading-none drop-shadow-sm">SahayakAI</div>
              <div className="text-sm font-semibold text-green-700 mt-0.5">सरकारी योजना सहायक</div>
            </div>
          </Link>

          {/* Right Section */}
          <div className="hidden md:flex items-center gap-5">
            
            {/* Search Bar */}
            <div className="relative group">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <Search className="h-4 w-4 text-green-600/50 group-focus-within:text-green-600 transition-colors" />
              </div>
              <input
                type="text"
                placeholder="Search schemes..."
                onKeyDown={(e) => {
                  if(e.key === 'Enter' && e.target.value.trim()) {
                    navigate('/search', { state: { query: e.target.value.trim() } });
                  }
                }}
                className="block w-72 pl-11 pr-4 py-2.5 border border-green-200 bg-white/60 backdrop-blur-sm rounded-full leading-5 text-green-950 placeholder-green-800/40 focus:outline-none focus:bg-white focus:ring-4 focus:ring-green-500/20 focus:border-green-500 transition-all duration-300 shadow-[0_4px_12px_rgba(22,163,74,0.04)] hover:shadow-md font-medium"
              />
            </div>

            {/* Language Toggle */}
            <button className="flex items-center gap-2 text-green-800 hover:text-green-900 transition-all py-2.5 px-4 rounded-full bg-green-50/80 hover:bg-green-100 border border-green-200/50 shadow-sm hover:shadow font-bold">
              <Globe className="h-5 w-5 text-green-600" />
              <span className="text-sm tracking-wide">EN | हिंदी</span>
            </button>

            {/* Auth State */}
            {!user ? (
              <div className="flex items-center gap-3">
                <button 
                  onClick={() => navigate('/login')}
                  className="flex items-center gap-2 text-green-700 hover:text-green-800 bg-white hover:bg-green-50 px-6 py-2.5 rounded-full font-bold transition-all border border-green-200 shadow-sm hover:shadow"
                >
                  Log In
                </button>
                <button 
                  onClick={() => navigate('/register')}
                  className="relative flex items-center gap-2 overflow-hidden bg-gradient-to-r from-green-600 to-green-500 hover:from-green-700 hover:to-green-600 text-white px-7 py-2.5 rounded-full font-bold transition-all duration-300 shadow-[0_4px_16px_rgba(22,163,74,0.3)] hover:shadow-[0_8px_24px_rgba(22,163,74,0.4)] active:scale-95 group"
                >
                  <span className="relative z-10">Sign Up Free</span>
                </button>
              </div>
            ) : (
              <div className="relative group ml-2">
                <button className="flex items-center gap-3 py-1.5 pl-3 pr-4 rounded-full bg-green-50 border border-green-200 hover:bg-green-100 hover:border-green-300 transition-all shadow-sm">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center text-white font-bold text-sm shadow-inner">
                    {user.name ? user.name.charAt(0).toUpperCase() : <User className="h-4 w-4" />}
                  </div>
                  <span className="text-green-950 font-bold text-sm max-w-[100px] truncate">
                    {user.name || "User"}
                  </span>
                </button>

                {/* Dropdown menu */}
                <div className="absolute right-0 mt-2 w-56 bg-white rounded-2xl shadow-[0_20px_60px_-15px_rgba(0,0,0,0.1)] border border-green-100 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 transform origin-top-right scale-95 group-hover:scale-100 z-50 overflow-hidden">
                  <div className="p-2 space-y-1 relative">
                    <Link to="/dashboard" className="flex items-center gap-3 px-4 py-3 bg-white hover:bg-green-50 rounded-xl text-green-900 font-semibold transition-colors">
                      <LayoutDashboard className="h-5 w-5 text-green-600" /> Dashboard
                    </Link>
                    <Link to="/profile" className="flex items-center gap-3 px-4 py-3 bg-white hover:bg-green-50 rounded-xl text-green-900 font-semibold transition-colors">
                      <User className="h-5 w-5 text-green-600" /> My Profile
                    </Link>
                    <div className="h-px bg-green-100 my-1 mx-2"></div>
                    <button onClick={handleLogout} className="flex items-center gap-3 px-4 py-3 bg-white hover:bg-red-50 text-red-600 font-semibold rounded-xl w-full text-left transition-colors">
                      <LogOut className="h-5 w-5" /> Sign Out
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Mobile Menu Button - TODO */}
        </div>
      </div>
    </nav>
  );
}