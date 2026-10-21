import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api, { errorMessage } from '../services/api';

// RF03 (criar) e RF04 (listar, acessar, excluir)
export default function Dashboard({ onOpenProject }) {
  const { user, logout } = useAuth();
  const [projects, setProjects] = useState([]);
  const [nome, setNome] = useState('');
  const [erro, setErro] = useState('');

  useEffect(() => {
    api.get('/projects')
      .then((res) => setProjects(res.data))
      .catch((err) => (err.response?.status === 401 ? logout() : setErro('Erro ao carregar projetos.')));
  }, []);

  async function handleCreate(e) {
    e.preventDefault();
    setErro('');
    try {
      const { data } = await api.post('/projects', { nome });
      setProjects([data, ...projects]);
      setNome('');
    } catch (err) {
      setErro(errorMessage(err, 'Erro ao criar projeto.'));
    }
  }

  async function handleDelete(project) {
    if (!confirm(`Excluir o projeto "${project.nome}"?`)) return;
    try {
      await api.delete(`/projects/${project.id}`);
      setProjects(projects.filter((p) => p.id !== project.id));
    } catch (err) {
      setErro(errorMessage(err, 'Erro ao excluir projeto.'));
    }
  }

  return (
    <>
      <header className="topbar">
        <span className="logo"><span className="dot" /> CROSSPLAT</span>
        <div className="row">
          <span className="muted">Bem-vindo, {user.nome}</span>
          <button className="btn btn-outline" onClick={logout}>Sair</button>
        </div>
      </header>

      <main className="content">
        <h2>Meus Projetos</h2>

        <form className="row new-project" onSubmit={handleCreate}>
          <input placeholder="Nome do novo projeto" value={nome} onChange={(e) => setNome(e.target.value)} required />
          <button className="btn btn-primary">+ Novo Projeto</button>
        </form>

        {erro && <p className="error">{erro}</p>}
        {projects.length === 0 && <p className="muted">Nenhum projeto ainda. Crie o primeiro acima.</p>}

        <div className="grid">
          {projects.map((p) => (
            <div key={p.id} className="project-card">
              <h3>{p.nome}</h3>
              <p className="muted">Criado em: {new Date(p.data_criacao).toLocaleDateString('pt-BR')}</p>
              <div className="row">
                <button className="btn btn-outline" onClick={() => onOpenProject(p)}>Acessar</button>
                <button className="btn btn-danger" onClick={() => handleDelete(p)}>Excluir</button>
              </div>
            </div>
          ))}
        </div>
      </main>
    </>
  );
}
