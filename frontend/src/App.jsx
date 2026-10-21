import { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import EditorView from './pages/EditorView';

function Screens() {
  const { user } = useAuth();
  const [screen, setScreen] = useState('login');
  const [project, setProject] = useState(null);

  if (!user) {
    return screen === 'login'
      ? <Login onGoToRegister={() => setScreen('register')} />
      : <Register onGoToLogin={() => setScreen('login')} />;
  }

  if (project) return <EditorView project={project} onBack={() => setProject(null)} />;

  return <Dashboard onOpenProject={setProject} />;
}

export default function App() {
  return (
    <AuthProvider>
      <Screens />
    </AuthProvider>
  );
}
