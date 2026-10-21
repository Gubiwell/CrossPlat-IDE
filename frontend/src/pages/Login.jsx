import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { errorMessage } from '../services/api';

// RF02 - Login
export default function Login({ onGoToRegister }) {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [erro, setErro] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    setErro('');
    try {
      await login(email, senha);
    } catch (err) {
      setErro(errorMessage(err, 'Não foi possível entrar.'));
    }
  }

  return (
    <div className="auth-page">
      <form className="card" onSubmit={handleSubmit}>
        <h1 className="logo"><span className="dot" /> CROSSPLAT</h1>
        {erro && <p className="error">{erro}</p>}

        <label>E-mail
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label>Senha
          <input type="password" value={senha} onChange={(e) => setSenha(e.target.value)} required />
        </label>

        <button className="btn btn-primary full">Entrar no Sistema</button>
        <p className="muted center">
          Não tem conta? <button type="button" className="link" onClick={onGoToRegister}>Cadastre-se</button>
        </p>
      </form>
    </div>
  );
}
