import { useEffect, useRef, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api, { errorMessage } from '../services/api';

const TAB_NAMES = {
  gpl_code: 'GPL.crossplat',
  datatype_def: 'datatypes.crossplat',
  global_functions: 'global.crossplat',
  deploy_model: 'deploy.crossplat (Visual)',
};

// Extrai o cabeçalho "platform X: Y {" e o "}" final para proteger o template (RF08)
function extrairLimitesPlataforma(codigo) {
  const linhas = (codigo || '').split('\n');
  if (linhas.length >= 2) {
    return {
      cabecalho: linhas[0].trim(),
      rodape: linhas[linhas.length - 1].trim(),
    };
  }
  return null;
}

// Analisa o código GPL e o deploy_model atual para montar o painel visual (RF09)
function parseDeployState(gplCode, deployModel) {
  const classRegex = /class\s+([a-zA-Z0-9_]+)\s*\{/g;
  const classesEncontradas = [];
  let match;
  while ((match = classRegex.exec(gplCode || '')) !== null) {
    if (!classesEncontradas.includes(match[1])) {
      classesEncontradas.push(match[1]);
    }
  }

  let deployName = ' MeuDeploy';
  const nameMatch = /deploy\s+([a-zA-Z0-9_]+)\s*\{/.exec(deployModel || '');
  if (nameMatch) {
    deployName = nameMatch[1];
  }

  const selections = {};
  classesEncontradas.forEach((c) => {
    selections[c] = [];
  });

  const mapRegex = /([a-zA-Z0-9_]+)\s*:\s*([a-zA-Z0-9_]+)/g;
  const bodyMatch = /\{([\s\S]*)\}/.exec(deployModel || '');
  if (bodyMatch) {
    const body = bodyMatch[1];
    let m;
    while ((m = mapRegex.exec(body)) !== null) {
      const cls = m[1];
      const plat = m[2];
      if (selections[cls] && !selections[cls].includes(plat)) {
        selections[cls].push(plat);
      }
    }
  }

  return { classesEncontradas, deployName, selections };
}

function buildDeployCode(deployName, selections) {
  const dName = (deployName || '').trim() || 'MeuDeploy';
  let code = `deploy ${dName}{\n`;
  Object.keys(selections).forEach((cls) => {
    (selections[cls] || []).forEach((plat) => {
      code += `\t${cls}: ${plat}\n`;
    });
  });
  code += `}`;
  return code;
}

export default function EditorView({ project, onBack }) {
  const { user, logout } = useAuth();

  // Estado dos arquivos do projeto (RF05 / RF06)
  const [projectFiles, setProjectFiles] = useState({
    gpl_code: '',
    datatype_def: '',
    global_functions: '',
    deploy_model: '',
  });
  const [linkedPlatforms, setLinkedPlatforms] = useState([]);
  const [outputFiles, setOutputFiles] = useState([]);
  const [activeKey, setActiveKey] = useState('gpl_code');

  // Estado do painel visual de Deploy (RF09)
  const [deployClasses, setDeployClasses] = useState([]);
  const [deployName, setDeployName] = useState('MeuDeploy');
  const [deploySelections, setDeploySelections] = useState({});

  // Estado dos Modais de Marketplace (RF07) e Criação de Plataforma (RF08)
  const [showMarketModal, setShowMarketModal] = useState(false);
  const [marketSearch, setMarketSearch] = useState('');
  const [marketList, setMarketList] = useState([]);

  const [showCreatePlatModal, setShowCreatePlatModal] = useState(false);
  const [languages, setLanguages] = useState([]);
  const [newPlatName, setNewPlatName] = useState('');
  const [newPlatLang, setNewPlatLang] = useState('');

  // Loading de Build (RF10) e Toast
  const [isBuilding, setIsBuilding] = useState(false);
  const [toast, setToast] = useState(null);

  // Referências para integração com o Monaco Editor (RF06)
  const monacoContainerRef = useRef(null);
  const editorRef = useRef(null);
  const isProgrammaticChangeRef = useRef(false);
  const activeKeyRef = useRef(activeKey);
  const projectFilesRef = useRef(projectFiles);
  const linkedPlatformsRef = useRef(linkedPlatforms);
  const platBoundsRef = useRef(null);
  const lastValidPlatCodeRef = useRef('');

  activeKeyRef.current = activeKey;
  projectFilesRef.current = projectFiles;
  linkedPlatformsRef.current = linkedPlatforms;

  function showToast(msg, isError = false) {
    setToast({ msg, isError });
    setTimeout(() => setToast(null), 3500);
  }

  // Carrega detalhes do projeto e plataformas vinculadas (RF06)
  async function carregarProjeto() {
    try {
      const { data } = await api.get(`/projects/${project.id}`);
      const files = {
        gpl_code: data.gpl_code || '// Escreva seu código GPL aqui\n\nclass Exemplo {\n\t\n}',
        datatype_def: data.datatype_def || '// Definição de Tipos de Dados (datatypes.crossplat)\n',
        global_functions: data.global_functions || '// Declaração de Funções Globais (global.crossplat)\n',
        deploy_model: data.deploy_model || 'deploy MeuDeploy{\n\t\n}',
      };
      setProjectFiles(files);
      setLinkedPlatforms(data.modelos_vinculados || []);
      return { files, modelos: data.modelos_vinculados || [] };
    } catch (err) {
      if (err.response?.status === 401) logout();
      else showToast(errorMessage(err, 'Erro ao carregar projeto.'), true);
      return null;
    }
  }

  useEffect(() => {
    carregarProjeto();
  }, [project.id]);

  // Inicializa o Monaco Editor via CDN loader (igual ao projeto_editor.html)
  useEffect(() => {
    let disposed = false;

    function initMonaco() {
      if (!window.require || !monacoContainerRef.current || editorRef.current) return;
      window.require.config({
        paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.36.1/min/vs' },
      });
      window.require(['vs/editor/editor.main'], () => {
        if (disposed || !monacoContainerRef.current || editorRef.current) return;
        const instance = window.monaco.editor.create(monacoContainerRef.current, {
          value: projectFilesRef.current.gpl_code || '',
          language: 'cpp',
          theme: 'vs-dark',
          automaticLayout: true,
          fontSize: 14,
          fontFamily: "'Fira Code', monospace",
          minimap: { enabled: true },
          readOnly: false,
        });

        instance.onDidChangeModelContent(() => {
          if (isProgrammaticChangeRef.current) return;
          const currentKey = activeKeyRef.current;
          const val = instance.getValue();

          if (currentKey.startsWith('plat_')) {
            const bounds = platBoundsRef.current;
            if (bounds) {
              const linhas = val.split('\n');
              const cabecalhoIntacto = linhas[0].trim() === bounds.cabecalho;
              const rodapeIntacto = linhas[linhas.length - 1].trim() === bounds.rodape;
              if (linhas.length < 2 || !cabecalhoIntacto || !rodapeIntacto) {
                isProgrammaticChangeRef.current = true;
                const pos = instance.getPosition();
                instance.setValue(lastValidPlatCodeRef.current);
                if (pos) instance.setPosition(pos);
                isProgrammaticChangeRef.current = false;
                showToast('A estrutura "platform Nome: Linguagem { ... }" é protegida e não pode ser apagada!', true);
                return;
              }
            }
            lastValidPlatCodeRef.current = val;
            const platId = parseInt(currentKey.replace('plat_', ''), 10);
            setLinkedPlatforms((prev) =>
              prev.map((p) => (p.id === platId ? { ...p, codigo: val } : p))
            );
          } else if (!currentKey.startsWith('out_') && currentKey !== 'deploy_model') {
            setProjectFiles((prev) => ({ ...prev, [currentKey]: val }));
          }
        });

        editorRef.current = instance;
      });
    }

    initMonaco();
    return () => {
      disposed = true;
      if (editorRef.current) {
        editorRef.current.dispose();
        editorRef.current = null;
      }
    };
  }, []);

  // Sincroniza o conteúdo e permissões do Monaco quando a aba ativa muda
  useEffect(() => {
    if (activeKey === 'deploy_model') {
      const parsed = parseDeployState(projectFiles.gpl_code, projectFiles.deploy_model);
      setDeployClasses(parsed.classesEncontradas);
      setDeployName(parsed.deployName);
      setDeploySelections(parsed.selections);
      return;
    }

    const editor = editorRef.current;
    if (!editor || !window.monaco) return;

    isProgrammaticChangeRef.current = true;

    if (activeKey.startsWith('plat_')) {
      const platId = parseInt(activeKey.replace('plat_', ''), 10);
      const plat = linkedPlatforms.find((p) => p.id === platId);
      if (plat) {
        const isMine = plat.criador_id === user.id;
        lastValidPlatCodeRef.current = plat.codigo || '';
        platBoundsRef.current = extrairLimitesPlataforma(plat.codigo || '');
        window.monaco.editor.setModelLanguage(editor.getModel(), 'cpp');
        editor.setValue(plat.codigo || '');
        editor.updateOptions({ readOnly: !isMine });
      }
    } else if (activeKey.startsWith('out_')) {
      const outIdx = parseInt(activeKey.replace('out_', ''), 10);
      const file = outputFiles[outIdx];
      if (file) {
        const ext = file.nome.split('.').pop();
        const langMap = {
          py: 'python',
          js: 'javascript',
          java: 'java',
          cs: 'csharp',
          cpp: 'cpp',
          h: 'cpp',
          kt: 'kotlin',
          swift: 'swift',
          dart: 'dart',
        };
        window.monaco.editor.setModelLanguage(editor.getModel(), langMap[ext] || 'plaintext');
        editor.setValue(file.conteudo || '');
        editor.updateOptions({ readOnly: true });
      }
    } else {
      platBoundsRef.current = null;
      window.monaco.editor.setModelLanguage(editor.getModel(), 'cpp');
      editor.setValue(projectFiles[activeKey] || '');
      editor.updateOptions({ readOnly: false });
    }

    isProgrammaticChangeRef.current = false;
  }, [activeKey, outputFiles]);

  // Atualiza o editor quando o projeto termina de carregar pela primeira vez
  useEffect(() => {
    const editor = editorRef.current;
    if (!editor || activeKey !== 'gpl_code') return;
    if (editor.getValue() === '' && projectFiles.gpl_code) {
      isProgrammaticChangeRef.current = true;
      editor.setValue(projectFiles.gpl_code);
      isProgrammaticChangeRef.current = false;
    }
  }, [projectFiles.gpl_code]);

  // Manipuladores do Painel Visual de Deploy (RF09)
  function handleDeployNameChange(val) {
    setDeployName(val);
    const code = buildDeployCode(val, deploySelections);
    setProjectFiles((prev) => ({ ...prev, deploy_model: code }));
  }

  function handleToggleDeployPlatform(className, platName) {
    setDeploySelections((prev) => {
      const currentList = prev[className] || [];
      const exists = currentList.includes(platName);
      const nextList = exists
        ? currentList.filter((item) => item !== platName)
        : [...currentList, platName];
      const nextSelections = { ...prev, [className]: nextList };
      const code = buildDeployCode(deployName, nextSelections);
      setProjectFiles((pf) => ({ ...pf, deploy_model: code }));
      return nextSelections;
    });
  }

  // RF05 - Salvar arquivos do projeto e plataforma ativa (se for do usuário)
  async function handleSaveProject(silencioso = false) {
    try {
      await api.put(`/projects/${project.id}`, projectFiles);

      if (activeKey.startsWith('plat_')) {
        const platId = parseInt(activeKey.replace('plat_', ''), 10);
        const plat = linkedPlatforms.find((p) => p.id === platId);
        if (plat && plat.criador_id === user.id) {
          const resPlat = await api.put(`/marketplace/${platId}`, { codigo: plat.codigo });
          if (resPlat.data?.erro) {
            showToast(resPlat.data.erro, true);
            return false;
          }
        }
      }

      if (!silencioso) showToast('Projeto salvo com sucesso!');
      return true;
    } catch (err) {
      showToast(errorMessage(err, 'Erro ao salvar.'), true);
      return false;
    }
  }

  // RF10 - Compilar & Build acionando generator.jar no backend
  async function handleBuildProject() {
    await handleSaveProject(true);
    setIsBuilding(true);
    try {
      const { data } = await api.post(`/projects/${project.id}/build`);
      setIsBuilding(false);

      if (data.sucesso) {
        const arquivos = data.arquivos || [];
        setOutputFiles(arquivos);
        showToast('Build concluído! Veja a aba Output.');
        if (arquivos.length > 0) {
          setActiveKey('out_0');
        }
      } else {
        showToast(data.erro || 'Falha na compilação', true);
        if (data.detalhes) {
          alert(`Log de Erro do Compilador:\n\n${data.detalhes}`);
        }
      }
    } catch (err) {
      setIsBuilding(false);
      const resp = err.response?.data;
      showToast(resp?.erro || 'Erro de conexão com o servidor de Build.', true);
      if (resp?.detalhes) {
        alert(`Log de Erro do Compilador:\n\n${resp.detalhes}`);
      }
    }
  }

  // RF07 - Desvincular plataforma do projeto
  async function handleUnlinkPlatform(e, modelId) {
    e.stopPropagation();
    if (!confirm('Remover plataforma deste projeto?')) return;
    try {
      await api.delete(`/projects/${project.id}/model/${modelId}`);
      const updated = await carregarProjeto();
      if (activeKey === `plat_${modelId}`) {
        setActiveKey('gpl_code');
      } else if (activeKey === 'deploy_model' && updated) {
        const parsed = parseDeployState(updated.files.gpl_code, updated.files.deploy_model);
        setDeployClasses(parsed.classesEncontradas);
        setDeploySelections(parsed.selections);
      }
      showToast('Plataforma desvinculada.');
    } catch (err) {
      showToast(errorMessage(err, 'Erro ao desvincular plataforma.'), true);
    }
  }

  // RF07 - Marketplace Modal
  async function buscarMarketplace(q = '') {
    try {
      const { data } = await api.get(`/marketplace?q=${encodeURIComponent(q)}`);
      setMarketList(data);
    } catch (err) {
      showToast(errorMessage(err, 'Erro ao buscar no Marketplace.'), true);
    }
  }

  function handleOpenMarketplace() {
    setMarketSearch('');
    setShowMarketModal(true);
    buscarMarketplace('');
  }

  async function handleLinkModel(modelId) {
    try {
      await api.post(`/projects/${project.id}/link_model`, { model_id: modelId });
      await carregarProjeto();
      setShowMarketModal(false);
      showToast('Plataforma vinculada!');
    } catch (err) {
      showToast(errorMessage(err, 'Erro ao vincular plataforma.'), true);
    }
  }

  // RF08 - Criar Nova Plataforma Modal
  async function handleOpenCreatePlat() {
    setShowMarketModal(false);
    setNewPlatName('');
    setShowCreatePlatModal(true);
    try {
      const { data } = await api.get('/linguagens');
      setLanguages(data);
      if (data.length > 0) setNewPlatLang(data[0].nome);
    } catch (err) {
      showToast(errorMessage(err, 'Erro ao carregar linguagens.'), true);
    }
  }

  async function handleCreatePlatform() {
    const nomeLimpo = newPlatName.replace(/[^a-zA-Z0-9_]/g, '');
    if (!nomeLimpo || !newPlatLang) {
      showToast('Preencha o nome e selecione uma linguagem.', true);
      return;
    }

    const codigoTemplate = `platform ${nomeLimpo}: ${newPlatLang} {\n\t// Escreva os triggers aqui\n}`;
    try {
      const { data } = await api.post('/marketplace', {
        nome: nomeLimpo,
        linguagem: newPlatLang,
        codigo: codigoTemplate,
      });
      await handleLinkModel(data.id);
      setShowCreatePlatModal(false);
      setActiveKey(`plat_${data.id}`);
    } catch (err) {
      showToast(errorMessage(err, 'Erro ao criar plataforma.'), true);
    }
  }

  // Calcula título da aba e status exibido no topo do editor
  let currentTabTitle = TAB_NAMES[activeKey] || activeKey;
  let statusNode = (
    <>
      <span className="material-symbols-outlined" style={{ fontSize: 14 }}>edit</span>
      Modo Edição Livre
    </>
  );
  let statusColor = '#888';

  if (activeKey === 'deploy_model') {
    statusColor = '#60a5fa';
    statusNode = (
      <>
        <span className="material-symbols-outlined" style={{ fontSize: 14 }}>visibility</span>
        Modo Visual Interativo
      </>
    );
  } else if (activeKey.startsWith('plat_')) {
    const platId = parseInt(activeKey.replace('plat_', ''), 10);
    const plat = linkedPlatforms.find((p) => p.id === platId);
    if (plat) {
      currentTabTitle = `${plat.nome}.plat`;
      const isMine = plat.criador_id === user.id;
      statusColor = isMine ? '#34d399' : '#facc15';
      statusNode = isMine ? (
        <>
          <span className="material-symbols-outlined" style={{ fontSize: 14 }}>edit</span>
          Modo Edição (Autor - Linhas 1 e Final Protegidas)
        </>
      ) : (
        <>
          <span className="material-symbols-outlined" style={{ fontSize: 14 }}>lock</span>
          Modo Leitura (Comunidade)
        </>
      );
    }
  } else if (activeKey.startsWith('out_')) {
    const outIdx = parseInt(activeKey.replace('out_', ''), 10);
    const file = outputFiles[outIdx];
    if (file) {
      currentTabTitle = `[Output] ${file.nome}`;
      statusColor = '#34d399';
      statusNode = (
        <>
          <span className="material-symbols-outlined" style={{ fontSize: 14 }}>check_circle</span>
          Código Gerado (Apenas Leitura)
        </>
      );
    }
  }

  const sanitizedPreviewName = newPlatName.replace(/[^a-zA-Z0-9_]/g, '') || 'Nome';
  const previewLang = newPlatLang || 'Linguagem';

  return (
    <div className="ide-screen">
      {/* OVERLAY DE COMPILAÇÃO (RF10) */}
      {isBuilding && (
        <div className="loading-overlay">
          <span className="material-symbols-outlined spin" style={{ fontSize: 48, color: '#10b981' }}>
            settings
          </span>
          <h3 style={{ color: '#fff' }}>Compilando Projeto...</h3>
          <p className="muted">Gerando código multiplataforma via Motor Crossplat</p>
        </div>
      )}

      {/* NAVBAR SUPERIOR */}
      <header className="ide-navbar">
        <div className="row" style={{ gap: 16 }}>
          <button className="btn btn-outline" onClick={onBack}>
            <span className="material-symbols-outlined" style={{ fontSize: 16 }}>arrow_back</span>
            Dashboard
          </button>
          <span className="logo" style={{ margin: 0, fontSize: 18 }}>
            <span className="dot" /> CROSSPLAT IDE
          </span>
          <span className="ide-project-badge">{project.nome}</span>
        </div>
        <div className="row">
          <button className="btn btn-primary" onClick={() => handleSaveProject(false)}>
            <span className="material-symbols-outlined" style={{ fontSize: 16 }}>save</span>
            Salvar
          </button>
          <button className="btn btn-success" onClick={handleBuildProject}>
            <span className="material-symbols-outlined" style={{ fontSize: 16 }}>play_arrow</span>
            Compilar &amp; Build
          </button>
          <button
            className="btn btn-outline"
            onClick={logout}
            style={{ color: '#f87171', borderColor: 'transparent' }}
          >
            Sair
          </button>
        </div>
      </header>

      {/* ÁREA DE TRABALHO */}
      <div className="ide-workspace">
        {/* SIDEBAR DE ARQUIVOS */}
        <aside className="ide-sidebar">
          <div className="sidebar-section">Fontes do Projeto</div>
          <div
            className={`file-item ${activeKey === 'gpl_code' ? 'active' : ''}`}
            onClick={() => setActiveKey('gpl_code')}
          >
            <div className="file-item-left">
              <span className="material-symbols-outlined" style={{ fontSize: 18 }}>code</span>
              GPL.crossplat
            </div>
          </div>
          <div
            className={`file-item ${activeKey === 'datatype_def' ? 'active' : ''}`}
            onClick={() => setActiveKey('datatype_def')}
          >
            <div className="file-item-left">
              <span className="material-symbols-outlined" style={{ fontSize: 18 }}>data_object</span>
              datatypes.crossplat
            </div>
          </div>
          <div
            className={`file-item ${activeKey === 'global_functions' ? 'active' : ''}`}
            onClick={() => setActiveKey('global_functions')}
          >
            <div className="file-item-left">
              <span className="material-symbols-outlined" style={{ fontSize: 18 }}>functions</span>
              global.crossplat
            </div>
          </div>
          <div
            className={`file-item ${activeKey === 'deploy_model' ? 'active' : ''}`}
            onClick={() => setActiveKey('deploy_model')}
          >
            <div className="file-item-left">
              <span className="material-symbols-outlined" style={{ fontSize: 18, color: '#60a5fa' }}>
                rocket_launch
              </span>
              deploy.crossplat
            </div>
          </div>

          <div className="sidebar-section" style={{ marginTop: 15 }}>
            <span>Plataformas</span>
            <span
              className="material-symbols-outlined"
              style={{ fontSize: 16, cursor: 'pointer', color: '#60a5fa' }}
              onClick={handleOpenMarketplace}
              title="Adicionar Plataforma"
            >
              add
            </span>
          </div>

          <div>
            {linkedPlatforms.map((plat) => {
              const isMine = plat.criador_id === user.id;
              const key = `plat_${plat.id}`;
              return (
                <div
                  key={plat.id}
                  className={`file-item ${activeKey === key ? 'active' : ''}`}
                  onClick={() => setActiveKey(key)}
                >
                  <div className="file-item-left">
                    <span
                      className="material-symbols-outlined"
                      style={{ fontSize: 16, color: isMine ? '#34d399' : '#888' }}
                    >
                      {isMine ? 'edit_note' : 'lock'}
                    </span>
                    <span>{plat.nome}.plat</span>
                  </div>
                  <span
                    className="material-symbols-outlined"
                    style={{ fontSize: 14, color: '#666' }}
                    title="Desvincular plataforma"
                    onClick={(e) => handleUnlinkPlatform(e, plat.id)}
                  >
                    close
                  </span>
                </div>
              );
            })}
          </div>

          <div style={{ padding: '10px 20px' }}>
            <button
              className="btn btn-outline"
              style={{ width: '100%', justifyContent: 'center', borderStyle: 'dashed', fontSize: 12 }}
              onClick={handleOpenMarketplace}
            >
              <span className="material-symbols-outlined" style={{ fontSize: 16 }}>storefront</span>
              Marketplace Global
            </button>
          </div>

          <div className="sidebar-section" style={{ marginTop: 15 }}>
            <span>Output</span>
          </div>
          <div>
            {outputFiles.length === 0 ? (
              <div style={{ padding: '10px 20px', fontSize: 12, color: '#555' }}>
                Nenhum build gerado
              </div>
            ) : (
              outputFiles.map((file, idx) => {
                const key = `out_${idx}`;
                return (
                  <div
                    key={key}
                    className={`file-item ${activeKey === key ? 'active' : ''}`}
                    onClick={() => setActiveKey(key)}
                  >
                    <div className="file-item-left">
                      <span
                        className="material-symbols-outlined"
                        style={{ fontSize: 16, color: '#34d399' }}
                      >
                        description
                      </span>
                      <span>{file.nome}</span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </aside>

        {/* ÁREA PRINCIPAL DO EDITOR */}
        <section className="ide-editor-area">
          <div className="editor-tabs">
            <div className="tab">
              <span className="material-symbols-outlined" style={{ fontSize: 15 }}>description</span>
              <span>{currentTabTitle}</span>
            </div>
            <div className="editor-status" style={{ color: statusColor }}>
              {statusNode}
            </div>
          </div>

          {/* MONACO EDITOR (permanece montado e fica oculto apenas na aba Visual de Deploy) */}
          <div
            ref={monacoContainerRef}
            className="monaco-wrapper"
            style={{ display: activeKey === 'deploy_model' ? 'none' : 'block' }}
          />

          {/* PAINEL VISUAL DE DEPLOY (RF09) */}
          {activeKey === 'deploy_model' && (
            <div className="deploy-container">
              <div className="deploy-panel">
                <h2 style={{ marginBottom: 5, fontSize: 18 }}>Configuração de Deploy</h2>
                <p className="muted" style={{ marginBottom: 20 }}>
                  Selecione em quais plataformas cada classe do seu código GPL será compilada.
                </p>

                <label>
                  NOME DO DEPLOY
                  <input
                    value={deployName}
                    onChange={(e) => handleDeployNameChange(e.target.value)}
                    style={{ maxWidth: 300, display: 'block' }}
                  />
                </label>

                {deployClasses.length === 0 ? (
                  <div
                    style={{
                      padding: 20,
                      background: '#1e1e1e',
                      border: '1px dashed #444',
                      borderRadius: 8,
                      color: '#888',
                    }}
                  >
                    Nenhuma classe detectada no arquivo <b>GPL.crossplat</b>.<br />
                    Declare classes como <code>class Usuario {'{ ... }'}</code> na aba GPL para mapeá-las aqui.
                  </div>
                ) : linkedPlatforms.length === 0 ? (
                  <div
                    style={{
                      padding: 20,
                      background: '#1e1e1e',
                      border: '1px dashed #f87171',
                      borderRadius: 8,
                      color: '#f87171',
                    }}
                  >
                    Você ainda não vinculou nenhuma plataforma ao projeto.<br />
                    Clique em <b>Marketplace Global</b> na barra lateral para adicionar plataformas.
                  </div>
                ) : (
                  deployClasses.map((cls) => (
                    <div key={cls} className="class-card">
                      <div className="class-name">
                        <span className="material-symbols-outlined" style={{ color: '#60a5fa' }}>
                          data_object
                        </span>
                        {cls}
                      </div>
                      <div className="platform-toggles">
                        {linkedPlatforms.map((plat) => {
                          const isSelected = (deploySelections[cls] || []).includes(plat.nome);
                          return (
                            <button
                              key={plat.id}
                              type="button"
                              className={`plat-btn ${isSelected ? 'selected' : ''}`}
                              onClick={() => handleToggleDeployPlatform(cls, plat.nome)}
                            >
                              <span className="material-symbols-outlined" style={{ fontSize: 14 }}>
                                {isSelected ? 'check_circle' : 'radio_button_unchecked'}
                              </span>
                              {plat.nome}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  ))
                )}
              </div>

              <div className="deploy-preview">
                <div
                  style={{
                    color: '#888',
                    fontSize: 11,
                    marginBottom: 10,
                    textTransform: 'uppercase',
                    fontWeight: 700,
                  }}
                >
                  Código Gerado (deploy.crossplat)
                </div>
                <pre style={{ whiteSpace: 'pre-wrap', fontFamily: "'Fira Code', monospace" }}>
                  {projectFiles.deploy_model}
                </pre>
              </div>
            </div>
          )}
        </section>
      </div>

      {/* MODAL DO MARKETPLACE (RF07) */}
      {showMarketModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Marketplace de Plataformas</h3>
              <span
                className="material-symbols-outlined"
                style={{ cursor: 'pointer', color: '#888' }}
                onClick={() => setShowMarketModal(false)}
              >
                close
              </span>
            </div>

            <div className="row">
              <input
                placeholder="Buscar plataforma (ex: Flask, React, Android)..."
                value={marketSearch}
                onChange={(e) => {
                  setMarketSearch(e.target.value);
                  buscarMarketplace(e.target.value);
                }}
                style={{ marginTop: 0 }}
              />
              <button
                className="btn btn-primary"
                style={{ whiteSpace: 'nowrap' }}
                onClick={handleOpenCreatePlat}
              >
                + Nova Plataforma
              </button>
            </div>

            <div className="market-list">
              {marketList.length === 0 ? (
                <p className="muted" style={{ textAlign: 'center', padding: 20 }}>
                  Nenhuma plataforma encontrada. Crie a primeira!
                </p>
              ) : (
                marketList.map((m) => {
                  const jaVinculado = linkedPlatforms.some((p) => p.id === m.id);
                  const isMine = m.criador_id === user.id;
                  return (
                    <div key={m.id} className="market-item">
                      <div>
                        <strong style={{ color: '#fff', fontSize: 14 }}>{m.nome}</strong>
                        <span className={`tag ${isMine ? 'mine' : ''}`}>
                          {isMine ? 'Seu Modelo' : 'Comunidade'}
                        </span>
                        <div style={{ fontSize: 11, color: '#888', marginTop: 4 }}>
                          Linguagem Base: <b style={{ color: '#ccc' }}>{m.linguagem || 'N/A'}</b>
                        </div>
                      </div>
                      {jaVinculado ? (
                        <button className="btn btn-outline" disabled style={{ opacity: 0.5 }}>
                          Vinculado
                        </button>
                      ) : (
                        <button className="btn btn-primary" onClick={() => handleLinkModel(m.id)}>
                          Adicionar
                        </button>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      )}

      {/* MODAL CRIAR NOVA PLATAFORMA (RF08) */}
      {showCreatePlatModal && (
        <div className="modal-overlay">
          <div className="modal-content" style={{ width: 450 }}>
            <div className="modal-header">
              <h3>Criar Modelo de Plataforma</h3>
              <span
                className="material-symbols-outlined"
                style={{ cursor: 'pointer', color: '#888' }}
                onClick={() => setShowCreatePlatModal(false)}
              >
                close
              </span>
            </div>

            <div>
              <label style={{ marginBottom: 4 }}>NOME DA PLATAFORMA (Sem espaços)</label>
              <input
                placeholder="Ex: SpringBoot, ReactWeb, PostgreSQL"
                value={newPlatName}
                onChange={(e) => setNewPlatName(e.target.value)}
              />
            </div>

            <div>
              <label style={{ marginBottom: 4 }}>LINGUAGEM ALVO</label>
              <select value={newPlatLang} onChange={(e) => setNewPlatLang(e.target.value)}>
                {languages.map((l) => (
                  <option key={l.id} value={l.nome}>
                    {l.nome}
                  </option>
                ))}
              </select>
            </div>

            <div
              style={{
                background: '#141414',
                padding: 12,
                borderRadius: 6,
                border: '1px solid #333',
                fontFamily: "'Fira Code', monospace",
                fontSize: 12,
                color: '#888',
              }}
            >
              <div>
                <span style={{ color: '#c678dd' }}>platform</span>{' '}
                <span style={{ color: '#60a5fa' }}>{sanitizedPreviewName}</span>:{' '}
                <span style={{ color: '#e5c07b' }}>{previewLang}</span> {'{'}
              </div>
              <div style={{ paddingLeft: 15, color: '#555' }}>// Seu código de geração aqui</div>
              <div>{'}'}</div>
            </div>

            <button className="btn btn-primary full" onClick={handleCreatePlatform}>
              Criar &amp; Vincular ao Projeto
            </button>
          </div>
        </div>
      )}

      {/* TOAST DE FEEDBACK */}
      {toast && <div className={`toast ${toast.isError ? 'error' : ''}`}>{toast.msg}</div>}
    </div>
  );
}
