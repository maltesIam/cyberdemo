import {
  ChevronDown,
  ChevronRight,
  Activity,
  Users,
  Scissors,
  TestTube,
  Calendar,
} from "lucide-react";
import React, { useState } from "react";
import { usePatientStore } from "./stores/patientStore";

interface AccordionSectionProps {
  title: string;
  icon: React.ElementType;
  children: React.ReactNode;
  defaultOpen?: boolean;
}

const AccordionSection: React.FC<AccordionSectionProps> = ({
  title,
  icon: Icon,
  children,
  defaultOpen = false,
}) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-4 py-3 bg-gray-50 flex items-center justify-between hover:bg-gray-100 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Icon className="w-5 h-5 text-medical-primary" />
          <span className="font-medium text-gray-900">{title}</span>
        </div>
        {isOpen ? (
          <ChevronDown className="w-5 h-5 text-gray-500" />
        ) : (
          <ChevronRight className="w-5 h-5 text-gray-500" />
        )}
      </button>
      {isOpen && <div className="p-4 bg-white">{children}</div>}
    </div>
  );
};

export const HistoriaTab: React.FC = () => {
  const rawData = usePatientStore((state) => state.rawData);
  const getLabResults = usePatientStore((state) => state.getLabResults);
  const getEpisodes = usePatientStore((state) => state.getEpisodes);
  const getPersonalBackground = usePatientStore((state) => state.getPersonalBackground);
  const getFamilyBackground = usePatientStore((state) => state.getFamilyBackground);
  const getSurgicalBackground = usePatientStore((state) => state.getSurgicalBackground);

  if (!rawData) {
    return (
      <div className="p-6 flex items-center justify-center h-full">
        <p className="text-gray-500">Cargando datos del paciente...</p>
      </div>
    );
  }

  const labResults = getLabResults();
  const episodes = getEpisodes();
  const personales = getPersonalBackground();
  const familiares = getFamilyBackground();
  const quirurgicos = getSurgicalBackground();

  return (
    <div className="h-full overflow-y-auto p-6 space-y-4">
      {/* Personal Background */}
      <AccordionSection title="Antecedentes Personales" icon={Activity} defaultOpen>
        <div className="space-y-3">
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-1">Enfermedades</h4>
            <ul className="list-disc list-inside text-sm text-gray-600">
              {personales.enfermedades.length > 0 ? (
                personales.enfermedades.map((enf, idx) => <li key={idx}>{enf}</li>)
              ) : (
                <li className="text-gray-400">Sin antecedentes registrados</li>
              )}
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-1">Hábitos</h4>
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Tabaco:</span>{" "}
                <span className="text-gray-900">{personales.habitos.tabaco}</span>
              </div>
              <div>
                <span className="text-gray-500">Alcohol:</span>{" "}
                <span className="text-gray-900">{personales.habitos.alcohol}</span>
              </div>
              <div>
                <span className="text-gray-500">Ejercicio:</span>{" "}
                <span className="text-gray-900">{personales.habitos.ejercicio}</span>
              </div>
            </div>
          </div>
        </div>
      </AccordionSection>

      {/* Family Background */}
      <AccordionSection title="Antecedentes Familiares" icon={Users}>
        <div className="space-y-2 text-sm">
          {familiares.length > 0 ? (
            familiares.map((item, idx) => (
              <p key={idx} className="text-gray-600">
                {item}
              </p>
            ))
          ) : (
            <p className="text-gray-400">Sin antecedentes familiares registrados</p>
          )}
        </div>
      </AccordionSection>

      {/* Surgical Background */}
      <AccordionSection title="Antecedentes Quirúrgicos" icon={Scissors}>
        {quirurgicos.length > 0 ? (
          <div className="space-y-2">
            {quirurgicos.map((cirugia, idx) => (
              <div key={idx} className="flex justify-between items-start p-2 bg-gray-50 rounded">
                <div>
                  <p className="font-medium text-gray-900">{cirugia.procedimiento}</p>
                  {cirugia.hospital && <p className="text-sm text-gray-500">{cirugia.hospital}</p>}
                </div>
                <span className="text-sm text-gray-500">{cirugia.fecha}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-400 text-sm">Sin antecedentes quirúrgicos</p>
        )}
      </AccordionSection>

      {/* Lab Results */}
      <AccordionSection title="Resultados de Laboratorio" icon={TestTube}>
        {labResults.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-2 px-2 font-medium text-gray-700">Fecha</th>
                  <th className="text-left py-2 px-2 font-medium text-gray-700">Parámetro</th>
                  <th className="text-right py-2 px-2 font-medium text-gray-700">Valor</th>
                  <th className="text-left py-2 px-2 font-medium text-gray-700">Unidad</th>
                  <th className="text-left py-2 px-2 font-medium text-gray-700">Rango</th>
                </tr>
              </thead>
              <tbody>
                {labResults.map((result) => {
                  const isOutOfRange =
                    result.valor < result.rangoMin || result.valor > result.rangoMax;
                  return (
                    <tr key={result.id} className="border-b border-gray-100">
                      <td className="py-2 px-2 text-gray-600">{result.fecha}</td>
                      <td className="py-2 px-2 text-gray-900">{result.parametro}</td>
                      <td
                        className={`py-2 px-2 text-right font-medium ${isOutOfRange ? "text-red-600" : "text-green-600"}`}
                      >
                        {result.valor}
                      </td>
                      <td className="py-2 px-2 text-gray-600">{result.unidad}</td>
                      <td className="py-2 px-2 text-gray-500">
                        {result.rangoMin} - {result.rangoMax}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-gray-400 text-sm">Sin resultados de laboratorio</p>
        )}
      </AccordionSection>

      {/* Clinical Episodes */}
      <AccordionSection title="Episodios Clínicos" icon={Calendar}>
        {episodes.length > 0 ? (
          <div className="space-y-3">
            {[...episodes]
              .sort((a, b) => new Date(b.fecha).getTime() - new Date(a.fecha).getTime())
              .map((episode) => (
                <div key={episode.id} className="p-3 bg-gray-50 rounded-lg">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <span className="text-sm text-gray-500">{episode.fecha}</span>
                      {episode.especialidad && (
                        <span className="ml-2 px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs">
                          {episode.especialidad}
                        </span>
                      )}
                    </div>
                    {episode.codigoCIE10 && (
                      <span className="text-xs font-mono text-gray-500">{episode.codigoCIE10}</span>
                    )}
                  </div>
                  <p className="font-medium text-gray-900">{episode.motivo}</p>
                  <p className="text-sm text-gray-700 mt-1">{episode.diagnostico}</p>
                  {episode.tratamiento && (
                    <p className="text-sm text-gray-600 mt-1">
                      <span className="font-medium">Tratamiento:</span> {episode.tratamiento}
                    </p>
                  )}
                </div>
              ))}
          </div>
        ) : (
          <p className="text-gray-400 text-sm">Sin episodios clínicos registrados</p>
        )}
      </AccordionSection>
    </div>
  );
};
