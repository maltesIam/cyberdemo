import { Stethoscope, FileText, Code, Image } from "lucide-react";
import React from "react";
import { useTabStore, TABS } from "./stores/tabStore";

const iconMap: Record<string, React.ElementType> = {
  stethoscope: Stethoscope,
  "file-text": FileText,
  code: Code,
  image: Image,
};

export const TabBar: React.FC = () => {
  const activeTab = useTabStore((state) => state.activeTab);
  const setActiveTab = useTabStore((state) => state.setActiveTab);

  return (
    <nav className="bg-white border-b border-gray-200" data-testid="tab-bar" role="tablist">
      <div className="flex">
        {TABS.map((tab) => {
          const Icon = iconMap[tab.icon] || FileText;
          const isActive = activeTab === tab.id;

          return (
            <button
              key={tab.id}
              id={`tab-${tab.id}`}
              role="tab"
              aria-selected={isActive}
              onClick={() => setActiveTab(tab.id)}
              className={`
                flex items-center gap-2 px-6 py-4 text-sm font-medium transition-colors
                border-b-2 -mb-px
                ${
                  isActive
                    ? "border-medical-primary text-medical-primary bg-blue-50"
                    : "border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-50"
                }
              `}
              data-testid={`tab-${tab.id}`}
            >
              <Icon className="w-5 h-5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
};

export default TabBar;
