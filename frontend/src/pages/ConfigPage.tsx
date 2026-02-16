import { useState, useEffect } from "react";
import clsx from "clsx";
import {
  usePolicyConfig,
  useUpdatePolicyConfig,
  useNotificationConfig,
  useUpdateNotificationConfig,
  useIntegrationConfig,
  useUpdateIntegrationConfig,
  useResetConfig,
} from "../hooks/useApi";
import { useToast } from "../utils/toast";
import type { PolicyConfig, NotificationConfig, IntegrationConfig } from "../types";

// ============================================================================
// Slider Component
// ============================================================================

interface SliderProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  description?: string;
}

function Slider({ label, value, onChange, min = 0, max = 100, description }: SliderProps) {
  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <label className="text-sm font-medium text-gray-300">{label}</label>
        <span className="text-sm font-mono text-cyan-400">{value}%</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-cyan-500"
      />
      {description && <p className="text-xs text-gray-500">{description}</p>}
    </div>
  );
}

// ============================================================================
// Toggle Component
// ============================================================================

interface ToggleProps {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  description?: string;
}

function Toggle({ label, checked, onChange, description }: ToggleProps) {
  return (
    <div className="flex items-center justify-between py-2">
      <div>
        <span className="text-sm font-medium text-gray-300">{label}</span>
        {description && <p className="text-xs text-gray-500 mt-0.5">{description}</p>}
      </div>
      <button
        type="button"
        onClick={() => onChange(!checked)}
        className={clsx(
          "relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2 focus:ring-offset-gray-900",
          checked ? "bg-cyan-600" : "bg-gray-600",
        )}
      >
        <span
          className={clsx(
            "pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out",
            checked ? "translate-x-5" : "translate-x-0",
          )}
        />
      </button>
    </div>
  );
}

// ============================================================================
// Tag List Editor Component
// ============================================================================

interface TagListEditorProps {
  label: string;
  tags: string[];
  onChange: (tags: string[]) => void;
  description?: string;
  placeholder?: string;
}

function TagListEditor({
  label,
  tags,
  onChange,
  description,
  placeholder = "Add tag...",
}: TagListEditorProps) {
  const [inputValue, setInputValue] = useState("");

  const handleAdd = () => {
    const trimmed = inputValue.trim();
    if (trimmed && !tags.includes(trimmed)) {
      onChange([...tags, trimmed]);
      setInputValue("");
    }
  };

  const handleRemove = (tag: string) => {
    onChange(tags.filter((t) => t !== tag));
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleAdd();
    }
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-300">{label}</label>
      {description && <p className="text-xs text-gray-500">{description}</p>}
      <div className="flex flex-wrap gap-2 mb-2">
        {tags.map((tag) => (
          <span
            key={tag}
            className="inline-flex items-center gap-1 px-2 py-1 bg-gray-700 text-gray-300 rounded text-sm"
          >
            {tag}
            <button onClick={() => handleRemove(tag)} className="text-gray-500 hover:text-red-400">
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </span>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-500 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500"
        />
        <button
          onClick={handleAdd}
          className="px-3 py-2 bg-cyan-600 text-white rounded-lg hover:bg-cyan-500 text-sm"
        >
          Add
        </button>
      </div>
    </div>
  );
}

// ============================================================================
// Text Input Component
// ============================================================================

interface TextInputProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  type?: "text" | "url" | "email";
  description?: string;
  masked?: boolean;
}

function TextInput({
  label,
  value,
  onChange,
  placeholder,
  type = "text",
  description,
  masked,
}: TextInputProps) {
  const [showValue, setShowValue] = useState(!masked);

  return (
    <div className="space-y-1">
      <label className="block text-sm font-medium text-gray-300">{label}</label>
      {description && <p className="text-xs text-gray-500">{description}</p>}
      <div className="relative">
        <input
          type={showValue ? type : "password"}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-500 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500"
        />
        {masked && (
          <button
            type="button"
            onClick={() => setShowValue(!showValue)}
            className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
          >
            {showValue ? (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
                />
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                />
              </svg>
            )}
          </button>
        )}
      </div>
    </div>
  );
}

// ============================================================================
// Section Component
// ============================================================================

interface SectionProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  icon?: React.ReactNode;
}

function Section({ title, description, children, icon }: SectionProps) {
  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
      <div className="flex items-start gap-3 mb-4">
        {icon && <div className="text-cyan-400 mt-0.5">{icon}</div>}
        <div>
          <h3 className="text-lg font-semibold text-white">{title}</h3>
          {description && <p className="text-sm text-gray-400 mt-1">{description}</p>}
        </div>
      </div>
      <div className="space-y-4">{children}</div>
    </div>
  );
}

// ============================================================================
// Main ConfigPage Component
// ============================================================================

export function ConfigPage() {
  const { showToast } = useToast();

  // Fetch current configurations
  const { data: policyData, isLoading: policyLoading } = usePolicyConfig();
  const { data: notificationData, isLoading: notificationLoading } = useNotificationConfig();
  const { data: integrationData, isLoading: integrationLoading } = useIntegrationConfig();

  // Mutations
  const updatePolicy = useUpdatePolicyConfig();
  const updateNotification = useUpdateNotificationConfig();
  const updateIntegration = useUpdateIntegrationConfig();
  const resetConfig = useResetConfig();

  // Local state for form editing
  const [policyForm, setPolicyForm] = useState<Partial<PolicyConfig>>({});
  const [notificationForm, setNotificationForm] = useState<Partial<NotificationConfig>>({});
  const [integrationForm, setIntegrationForm] = useState<Partial<IntegrationConfig>>({});
  const [hasChanges, setHasChanges] = useState(false);

  // Initialize forms when data loads
  useEffect(() => {
    if (policyData) {
      setPolicyForm({
        auto_contain_threshold: policyData.auto_contain_threshold,
        false_positive_threshold: policyData.false_positive_threshold,
        auto_contain_enabled: policyData.auto_contain_enabled,
        vip_list: policyData.vip_list,
        critical_tags: policyData.critical_tags,
      });
    }
  }, [policyData]);

  useEffect(() => {
    if (notificationData) {
      setNotificationForm({
        slack_enabled: notificationData.slack_enabled,
        teams_enabled: notificationData.teams_enabled,
        email_enabled: notificationData.email_enabled,
        webhook_enabled: notificationData.webhook_enabled,
        slack_webhook_url: notificationData.slack_webhook_url ?? "",
        teams_webhook_url: notificationData.teams_webhook_url ?? "",
        email_recipients: notificationData.email_recipients,
        custom_webhook_url: notificationData.custom_webhook_url ?? "",
        notify_on_critical: notificationData.notify_on_critical,
        notify_on_high: notificationData.notify_on_high,
        notify_on_medium: notificationData.notify_on_medium,
        notify_on_containment: notificationData.notify_on_containment,
        notify_on_approval_needed: notificationData.notify_on_approval_needed,
        template_style: notificationData.template_style,
      });
    }
  }, [notificationData]);

  useEffect(() => {
    if (integrationData) {
      setIntegrationForm({
        enabled_integrations: integrationData.enabled_integrations,
      });
    }
  }, [integrationData]);

  const handlePolicyChange = <K extends keyof PolicyConfig>(key: K, value: PolicyConfig[K]) => {
    setPolicyForm((prev) => ({ ...prev, [key]: value }));
    setHasChanges(true);
  };

  const handleNotificationChange = <K extends keyof NotificationConfig>(
    key: K,
    value: NotificationConfig[K],
  ) => {
    setNotificationForm((prev) => ({ ...prev, [key]: value }));
    setHasChanges(true);
  };

  const handleSaveAll = async () => {
    try {
      // Save policy config
      if (Object.keys(policyForm).length > 0) {
        await updatePolicy.mutateAsync(policyForm);
      }

      // Save notification config
      if (Object.keys(notificationForm).length > 0) {
        await updateNotification.mutateAsync(notificationForm);
      }

      // Save integration config
      if (Object.keys(integrationForm).length > 0) {
        await updateIntegration.mutateAsync(integrationForm);
      }

      showToast("success", "Configuration saved successfully");
      setHasChanges(false);
    } catch (error) {
      showToast("error", `Failed to save configuration: ${(error as Error).message}`);
    }
  };

  const handleReset = async () => {
    if (
      !window.confirm(
        "Are you sure you want to reset all configuration to defaults? This cannot be undone.",
      )
    ) {
      return;
    }

    try {
      await resetConfig.mutateAsync();
      showToast("success", "Configuration reset to defaults");
      setHasChanges(false);
    } catch (error) {
      showToast("error", `Failed to reset configuration: ${(error as Error).message}`);
    }
  };

  const isLoading = policyLoading || notificationLoading || integrationLoading;
  const isSaving =
    updatePolicy.isPending || updateNotification.isPending || updateIntegration.isPending;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <svg className="w-8 h-8 animate-spin text-cyan-500" fill="none" viewBox="0 0 24 24">
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
          />
        </svg>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Configuration</h1>
          <p className="text-gray-400 mt-1">
            Manage policy engine, notifications, and integrations
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleReset}
            disabled={isSaving}
            className="px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 disabled:opacity-50 transition-colors"
          >
            Reset to Defaults
          </button>
          <button
            onClick={handleSaveAll}
            disabled={isSaving || !hasChanges}
            className={clsx(
              "px-4 py-2 rounded-lg transition-colors flex items-center gap-2",
              hasChanges
                ? "bg-cyan-600 text-white hover:bg-cyan-500"
                : "bg-gray-700 text-gray-400 cursor-not-allowed",
            )}
          >
            {isSaving && (
              <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                />
              </svg>
            )}
            Save Changes
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Policy Engine Settings */}
        <Section
          title="Policy Engine"
          description="Configure auto-containment thresholds and asset handling"
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
              />
            </svg>
          }
        >
          <Toggle
            label="Auto-Containment Enabled"
            checked={policyForm.auto_contain_enabled ?? true}
            onChange={(v) => handlePolicyChange("auto_contain_enabled", v)}
            description="Automatically contain threats above threshold"
          />

          <Slider
            label="Auto-Containment Threshold"
            value={policyForm.auto_contain_threshold ?? 90}
            onChange={(v) => handlePolicyChange("auto_contain_threshold", v)}
            description="Confidence score required for automatic containment"
          />

          <Slider
            label="False Positive Threshold"
            value={policyForm.false_positive_threshold ?? 50}
            onChange={(v) => handlePolicyChange("false_positive_threshold", v)}
            description="Below this threshold, alerts are marked as false positive"
          />

          <TagListEditor
            label="VIP Asset List"
            tags={policyForm.vip_list ?? []}
            onChange={(v) => handlePolicyChange("vip_list", v)}
            description="Assets requiring manual approval for containment"
            placeholder="Enter asset hostname or ID..."
          />

          <TagListEditor
            label="Critical Tags"
            tags={policyForm.critical_tags ?? []}
            onChange={(v) => handlePolicyChange("critical_tags", v)}
            description="Asset tags that require human approval"
            placeholder="Enter tag name..."
          />
        </Section>

        {/* Notification Settings */}
        <Section
          title="Notifications"
          description="Configure notification channels and triggers"
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
              />
            </svg>
          }
        >
          <div className="border-b border-gray-700 pb-4">
            <h4 className="text-sm font-medium text-gray-400 mb-3">Channels</h4>
            <Toggle
              label="Slack"
              checked={notificationForm.slack_enabled ?? false}
              onChange={(v) => handleNotificationChange("slack_enabled", v)}
            />
            {notificationForm.slack_enabled && (
              <div className="mt-2 ml-4">
                <TextInput
                  label="Slack Webhook URL"
                  value={notificationForm.slack_webhook_url ?? ""}
                  onChange={(v) => handleNotificationChange("slack_webhook_url", v)}
                  placeholder="https://hooks.slack.com/services/..."
                  type="url"
                  masked
                />
              </div>
            )}

            <Toggle
              label="Microsoft Teams"
              checked={notificationForm.teams_enabled ?? false}
              onChange={(v) => handleNotificationChange("teams_enabled", v)}
            />
            {notificationForm.teams_enabled && (
              <div className="mt-2 ml-4">
                <TextInput
                  label="Teams Webhook URL"
                  value={notificationForm.teams_webhook_url ?? ""}
                  onChange={(v) => handleNotificationChange("teams_webhook_url", v)}
                  placeholder="https://outlook.office.com/webhook/..."
                  type="url"
                  masked
                />
              </div>
            )}

            <Toggle
              label="Email"
              checked={notificationForm.email_enabled ?? false}
              onChange={(v) => handleNotificationChange("email_enabled", v)}
            />
            {notificationForm.email_enabled && (
              <div className="mt-2 ml-4">
                <TagListEditor
                  label="Email Recipients"
                  tags={notificationForm.email_recipients ?? []}
                  onChange={(v) => handleNotificationChange("email_recipients", v)}
                  placeholder="email@example.com"
                />
              </div>
            )}

            <Toggle
              label="Custom Webhook"
              checked={notificationForm.webhook_enabled ?? false}
              onChange={(v) => handleNotificationChange("webhook_enabled", v)}
            />
            {notificationForm.webhook_enabled && (
              <div className="mt-2 ml-4">
                <TextInput
                  label="Webhook URL"
                  value={notificationForm.custom_webhook_url ?? ""}
                  onChange={(v) => handleNotificationChange("custom_webhook_url", v)}
                  placeholder="https://your-webhook-endpoint.com/..."
                  type="url"
                  masked
                />
              </div>
            )}
          </div>

          <div className="pt-2">
            <h4 className="text-sm font-medium text-gray-400 mb-3">Notification Triggers</h4>
            <Toggle
              label="Critical Incidents"
              checked={notificationForm.notify_on_critical ?? true}
              onChange={(v) => handleNotificationChange("notify_on_critical", v)}
            />
            <Toggle
              label="High Severity Incidents"
              checked={notificationForm.notify_on_high ?? true}
              onChange={(v) => handleNotificationChange("notify_on_high", v)}
            />
            <Toggle
              label="Medium Severity Incidents"
              checked={notificationForm.notify_on_medium ?? false}
              onChange={(v) => handleNotificationChange("notify_on_medium", v)}
            />
            <Toggle
              label="Auto-Containment Actions"
              checked={notificationForm.notify_on_containment ?? true}
              onChange={(v) => handleNotificationChange("notify_on_containment", v)}
            />
            <Toggle
              label="Approval Requests"
              checked={notificationForm.notify_on_approval_needed ?? true}
              onChange={(v) => handleNotificationChange("notify_on_approval_needed", v)}
            />
          </div>

          <div className="pt-2">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Notification Template
            </label>
            <select
              value={notificationForm.template_style ?? "detailed"}
              onChange={(e) => handleNotificationChange("template_style", e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
            >
              <option value="detailed">Detailed (Full incident info)</option>
              <option value="summary">Summary (Brief overview)</option>
              <option value="minimal">Minimal (Alert only)</option>
            </select>
          </div>
        </Section>

        {/* API Keys Section */}
        <Section
          title="API Keys"
          description="Manage API keys for external integrations"
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"
              />
            </svg>
          }
        >
          <div className="space-y-4">
            {integrationData?.api_keys && Object.keys(integrationData.api_keys).length > 0 ? (
              Object.entries(integrationData.api_keys).map(([service, maskedKey]) => (
                <div
                  key={service}
                  className="flex items-center justify-between p-3 bg-gray-700 rounded-lg"
                >
                  <div>
                    <span className="text-sm font-medium text-white capitalize">{service}</span>
                    <p className="text-xs text-gray-400 font-mono">{maskedKey}</p>
                  </div>
                  <button className="text-gray-400 hover:text-cyan-400 text-sm">Update</button>
                </div>
              ))
            ) : (
              <div className="text-center py-4 text-gray-500">
                <p>No API keys configured</p>
                <p className="text-xs mt-1">API keys can be configured via the backend</p>
              </div>
            )}
          </div>
        </Section>

        {/* Integration Status */}
        <Section
          title="Integrations"
          description="External service integrations"
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z"
              />
            </svg>
          }
        >
          <div className="space-y-3">
            {[
              { id: "virustotal", name: "VirusTotal", description: "File and URL scanning" },
              { id: "shodan", name: "Shodan", description: "Internet-wide scanning" },
              { id: "misp", name: "MISP", description: "Threat intelligence sharing" },
              { id: "jira", name: "Jira", description: "Ticket management" },
              { id: "servicenow", name: "ServiceNow", description: "ITSM integration" },
            ].map((integration) => {
              const isEnabled =
                integrationForm.enabled_integrations?.includes(integration.id) ?? false;
              return (
                <div
                  key={integration.id}
                  className="flex items-center justify-between p-3 bg-gray-700 rounded-lg"
                >
                  <div>
                    <span className="text-sm font-medium text-white">{integration.name}</span>
                    <p className="text-xs text-gray-400">{integration.description}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span
                      className={clsx(
                        "text-xs px-2 py-1 rounded",
                        isEnabled ? "bg-green-900 text-green-300" : "bg-gray-600 text-gray-400",
                      )}
                    >
                      {isEnabled ? "Enabled" : "Disabled"}
                    </span>
                    <button
                      onClick={() => {
                        const current = integrationForm.enabled_integrations ?? [];
                        const updated = isEnabled
                          ? current.filter((i) => i !== integration.id)
                          : [...current, integration.id];
                        setIntegrationForm((prev) => ({ ...prev, enabled_integrations: updated }));
                        setHasChanges(true);
                      }}
                      className={clsx(
                        "text-xs px-2 py-1 rounded",
                        isEnabled
                          ? "text-red-400 hover:bg-red-900/50"
                          : "text-cyan-400 hover:bg-cyan-900/50",
                      )}
                    >
                      {isEnabled ? "Disable" : "Enable"}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </Section>
      </div>

      {/* Last Updated Info */}
      {policyData?.last_updated && (
        <div className="text-center text-xs text-gray-500">
          Last updated: {new Date(policyData.last_updated).toLocaleString()}
        </div>
      )}
    </div>
  );
}
