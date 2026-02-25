import React, { useEffect } from "react";
import { PatientHeader } from "./PatientHeader";
import { TabBar } from "./TabBar";
import { CodificacionTab } from "./CodificacionTab";
import { ConsultaTab } from "./ConsultaTab";
import { HistoriaTab } from "./HistoriaTab";
import { VisorTab } from "./VisorTab";
import { mcpClient } from "./services/mcpClient";
import { usePatientStore } from "./stores/patientStore";
import { useTabStore } from "./stores/tabStore";

const TabContent: React.FC = () => {
  const activeTab = useTabStore((state) => state.activeTab);

  switch (activeTab) {
    case "consulta":
      return <ConsultaTab />;
    case "historia":
      return <HistoriaTab />;
    case "codificacion":
      return <CodificacionTab />;
    case "visor":
      return <VisorTab />;
    default:
      return <ConsultaTab />;
  }
};

export const MedicumApp: React.FC = () => {
  const loadPatientData = usePatientStore((state) => state.loadPatientData);
  const isLoading = usePatientStore((state) => state.isLoading);

  useEffect(() => {
    // Load patient data on mount
    loadPatientData();

    // Connect to MCP gateway
    mcpClient.connect();

    // Cleanup on unmount
    return () => {
      mcpClient.disconnect();
    };
  }, [loadPatientData]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-medical-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Cargando datos del paciente...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col" data-testid="medicum-app">
      <PatientHeader />
      <TabBar />
      <main className="flex-1 overflow-hidden" data-testid="medicum-main">
        <TabContent />
      </main>
    </div>
  );
};

export default MedicumApp;
