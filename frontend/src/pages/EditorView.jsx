// RF04 - Acessar projeto. O editor (Monaco + DSL) será implementado nos próximos requisitos.
export default function EditorView({ project, onBack }) {
  return (
    <>
      <header className="topbar">
        <div className="row">
          <button className="btn btn-outline" onClick={onBack}>← Voltar</button>
          <strong>{project.nome}</strong>
        </div>
      </header>
      <main className="content">
        <p className="muted">Editor do projeto será implementado nos próximos requisitos.</p>
      </main>
    </>
  );
}
