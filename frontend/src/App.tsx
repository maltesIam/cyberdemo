import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Layout } from "./components/Layout";
import { GenerationPage } from "./pages/GenerationPage";
import { DashboardPage } from "./pages/DashboardPage";
import { AssetsPage } from "./pages/AssetsPage";
import { IncidentsPage } from "./pages/IncidentsPage";
import { DetectionsPage } from "./pages/DetectionsPage";
import { TimelinePage } from "./pages/TimelinePage";
import { PostmortemsPage } from "./pages/PostmortemsPage";
import { TicketsPage } from "./pages/TicketsPage";
import { CTEMPage } from "./pages/CTEMPage";
import { GraphPage } from "./pages/GraphPage";
import { CollabPage } from "./pages/CollabPage";
import { ConfigPage } from "./pages/ConfigPage";
import { AuditPage } from "./pages/AuditPage";
import { SurfacePage } from "./pages/SurfacePage";
import { ThreatEnrichmentPage } from "./pages/ThreatEnrichmentPage";
import { VulnerabilityDashboard } from "./pages/VulnerabilityDashboard";
import {
  CVEDetailPage,
  CVEAssetsPage,
  CVEExploitsPage,
  SSVCDashboard,
} from "./pages/vuln-pages";
import { SimulationPage } from "./pages/SimulationPage";
import { ToastProvider } from "./utils/toast";
import { DemoProvider } from "./context/DemoContext";

function App() {
  return (
    <DemoProvider persistToStorage={true}>
    <ToastProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Navigate to="/generation" replace />} />
            <Route path="surface" element={<SurfacePage />} />
            <Route path="generation" element={<GenerationPage />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="assets" element={<AssetsPage />} />
            <Route path="incidents" element={<IncidentsPage />} />
            <Route path="detections" element={<DetectionsPage />} />
            <Route path="timeline" element={<TimelinePage />} />
            <Route path="postmortems" element={<PostmortemsPage />} />
            <Route path="tickets" element={<TicketsPage />} />
            <Route path="ctem" element={<CTEMPage />} />
            <Route path="graph" element={<GraphPage />} />
            <Route path="graph/:incidentId" element={<GraphPage />} />
            <Route path="collab" element={<CollabPage />} />
            <Route path="config" element={<ConfigPage />} />
            <Route path="audit" element={<AuditPage />} />
            <Route path="threats" element={<ThreatEnrichmentPage />} />
            <Route path="vulnerabilities" element={<VulnerabilityDashboard />} />
            <Route path="vulnerabilities/cves/:cveId" element={<CVEDetailPage />} />
            <Route path="vulnerabilities/cves/:cveId/assets" element={<CVEAssetsPage />} />
            <Route path="vulnerabilities/cves/:cveId/exploits" element={<CVEExploitsPage />} />
            <Route path="vulnerabilities/ssvc" element={<SSVCDashboard />} />
            <Route path="simulation" element={<SimulationPage />} />
            <Route path="*" element={<Navigate to="/generation" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ToastProvider>
    </DemoProvider>
  );
}

export default App;
