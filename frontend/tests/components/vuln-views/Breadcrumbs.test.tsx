/**
 * Breadcrumbs Tests - TDD
 *
 * Tests for the reusable Breadcrumbs component
 * - Renders navigation links
 * - Proper styling
 * - Current page indicator
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import React from "react";

// ============================================================================
// Test Utilities
// ============================================================================

import { Breadcrumbs } from "../../../src/components/vuln-views/Breadcrumbs";

function BreadcrumbsWrapper({ items }: { items: Array<{ label: string; href?: string }> }) {
  return (
    <BrowserRouter>
      <Breadcrumbs items={items} />
    </BrowserRouter>
  );
}

// ============================================================================
// Breadcrumbs Tests
// ============================================================================

describe("Breadcrumbs Component", () => {
  describe("Basic Rendering", () => {
    it("should render navigation element with breadcrumb label", async () => {
      render(
        <BreadcrumbsWrapper
          items={[
            { label: "Home", href: "/" },
            { label: "Vulnerabilities", href: "/vulnerabilities" },
            { label: "CVE-2024-0001" },
          ]}
        />
      );

      const nav = await screen.findByRole("navigation", { name: /breadcrumb/i });
      expect(nav).toBeInTheDocument();
    });

    it("should render all breadcrumb items", async () => {
      render(
        <BreadcrumbsWrapper
          items={[
            { label: "Home", href: "/" },
            { label: "Vulnerabilities", href: "/vulnerabilities" },
            { label: "CVE-2024-0001" },
          ]}
        />
      );

      expect(await screen.findByText("Home")).toBeInTheDocument();
      expect(screen.getByText("Vulnerabilities")).toBeInTheDocument();
      expect(screen.getByText("CVE-2024-0001")).toBeInTheDocument();
    });
  });

  describe("Links and Current Page", () => {
    it("should render items with href as links", async () => {
      render(
        <BreadcrumbsWrapper
          items={[
            { label: "Home", href: "/" },
            { label: "Vulnerabilities", href: "/vulnerabilities" },
            { label: "Current Page" },
          ]}
        />
      );

      const homeLink = await screen.findByRole("link", { name: "Home" });
      expect(homeLink).toHaveAttribute("href", "/");

      const vulnLink = screen.getByRole("link", { name: "Vulnerabilities" });
      expect(vulnLink).toHaveAttribute("href", "/vulnerabilities");
    });

    it("should render last item without href as text (not link)", async () => {
      render(
        <BreadcrumbsWrapper
          items={[
            { label: "Home", href: "/" },
            { label: "Current Page" },
          ]}
        />
      );

      await screen.findByText("Home");

      // Current page should not be a link
      const currentPage = screen.getByText("Current Page");
      expect(currentPage.tagName).not.toBe("A");
    });

    it("should apply current page styling to last item", async () => {
      render(
        <BreadcrumbsWrapper
          items={[
            { label: "Home", href: "/" },
            { label: "Current Page" },
          ]}
        />
      );

      const currentPage = await screen.findByText("Current Page");
      // Should have different styling (e.g., text-white vs text-gray-400)
      expect(currentPage.className).toMatch(/text-white|current/i);
    });
  });

  describe("Separators", () => {
    it("should render separators between items", async () => {
      render(
        <BreadcrumbsWrapper
          items={[
            { label: "Home", href: "/" },
            { label: "Vulnerabilities", href: "/vulnerabilities" },
            { label: "CVE-2024-0001" },
          ]}
        />
      );

      // Wait for component to load
      await screen.findByText("Home");

      // Should have separator elements (chevrons or slashes)
      const separators = screen.getAllByText(/[>\/]/);
      // Should have n-1 separators for n items
      expect(separators.length).toBeGreaterThanOrEqual(2);
    });
  });

  describe("Accessibility", () => {
    it("should have proper aria-label", async () => {
      render(
        <BreadcrumbsWrapper
          items={[
            { label: "Home", href: "/" },
            { label: "Page" },
          ]}
        />
      );

      const nav = await screen.findByRole("navigation", { name: /breadcrumb/i });
      expect(nav).toHaveAttribute("aria-label");
    });

    it("should mark current page with aria-current", async () => {
      render(
        <BreadcrumbsWrapper
          items={[
            { label: "Home", href: "/" },
            { label: "Current Page" },
          ]}
        />
      );

      const currentPage = await screen.findByText("Current Page");
      expect(currentPage).toHaveAttribute("aria-current", "page");
    });
  });

  describe("Edge Cases", () => {
    it("should handle single item breadcrumb", async () => {
      render(
        <BreadcrumbsWrapper items={[{ label: "Home" }]} />
      );

      expect(await screen.findByText("Home")).toBeInTheDocument();
    });

    it("should handle empty items array gracefully", async () => {
      render(<BreadcrumbsWrapper items={[]} />);

      const nav = await screen.findByRole("navigation", { name: /breadcrumb/i });
      expect(nav).toBeInTheDocument();
    });
  });
});
