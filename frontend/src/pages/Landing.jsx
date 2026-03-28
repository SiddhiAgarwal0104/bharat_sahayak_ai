import { ArrowRight, ChevronRight, Leaf, Users, Shield, BookOpen, HeartPulse, Home, Wrench, Sprout, Landmark, Scale, Cpu, Plane, Settings, Baby, Trophy, Bus } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import VoiceSearch from '../components/ui/VoiceSearch';

const STATS = [
  { label: 'Total Verified Schemes', value: '4,680+' },
  { label: 'Central Govt Schemes', value: '650+' },
  { label: 'State Specific Schemes', value: '4,000+' },
];

const CATEGORIES = [
  { name: 'Agriculture, Rural & Environment', iconColor: 'text-green-700', icon: Sprout, count: 837 },
  { name: 'Banking, Financial Services and Insurance', iconColor: 'text-amber-600', icon: Landmark, count: 322 },
  { name: 'Business & Entrepreneurship', iconColor: 'text-blue-600', icon: Wrench, count: 736 },
  { name: 'Education & Learning', iconColor: 'text-red-500', icon: BookOpen, count: 1093 },
  { name: 'Health & Wellness', iconColor: 'text-teal-500', icon: HeartPulse, count: 284 },
  { name: 'Housing & Shelter', iconColor: 'text-blue-800', icon: Home, count: 130 },
  { name: 'Public Safety, Law & Justice', iconColor: 'text-orange-700', icon: Scale, count: 32 },
  { name: 'Science, IT & Communications', iconColor: 'text-cyan-600', icon: Cpu, count: 107 },
  { name: 'Skills & Employment', iconColor: 'text-yellow-600', icon: Shield, count: 391 },
  { name: 'Social welfare & Empowerment', iconColor: 'text-orange-500', icon: Users, count: 1468 },
  { name: 'Sports & Culture', iconColor: 'text-lime-600', icon: Trophy, count: 259 },
  { name: 'Transport & Infrastructure', iconColor: 'text-amber-500', icon: Bus, count: 99 },
  { name: 'Travel & Tourism', iconColor: 'text-pink-600', icon: Plane, count: 94 },
  { name: 'Utility & Sanitation', iconColor: 'text-purple-600', icon: Settings, count: 58 },
  { name: 'Women and Child', iconColor: 'text-indigo-600', icon: Baby, count: 463 },
];

export default function Landing() {
  const navigate = useNavigate();
  return (
    <div className="bg-white min-h-screen relative pt-[84px] overflow-hidden">
      
      {/* 1. Hero Section - Cleaner, less green, more vibrant images */}
      <section className="relative w-full pb-24 pt-10 md:pt-16 lg:pt-20 bg-gradient-to-b from-green-50/50 to-white">
        {/* Subtle background grid instead of heavy green */}
        <div className="absolute inset-0 bg-grid-pattern opacity-[0.15] pointer-events-none z-0"></div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 flex flex-col lg:flex-row items-center gap-10">
          
          {/* Text Content */}
          <div className="flex-1 text-center lg:text-left pt-10">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-gray-200 bg-white shadow-sm mb-6">
              <span className="flex h-2.5 w-2.5 rounded-full bg-green-500 animate-pulse"></span>
              <span className="text-xs font-bold text-gray-700 tracking-wide uppercase">Official Portal For Govt Schemes</span>
            </div>
            
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-extrabold text-gray-900 tracking-tight leading-[1.1] mb-6">
              Discover Schemes <br className="hidden md:block"/>
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-green-600 to-emerald-500">
                You Deserve.
              </span>
            </h1>
            
            <p className="text-xl text-gray-600 mb-10 font-medium max-w-2xl mx-auto lg:mx-0 leading-relaxed">
              Find and apply for government schemes in your own language. We make it simple, accessible, and inclusive for everyone.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center gap-4 justify-center lg:justify-start">
              <button 
                onClick={() => navigate('/dashboard')}
                className="w-full sm:w-auto flex items-center justify-center gap-3 bg-green-600 hover:bg-green-700 text-white px-8 py-4 rounded-full font-bold text-lg transition-all duration-300 shadow-lg shadow-green-200 hover:-translate-y-1"
              >
                Find Schemes For You
                <span className="bg-white/20 p-1.5 rounded-full">
                  <ArrowRight className="h-5 w-5" />
                </span>
              </button>
              <button className="w-full sm:w-auto flex items-center justify-center gap-3 bg-white hover:bg-gray-50 text-gray-800 border-2 border-gray-200 px-8 py-4 rounded-full font-bold text-lg transition-all duration-300 shadow-sm hover:-translate-y-1">
                How It Works
              </button>
            </div>
          </div>

          {/* Epic Hero Image Cluster - CLEAR image without heavy green tint */}
          <div className="flex-1 w-full max-w-[550px] lg:max-w-none relative mt-10 lg:mt-0">
            {/* Soft decorative background shape, colored but not overpowering */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[110%] h-[110%] bg-gradient-to-tr from-amber-100 to-green-100 rounded-[3rem] transform rotate-3 z-0"></div>
            
            {/* Main Picture without heavy tint */}
            <div className="relative rounded-[2rem] overflow-hidden border-8 border-white shadow-2xl z-10 bg-gray-100">
              <img 
                src="https://images.pexels.com/photos/10327341/pexels-photo-10327341.jpeg?auto=compress&cs=tinysrgb&w=800" 
                alt="Happy diverse beneficiaries"
                className="w-full h-[450px] object-cover"
              />
              {/* Only a very slight bottom gradient for text readability */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent"></div>
              
              {/* Floating Badge */}
              <div className="absolute bottom-6 left-6 right-6 bg-white/95 backdrop-blur-md rounded-2xl p-4 flex items-center gap-4 shadow-lg border border-gray-100">
                <div className="h-12 w-12 bg-green-100 rounded-full flex items-center justify-center text-green-600 shrink-0">
                  <Shield className="h-6 w-6" />
                </div>
                <div>
                  <h4 className="text-gray-900 font-bold leading-tight">Trusted & Verified</h4>
                  <p className="text-gray-600 text-sm font-medium">All schemes updated directly from Government APIs</p>
                </div>
              </div>
            </div>

            {/* Small decorative floating elements */}
            <div className="absolute -top-6 -right-6 w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-lg border border-gray-50 z-20 animate-bounce" style={{animationDuration: '3s'}}>
              <span className="text-3xl">🇮🇳</span>
            </div>
          </div>
          
        </div>
      </section>

      {/* 2. Stats Section */}
      <section className="relative z-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-8 mb-16">
        <div className="bg-white rounded-[2rem] p-2 md:p-4 shadow-[0_8px_30px_rgb(0,0,0,0.06)] border border-gray-100 flex flex-col md:flex-row items-center divide-y md:divide-y-0 md:divide-x divide-gray-100">
          {STATS.map((stat, i) => (
            <div key={i} className="flex-1 w-full p-6 md:p-8 flex flex-col items-center justify-center hover:bg-green-50/50 transition-colors rounded-2xl">
              <div className="text-4xl font-extrabold text-green-600 mb-2">
                {stat.value}
              </div>
              <div className="text-gray-600 font-bold uppercase tracking-wider text-xs text-center">
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 4. Rich Categories Grid matching provided MyScheme screenshot */}
      <section className="py-20 relative bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-extrabold text-gray-900">Find schemes based on categories</h2>
            <div className="w-24 h-1 bg-green-500 mx-auto mt-4 rounded-full"></div>
          </div>

          {/* 5 column grid on large screens */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-x-6 gap-y-12">
            {CATEGORIES.map((cat, i) => (
              <div 
                key={i}
                className="group flex flex-col items-center text-center cursor-pointer transform hover:-translate-y-1 transition-transform duration-300"
              >
                {/* Icon with light blue blob background */}
                <div className="relative mb-4 flex items-center justify-center w-20 h-20">
                  <div className="absolute inset-0 bg-blue-50 rounded-full scale-[0.8] blur-[2px] transform group-hover:scale-110 group-hover:bg-blue-100 transition-all duration-300 -z-10 translate-y-2 translate-x-1"></div>
                  <cat.icon className={`h-10 w-10 ${cat.iconColor}`} strokeWidth={2} />
                </div>
                
                {/* Scheme Count Label */}
                <div className="flex items-center gap-1 mb-1.5">
                  <span className="text-green-600 font-semibold text-sm">{cat.count}</span>
                  <span className="text-green-600/80 text-xs font-medium">Schemes</span>
                </div>
                
                {/* Title */}
                <h4 className="text-gray-800 font-medium text-sm px-2 leading-tight group-hover:text-green-700 transition-colors">
                  {cat.name}
                </h4>
              </div>
            ))}
          </div>
          
        </div>
      </section>

      <VoiceSearch />

    </div>
  );
}