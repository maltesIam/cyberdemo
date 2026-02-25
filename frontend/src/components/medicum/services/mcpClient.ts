/**
 * MCP Client Service - OpenClaw Gateway Protocol
 * Handles WebSocket communication with the gateway for PIA control
 */

import { useConnectionStore } from "../stores/connectionStore";
import { useTabStore } from "../stores/tabStore";
import type { MCPMessage, MCPResponse, TabId } from "../types";

/** Gateway request frame format */
interface GatewayRequestFrame {
  type: "req";
  id: string;
  method: string;
  params?: unknown;
}

/** Gateway response frame format */
interface GatewayResponseFrame {
  type: "res";
  id: string;
  ok: boolean;
  payload?: unknown;
  error?: { code: string; message: string };
}

/** Gateway event frame format */
interface GatewayEventFrame {
  type: "event";
  event: string;
  payload?: unknown;
}

type PendingRequest = {
  resolve: (value: unknown) => void;
  reject: (error: Error) => void;
};

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 11)}`;
}

class MCPClient {
  private ws: WebSocket | null = null;
  private url: string;
  private token: string;
  private reconnectTimeout: ReturnType<typeof setTimeout> | null = null;
  private connectTimeout: ReturnType<typeof setTimeout> | null = null;
  private pendingRequests = new Map<string, PendingRequest>();
  private authenticated = false;
  private connectSent = false;
  private shouldReconnect = true;

  constructor() {
    this.url = import.meta.env?.VITE_GATEWAY_URL || "ws://localhost:18789/gateway";
    this.token = import.meta.env?.VITE_GATEWAY_TOKEN || "";
  }

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN || this.ws?.readyState === WebSocket.CONNECTING) {
      return;
    }

    this.shouldReconnect = true;
    this.authenticated = false;
    this.connectSent = false;
    useConnectionStore.getState().setStatus("connecting");

    try {
      this.ws = new WebSocket(this.url);

      this.ws.addEventListener("open", () => {
        console.log("[MCP] WebSocket connected, sending connect...");
        this.queueConnect();
      });

      this.ws.addEventListener("message", (event) => {
        this.handleMessage(event.data);
      });

      this.ws.addEventListener("error", (error) => {
        console.error("[MCP] WebSocket error:", error);
        useConnectionStore.getState().setStatus("error");
        useConnectionStore.getState().setError("Connection error");
      });

      this.ws.addEventListener("close", () => {
        console.log("[MCP] WebSocket closed");
        this.authenticated = false;
        this.flushPending(new Error("Connection closed"));
        useConnectionStore.getState().setStatus("disconnected");
        if (this.shouldReconnect) {
          this.scheduleReconnect();
        }
      });
    } catch (error) {
      console.error("[MCP] Failed to connect:", error);
      useConnectionStore.getState().setStatus("error");
    }
  }

  private queueConnect(): void {
    this.connectSent = false;
    this.clearConnectTimeout();
    // Wait a bit for challenge event, otherwise send connect
    this.connectTimeout = setTimeout(() => {
      void this.sendConnect();
    }, 750);
  }

  private clearConnectTimeout(): void {
    if (this.connectTimeout) {
      clearTimeout(this.connectTimeout);
      this.connectTimeout = null;
    }
  }

  private async sendConnect(): Promise<void> {
    if (this.connectSent || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
      return;
    }
    this.connectSent = true;
    this.clearConnectTimeout();

    // OpenClaw gateway connect params format
    // client.id must be 'openclaw-control-ui' for control UI clients
    const params = {
      minProtocol: 3,
      maxProtocol: 3,
      client: {
        id: "openclaw-control-ui",
        version: "1.0.0",
        platform: navigator?.platform ?? "web",
        mode: "webchat",
        instanceId: generateId(),
      },
      role: "operator",
      scopes: ["operator.admin"],
      caps: [],
      auth: this.token ? { token: this.token } : undefined,
      userAgent: navigator?.userAgent ?? "MedicumDemo",
      locale: navigator?.language ?? "es",
    };

    try {
      const hello = await this.requestInternal<{ type: string }>("connect", params);
      if (hello?.type === "hello-ok") {
        this.authenticated = true;
        useConnectionStore.getState().setStatus("connected");
        useConnectionStore.getState().resetReconnectAttempts();
        console.log("[MCP] Gateway authenticated successfully");
      }
    } catch (error) {
      console.error("[MCP] Connect failed:", error);
      useConnectionStore.getState().setStatus("error");
      useConnectionStore
        .getState()
        .setError(error instanceof Error ? error.message : "Connect failed");
      this.ws?.close(4008, "connect failed");
    }
  }

  /**
   * Internal request that works before authenticated
   */
  private async requestInternal<T = unknown>(method: string, params?: unknown): Promise<T> {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error("WebSocket not open");
    }

    const id = generateId();
    const frame: GatewayRequestFrame = {
      type: "req",
      id,
      method,
      params,
    };

    return new Promise<T>((resolve, reject) => {
      this.pendingRequests.set(id, {
        resolve: resolve as (value: unknown) => void,
        reject,
      });
      this.ws!.send(JSON.stringify(frame));
    });
  }

  /**
   * Send a request to the gateway (requires authentication)
   */
  async request<T = unknown>(method: string, params?: unknown): Promise<T> {
    if (!this.ws || !this.authenticated) {
      throw new Error("Gateway not connected");
    }
    return this.requestInternal<T>(method, params);
  }

  private handleMessage(data: string): void {
    let parsed: unknown;
    try {
      parsed = JSON.parse(data);
    } catch {
      console.error("[MCP] Failed to parse message");
      return;
    }

    const frame = parsed as { type?: string };

    // Handle events
    if (frame.type === "event") {
      const evt = parsed as GatewayEventFrame;

      // Handle connect challenge
      if (evt.event === "connect.challenge") {
        const payload = evt.payload as { nonce?: string } | undefined;
        if (payload?.nonce) {
          void this.sendConnect();
        }
        return;
      }

      // Handle MCP commands from PIA
      if (evt.event === "mcp.command") {
        this.handleMCPCommand(evt);
        return;
      }

      console.log("[MCP] Event:", evt.event, evt.payload);
      return;
    }

    // Handle responses
    if (frame.type === "res") {
      const res = parsed as GatewayResponseFrame;
      const pending = this.pendingRequests.get(res.id);
      if (pending) {
        this.pendingRequests.delete(res.id);
        if (res.ok) {
          pending.resolve(res.payload);
        } else {
          pending.reject(new Error(res.error?.message ?? "Request failed"));
        }
      }
      return;
    }

    console.log("[MCP] Unknown frame:", parsed);
  }

  private handleMCPCommand(evt: GatewayEventFrame): void {
    const params = evt.payload as MCPMessage | undefined;
    if (!params) {
      return;
    }

    let response: MCPResponse;

    try {
      switch (params.command) {
        case "navigate_to_tab":
          response = this.handleNavigateToTab(params.params as { tab: string });
          break;

        case "get_state":
          response = this.handleGetState();
          break;

        case "fill_field":
          response = this.handleFillField(params.params as { field_id: string; value: string });
          break;

        case "click_element":
          response = this.handleClickElement(params.params as { element_id: string });
          break;

        default:
          response = {
            id: "",
            success: false,
            error: `Unknown command: ${params.command}`,
          };
      }
    } catch (error) {
      response = {
        id: "",
        success: false,
        error: error instanceof Error ? error.message : "Command execution failed",
      };
    }

    console.log("[MCP] Command response:", response);
  }

  private handleNavigateToTab(params: { tab: string }): MCPResponse {
    const tabStore = useTabStore.getState();
    const tabId = params.tab as TabId;

    if (!tabStore.isValidTab(tabId)) {
      return {
        id: "",
        success: false,
        error: `Invalid tab: ${params.tab}. Valid tabs: consulta, historia, codificacion, visor`,
      };
    }

    tabStore.setActiveTab(tabId);

    return {
      id: "",
      success: true,
      data: { activeTab: tabId },
    };
  }

  private handleGetState(): MCPResponse {
    const tabStore = useTabStore.getState();

    return {
      id: "",
      success: true,
      data: {
        activeTab: tabStore.activeTab,
        availableTabs: tabStore.tabs.map((t) => t.id),
        connected: useConnectionStore.getState().status === "connected",
      },
    };
  }

  private handleFillField(params: { field_id: string; value: string }): MCPResponse {
    const element = document.getElementById(params.field_id) as
      | HTMLInputElement
      | HTMLTextAreaElement;

    if (!element) {
      return {
        id: "",
        success: false,
        error: `Element not found: ${params.field_id}`,
      };
    }

    element.value = params.value;
    element.dispatchEvent(new Event("input", { bubbles: true }));

    return {
      id: "",
      success: true,
      data: { field_id: params.field_id, value: params.value },
    };
  }

  private handleClickElement(params: { element_id: string }): MCPResponse {
    const element = document.getElementById(params.element_id);

    if (!element) {
      return {
        id: "",
        success: false,
        error: `Element not found: ${params.element_id}`,
      };
    }

    element.click();

    return {
      id: "",
      success: true,
      data: { element_id: params.element_id },
    };
  }

  private flushPending(error: Error): void {
    for (const [, pending] of this.pendingRequests) {
      pending.reject(error);
    }
    this.pendingRequests.clear();
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }

    const attempts = useConnectionStore.getState().reconnectAttempts;
    const delay = Math.min(800 * Math.pow(1.7, attempts), 15000);

    console.log(`[MCP] Reconnecting in ${Math.round(delay)}ms (attempt ${attempts + 1})`);

    this.reconnectTimeout = setTimeout(() => {
      useConnectionStore.getState().incrementReconnectAttempts();
      this.connect();
    }, delay);
  }

  disconnect(): void {
    this.shouldReconnect = false;
    this.clearConnectTimeout();

    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    this.authenticated = false;
    useConnectionStore.getState().setStatus("disconnected");
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN && this.authenticated;
  }
}

// Singleton instance
export const mcpClient = new MCPClient();
