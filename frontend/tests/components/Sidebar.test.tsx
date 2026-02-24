/**
 * Sidebar Component Tests
 *
 * Tests for the navigation sidebar including:
 * - Menu items rendering
 * - Navigation links
 * - Active state styling
 * - Threats menu item (newly added)
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { BrowserRouter, MemoryRouter } from "react-router-dom";
import { Sidebar } from "../../src/components/Sidebar";

// Helper to render with router
const renderWithRouter = (initialRoute = "/") => {
  return render(
    <MemoryRouter initialEntries={[initialRoute]}>
      <Sidebar />
    </MemoryRouter>
  );
};

describe("Sidebar", () => {
  describe("Menu Items Rendering", () => {
    it("should render the CyberDemo logo and title", () => {
      renderWithRouter();
      expect(screen.getByText("CyberDemo")).toBeInTheDocument();
      expect(screen.getByText("SOC Dashboard")).toBeInTheDocument();
    });

    it("should render Command Center menu item", () => {
      renderWithRouter();
      expect(screen.getByText("Command Center")).toBeInTheDocument();
    });

    it("should render Generation menu item", () => {
      renderWithRouter();
      expect(screen.getByText("Generation")).toBeInTheDocument();
    });

    it("should render Dashboard menu item", () => {
      renderWithRouter();
      expect(screen.getByText("Dashboard")).toBeInTheDocument();
    });

    it("should render Assets menu item", () => {
      renderWithRouter();
      expect(screen.getByText("Assets")).toBeInTheDocument();
    });

    it("should render Incidents menu item", () => {
      renderWithRouter();
      expect(screen.getByText("Incidents")).toBeInTheDocument();
    });

    it("should render Detections menu item", () => {
      renderWithRouter();
      expect(screen.getByText("Detections")).toBeInTheDocument();
    });

    it("should render CTEM menu item", () => {
      renderWithRouter();
      expect(screen.getByText("CTEM")).toBeInTheDocument();
    });

    it("should render Vulnerabilities menu item", () => {
      renderWithRouter();
      expect(screen.getByText("Vulnerabilities")).toBeInTheDocument();
    });

    it("should render Threat Intel menu item", () => {
      renderWithRouter();
      expect(screen.getByText("Threat Intel")).toBeInTheDocument();
    });

    it("should render Timeline menu item", () => {
      renderWithRouter();
      expect(screen.getByText("Timeline")).toBeInTheDocument();
    });

    it("should render Postmortems menu item", () => {
      renderWithRouter();
      expect(screen.getByText("Postmortems")).toBeInTheDocument();
    });

    it("should render Tickets menu item", () => {
      renderWithRouter();
      expect(screen.getByText("Tickets")).toBeInTheDocument();
    });

    it("should render Collaboration menu item", () => {
      renderWithRouter();
      expect(screen.getByText("Collaboration")).toBeInTheDocument();
    });

    it("should render Configuration menu item", () => {
      renderWithRouter();
      expect(screen.getByText("Configuration")).toBeInTheDocument();
    });

    it("should render Audit Log menu item", () => {
      renderWithRouter();
      expect(screen.getByText("Audit Log")).toBeInTheDocument();
    });
  });

  describe("Navigation Links", () => {
    it("should have correct link to /vulnerabilities", () => {
      renderWithRouter();
      const link = screen.getByText("Vulnerabilities").closest("a");
      expect(link).toHaveAttribute("href", "/vulnerabilities");
    });

    it("should have correct link to /threats", () => {
      renderWithRouter();
      const link = screen.getByText("Threat Intel").closest("a");
      expect(link).toHaveAttribute("href", "/threats");
    });

    it("should have correct link to /surface", () => {
      renderWithRouter();
      const link = screen.getByText("Command Center").closest("a");
      expect(link).toHaveAttribute("href", "/surface");
    });

    it("should have correct link to /generation", () => {
      renderWithRouter();
      const link = screen.getByText("Generation").closest("a");
      expect(link).toHaveAttribute("href", "/generation");
    });

    it("should have correct link to /dashboard", () => {
      renderWithRouter();
      const link = screen.getByText("Dashboard").closest("a");
      expect(link).toHaveAttribute("href", "/dashboard");
    });

    it("should have correct link to /incidents", () => {
      renderWithRouter();
      const link = screen.getByText("Incidents").closest("a");
      expect(link).toHaveAttribute("href", "/incidents");
    });

    it("should have correct link to /ctem", () => {
      renderWithRouter();
      const link = screen.getByText("CTEM").closest("a");
      expect(link).toHaveAttribute("href", "/ctem");
    });
  });

  describe("Active State Styling", () => {
    it("should highlight Vulnerabilities when on /vulnerabilities route", () => {
      renderWithRouter("/vulnerabilities");
      const link = screen.getByText("Vulnerabilities").closest("a");
      expect(link).toHaveClass("bg-cyan-600");
    });

    it("should highlight Threat Intel when on /threats route", () => {
      renderWithRouter("/threats");
      const link = screen.getByText("Threat Intel").closest("a");
      expect(link).toHaveClass("bg-cyan-600");
    });

    it("should not highlight other items when on /threats route", () => {
      renderWithRouter("/threats");
      const vulnLink = screen.getByText("Vulnerabilities").closest("a");
      expect(vulnLink).not.toHaveClass("bg-cyan-600");
    });

    it("should highlight Generation when on /generation route", () => {
      renderWithRouter("/generation");
      const link = screen.getByText("Generation").closest("a");
      expect(link).toHaveClass("bg-cyan-600");
    });
  });

  describe("Menu Structure", () => {
    it("should render all 16 navigation items", () => {
      renderWithRouter();
      const navLinks = screen.getAllByRole("link");
      // 16 nav items (including Simulation)
      expect(navLinks.length).toBe(16);
    });

    it("should have Threat Intel positioned after Vulnerabilities in the menu", () => {
      renderWithRouter();
      const navLinks = screen.getAllByRole("link");
      const vulnIndex = navLinks.findIndex(
        (link) => link.textContent?.includes("Vulnerabilities")
      );
      const threatIndex = navLinks.findIndex(
        (link) => link.textContent?.includes("Threat Intel")
      );
      expect(threatIndex).toBe(vulnIndex + 1);
    });

    it("should have Threat Intel positioned before Timeline in the menu", () => {
      renderWithRouter();
      const navLinks = screen.getAllByRole("link");
      const threatIndex = navLinks.findIndex(
        (link) => link.textContent?.includes("Threat Intel")
      );
      const timelineIndex = navLinks.findIndex(
        (link) => link.textContent?.includes("Timeline")
      );
      expect(threatIndex).toBe(timelineIndex - 1);
    });
  });

  describe("User Info Section", () => {
    it("should display SOC Analyst user role", () => {
      renderWithRouter();
      expect(screen.getByText("SOC Analyst")).toBeInTheDocument();
    });

    it("should display Demo Mode indicator", () => {
      renderWithRouter();
      expect(screen.getByText("Demo Mode")).toBeInTheDocument();
    });
  });

  describe("Icons", () => {
    it("should render SVG icon for each menu item", () => {
      renderWithRouter();
      const svgIcons = document.querySelectorAll("nav svg");
      expect(svgIcons.length).toBeGreaterThanOrEqual(15);
    });

    it("should have Threat Intel icon with correct classes", () => {
      renderWithRouter();
      const threatLink = screen.getByText("Threat Intel").closest("a");
      const svg = threatLink?.querySelector("svg");
      expect(svg).toHaveClass("w-5", "h-5");
    });
  });

  describe("Accessibility", () => {
    it("should have navigation landmark", () => {
      renderWithRouter();
      expect(screen.getByRole("navigation")).toBeInTheDocument();
    });

    it("should have clickable links for all menu items", () => {
      renderWithRouter();
      const links = screen.getAllByRole("link");
      links.forEach((link) => {
        expect(link).toHaveAttribute("href");
      });
    });
  });
});

describe("Sidebar Integration with Router", () => {
  it("should render correctly within BrowserRouter", () => {
    render(
      <BrowserRouter>
        <Sidebar />
      </BrowserRouter>
    );
    expect(screen.getByText("Threat Intel")).toBeInTheDocument();
    expect(screen.getByText("Vulnerabilities")).toBeInTheDocument();
  });
});
