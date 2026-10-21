import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { errorMessage } from '../services/api';

// RF01 - Cadastro
export default function Register({ onGoToLogin }) {
  const { register } = useAuth();
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [erro, setErro] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    setErro('');
    try {
      await register(nome, email, senha);
      alert('Cadastro realizado! Faça login.');
      onGoToLogin();
    } catch (err) {
      setErro(errorMessage(err, 'Não foi possível cadastrar.'));
    }
  }

  return (
    <div className="auth-page">
      <form className="card" onSubmit={handleSubmit}>
        <h1 className="logo"><span className="dot" /> CROSSPLAT</h1>
        {erro && <p className="error">{erro}</p>}

        <label>Nome
          <input value={nome} onChange={(e) => setNome(e.target.value)} required />
        </label>
        <label>E-mail
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label>Senha (mín. 6 caracteres)
          <input type="password" value={senha} onChange={(e) => setSenha(e.target.value)} minLength={6} required />
        </label>

        <button className="btn btn-primary full">Criar Conta</button>
        <p className="muted center">
          Já tem conta? <button type="button" className="link" onClick={onGoToLogin}>Entrar</button>
        </p>
      </form>
    </div>
  );
}
