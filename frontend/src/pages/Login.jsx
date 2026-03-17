import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authApi } from "../services/api";
import logo from "../assets/logo.png";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [isSignUp, setIsSignUp] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!email || !password) {
      setError("Veuillez remplir tous les champs");
      return;
    }

    setLoading(true);
    try {
      if (isSignUp) {
        // Register then auto-login
        await authApi.register(email, password);
      }

      // Login (works for both flows)
      const res = await authApi.login(email, password);
      const data = res.data;

      localStorage.setItem("token", data.access_token);
      if (remember) localStorage.setItem("user", data.user.email);

      navigate("/dashboard");
    } catch (err) {
      const msg = err.response?.data?.detail || "Erreur serveur. Vérifie que ton backend est lancé !";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-background-light dark:bg-background-dark text-slate-900 dark:text-slate-100 min-h-screen flex items-center justify-center p-0 sm:p-4 font-display">
      <div className="flex flex-col lg:flex-row w-full max-w-6xl min-h-[85vh] bg-white dark:bg-slate-900 rounded-none lg:rounded-2xl shadow-2xl overflow-hidden">
        {/* Left Pane: Visual/Branding */}
        <div className="hidden lg:flex lg:w-5/12 relative flex-col justify-between p-12 bg-primary overflow-hidden">
          {/* Background Graphic */}
          <div className="absolute inset-0 opacity-10 pointer-events-none">
            <svg className="w-full h-full" preserveAspectRatio="none" viewBox="0 0 100 100">
              <defs>
                <pattern height="10" id="grid" patternUnits="userSpaceOnUse" width="10">
                  <path d="M 10 0 L 0 0 0 10" fill="none" stroke="white" strokeWidth="0.5"></path>
                </pattern>
              </defs>
              <rect fill="url(#grid)" height="100" width="100"></rect>
            </svg>
          </div>
          
          <div className="relative z-10">
            <div className="flex items-center gap-3 text-white">
              <div className="w-10 h-10 bg-white rounded-lg overflow-hidden flex items-center justify-center">
                <img src="/src/assets/logo.png" alt="LynxIA Logo" className="w-full h-full object-contain" />
              </div>
              <span className="text-2xl font-bold tracking-tight">LynxIA</span>
            </div>
          </div>
          
          <div className="relative z-10">
            <h1 className="text-4xl font-extrabold text-white leading-tight mb-6">
              Smarter <br /><span className="text-blue-200">intelligence.</span>
            </h1>
            <p className="text-blue-100 text-lg max-w-md leading-relaxed opacity-90">
              Advanced AI for enterprise-grade document analysis and security.
            </p>
            
            <div className="mt-12 bg-white/10 backdrop-blur-md border border-white/20 p-6 rounded-xl max-w-sm">
              <p className="text-white italic text-sm mb-4">"LynxIA reduced our manual processing time by over 80%."</p>
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-blue-400"></div>
                <div>
                  <p className="text-white font-semibold text-xs">Sarah Chen</p>
                  <p className="text-blue-200 text-[10px] uppercase tracking-wider">CTO, FinTech Global</p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="relative z-10 text-blue-200 text-[11px] flex justify-between opacity-70">
            <span>© 2024 LynxIA Inc.</span>
            <div className="flex gap-4">
              <a className="hover:text-white" href="#">Privacy</a>
              <a className="hover:text-white" href="#">Terms</a>
            </div>
          </div>
        </div>

        {/* Right Pane: Form Area */}
        <div className="w-full lg:w-7/12 flex flex-col p-8 md:p-12 lg:p-16 justify-center">
          <div className="max-w-sm mx-auto w-full">
            {/* Mobile Header */}
            <div className="flex lg:hidden items-center gap-3 mb-8">
              <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
                <img src="/src/assets/logo.png" alt="LynxIA Logo" className="w-full h-full object-contain" />
              </div>
              <h2 className="text-slate-900 dark:text-white text-xl font-bold">LynxIA</h2>
            </div>
            
            <div className="text-center lg:text-left mb-6">
              <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">
                {isSignUp ? "Create an account" : "Welcome back"}
              </h2>
            </div>

            {/* Form */}
            <form className="space-y-4" onSubmit={handleSubmit}>
              <div>
                <input 
                  type="email" 
                  placeholder="Email" 
                  required 
                  className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800/50 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent transition-all outline-none text-sm border-transparent"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              
              <div>
                <div className="relative">
                  <input 
                    type={showPassword ? "text" : "password"}
                    placeholder="Password" 
                    required 
                    className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800/50 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent transition-all outline-none text-sm border-transparent"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                  <button 
                    type="button" 
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                  >
                    <span className="material-symbols-outlined text-[18px]">
                      {showPassword ? "visibility_off" : "visibility"}
                    </span>
                  </button>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <input 
                    type="checkbox" 
                    id="remember" 
                    className="w-3.5 h-3.5 rounded text-primary border-slate-300 dark:border-slate-700 dark:bg-slate-800 focus:ring-primary"
                    checked={remember}
                    onChange={(e) => setRemember(e.target.checked)}
                  />
                  <label htmlFor="remember" className="text-xs text-slate-500 dark:text-slate-400 cursor-pointer">Remember me</label>
                </div>
                <a href="#" className="text-xs font-semibold text-primary hover:underline">Forgot password?</a>
              </div>
              
              {error && <p className="text-red-500 text-sm font-bold mt-2">{error}</p>}

              <button 
                type="submit"
                disabled={loading}
                className="w-full bg-primary hover:bg-primary/95 text-white font-semibold py-3.5 rounded-lg shadow-lg shadow-primary/10 transition-all transform active:scale-[0.99] mt-2 disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {loading ? "Chargement..." : (isSignUp ? "Sign up" : "Sign in")}
              </button>
            </form>
            <p className="mt-8 text-center text-slate-500 dark:text-slate-400 text-sm">
              {isSignUp ? "Already have an account?" : "New to LynxIA?"}{" "}
              <span 
                onClick={() => {
                  setIsSignUp(!isSignUp);
                  setError("");
                }} 
                className="text-primary font-bold hover:underline cursor-pointer"
              >
                {isSignUp ? "Sign in" : "Sign up"}
              </span>
            </p>
            
            <div className="mt-12 flex items-center justify-center gap-2 text-slate-300 dark:text-slate-600">
              <span className="material-symbols-outlined text-[14px]">lock</span>
              <span className="text-[9px] uppercase tracking-[0.2em] font-bold">Secure SSL Connection</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}