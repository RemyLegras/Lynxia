// src/pages/Login.jsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../style/Login.css";
import background from "../assets/fond.png"; // image correctement importée
import { FaEye, FaEyeSlash } from "react-icons/fa";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(false);
  const [showPassword, setShowPassword] = useState(false); // pour afficher le mot de passe
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    // MOCK authentication
    localStorage.setItem("user", email);
    navigate("/dashboard");
  };

  return (
    <div
      className="login-page"
      style={{ backgroundImage: `url(${background})` }}
    >
      <div className="login-card">
        <h2>Identifiez-vous</h2>
        <form onSubmit={handleSubmit}>
          <label>Email</label>
          <input
            type="email"
            placeholder="Exemple@gmail.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <label>Mot de passe</label>
          <div className="password-wrapper">
            <input
              type={showPassword ? "text" : "password"}
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <span
              className="eye-icon"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? <FaEyeSlash /> : <FaEye />}
            </span>
          </div>

          <div className="remember">
            <input
              type="checkbox"
              checked={remember}
              onChange={(e) => setRemember(e.target.checked)}
            />
            <span>Se souvenir de moi</span>
          </div>

          <button type="submit">Connecter</button>
        </form>

        <p className="switch">
          <span
            style={{ cursor: "pointer", color: "blue" }}
            onClick={() => navigate("/signup")}
          >
            Créez un compte
          </span>
        </p>
      </div>
    </div>
  );
}