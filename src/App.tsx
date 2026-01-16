import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/dashboard/Layout';
import { DashboardView } from './views/DashboardView';
import { FactoryView } from './views/FactoryView';
import { IntelligenceView } from './views/IntelligenceView';
import { ProjectsView } from './views/ProjectsView';
import { BoardView } from './views/BoardView';
import './index.css';
import './views/Views.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Nested routes under Layout */}
        <Route path="/" element={<Layout />}>
          <Route index element={<DashboardView />} />
          <Route path="factory" element={<FactoryView />} />
          <Route path="intelligence" element={<IntelligenceView />} />
          <Route path="projects" element={<ProjectsView />} />
          <Route path="projects/:projectName" element={<ProjectsView />} />
          <Route path="board" element={<BoardView />} />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
