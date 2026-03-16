import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../style/Login.css";
import background from "../assets/fond.png";

export default function Signup() {

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      alert("Les mots de passe ne correspondent pas");
      return;
    }

    // mock signup
    localStorage.setItem("user", email);

    navigate("/");
  };

  return (
    <div
      className="login-page"
      style={{ backgroundImage: `url(${background})` }}
    >
      <div className="login-card">

        <h2>Inscrivez vous</h2>

        <form onSubmit={handleSubmit}>

          <label>Email</label>
          <input
            type="email"
            placeholder="Exemple@gmail.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <label>Mot de passe</label>
          <input
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <label>Re-confirmer</label>
          <input
            type="password"
            placeholder="••••••••"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />

          <button type="submit">Inscription</button>

        </form>

        <p className="switch">
          <span
            style={{ cursor: "pointer", color: "blue" }}
            onClick={() => navigate("/")}
          >
            Se connecter
          </span>
        </p>

      </div>
    </div>
  );
}