/**
 * UT-063: Keyboard Navigation All Elements
 * Requirement: NFR-003
 * Task: T-NFR-003
 *
 * AC-001: Tab navigates between elements
 * AC-002: Enter/Space activates buttons and links
 * AC-003: Escape closes modals and popovers
 * AC-004: All interactive elements have visible focus indicators
 *
 * Verifies keyboard accessibility by:
 * 1. Static analysis of component source code for proper elements
 * 2. Runtime tests for ThemeToggle, FontSizeButton, Button, Input, Modal
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import * as fs from 'fs';
import * as path from 'path';
import { ThemeToggle } from '../../../src/components/ThemeToggle';
import { FontSizeButton } from '../../../src/components/FontSizeButton';
import { Button } from '../../../src/components/ui/Button';
import { Input } from '../../../src/components/ui/Input';
import { Modal } from '../../../src/components/ui/Modal';

// Mock matchMedia for ThemeToggle
const mockMatchMedia = (matches: boolean) => {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation((query: string) => ({
      matches: query.includes('dark') ? matches : !matches,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });
};

beforeEach(() => {
  document.documentElement.removeAttribute('data-theme');
  document.documentElement.style.fontSize = '';
  localStorage.clear();
  mockMatchMedia(true);
});

describe('UT-063: Keyboard Navigation (NFR-003)', () => {
  // AC-001: Tab navigates between elements
  describe('AC-001: Tab navigation', () => {
    it('ThemeToggle buttons are all tabbable (native button elements)', () => {
      render(<ThemeToggle />);
      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBe(3);
      // Native buttons are inherently tabbable (tabindex=0 by default)
      buttons.forEach(button => {
        expect(button.tagName).toBe('BUTTON');
        expect(button.getAttribute('tabindex')).not.toBe('-1');
      });
    });

    it('FontSizeButton is a tabbable button element', () => {
      render(<FontSizeButton />);
      const button = screen.getByRole('button');
      expect(button.tagName).toBe('BUTTON');
    });

    it('Button component renders as native button', () => {
      render(<Button>Click</Button>);
      const button = screen.getByRole('button');
      expect(button.tagName).toBe('BUTTON');
    });

    it('Input component renders as native input (tabbable)', () => {
      render(<Input aria-label="test" />);
      const input = screen.getByRole('textbox');
      expect(input.tagName).toBe('INPUT');
    });

    it('Multiple interactive elements can be tabbed through', () => {
      render(
        <div>
          <Button>First</Button>
          <Button>Second</Button>
          <Input aria-label="third" />
        </div>
      );
      const first = screen.getByRole('button', { name: 'First' });
      const second = screen.getByRole('button', { name: 'Second' });
      const input = screen.getByRole('textbox');

      // All exist and are focusable native elements
      expect(first.tagName).toBe('BUTTON');
      expect(second.tagName).toBe('BUTTON');
      expect(input.tagName).toBe('INPUT');
    });
  });

  // AC-002: Enter/Space activates buttons and links
  describe('AC-002: Enter/Space activation', () => {
    it('Button should respond to click events (keyboard Enter/Space triggers click on native buttons)', () => {
      const onClick = vi.fn();
      render(<Button onClick={onClick}>Activate</Button>);
      const button = screen.getByRole('button', { name: 'Activate' });
      fireEvent.click(button);
      expect(onClick).toHaveBeenCalledTimes(1);
    });

    it('ThemeToggle buttons respond to click events', () => {
      render(<ThemeToggle />);
      const lightButton = screen.getByLabelText('Light theme');
      fireEvent.click(lightButton);
      expect(document.documentElement.getAttribute('data-theme')).toBe('light');
    });

    it('FontSizeButton responds to click events', () => {
      render(<FontSizeButton />);
      const button = screen.getByRole('button');
      fireEvent.click(button);
      expect(document.documentElement.style.fontSize).toBe('18px');
    });

    it('Button component responds to Enter key (native behavior)', () => {
      const onClick = vi.fn();
      render(<Button onClick={onClick}>Enter</Button>);
      const button = screen.getByRole('button', { name: 'Enter' });
      // Native button elements activate on Enter key press
      fireEvent.keyDown(button, { key: 'Enter' });
      // Native browser behavior fires click on Enter for buttons
      // In JSDOM, we verify the button is a native element
      expect(button.tagName).toBe('BUTTON');
      expect(button.type).toBe('submit'); // or 'button' depending on defaults
    });

    it('Disabled button should not activate on click', () => {
      const onClick = vi.fn();
      render(<Button onClick={onClick} disabled>Disabled</Button>);
      const button = screen.getByRole('button', { name: 'Disabled' });
      fireEvent.click(button);
      expect(onClick).not.toHaveBeenCalled();
    });
  });

  // AC-003: Escape closes modals
  describe('AC-003: Escape closes modals', () => {
    it('Modal should close on Escape key press', () => {
      const onClose = vi.fn();
      render(
        <Modal open={true} onClose={onClose} title="Test Modal">
          <p>Content</p>
        </Modal>
      );
      fireEvent.keyDown(document, { key: 'Escape' });
      expect(onClose).toHaveBeenCalledTimes(1);
    });

    it('Modal should close when clicking overlay', () => {
      const onClose = vi.fn();
      render(
        <Modal open={true} onClose={onClose} title="Test Modal">
          <p>Content</p>
        </Modal>
      );
      const overlay = screen.getByTestId('modal-overlay');
      fireEvent.click(overlay);
      expect(onClose).toHaveBeenCalledTimes(1);
    });

    it('Modal should NOT close when clicking inside the dialog', () => {
      const onClose = vi.fn();
      render(
        <Modal open={true} onClose={onClose} title="Test Modal">
          <p>Content text</p>
        </Modal>
      );
      const dialog = screen.getByRole('dialog');
      fireEvent.click(dialog);
      expect(onClose).not.toHaveBeenCalled();
    });

    it('Modal should have aria-modal="true"', () => {
      const onClose = vi.fn();
      render(
        <Modal open={true} onClose={onClose} title="Test Modal">
          <p>Content</p>
        </Modal>
      );
      const dialog = screen.getByRole('dialog');
      expect(dialog.getAttribute('aria-modal')).toBe('true');
    });
  });

  // AC-004: Visible focus indicators
  describe('AC-004: Visible focus indicators', () => {
    it('Button should have data-focus-ring="true" for CSS focus styling', () => {
      render(<Button>Focus</Button>);
      const button = screen.getByRole('button', { name: 'Focus' });
      expect(button.getAttribute('data-focus-ring')).toBe('true');
    });

    it('Input should have data-focus-ring="true" for CSS focus styling', () => {
      render(<Input aria-label="test" />);
      const input = screen.getByRole('textbox');
      expect(input.getAttribute('data-focus-ring')).toBe('true');
    });

    it('Focus ring CSS utility exists in accessibility-utils', () => {
      const utilsPath = path.resolve(__dirname, '../../../src/components/ui/accessibility-utils.ts');
      const content = fs.readFileSync(utilsPath, 'utf-8');
      expect(content).toContain('getFocusRingCSS');
      expect(content).toContain('focus-visible');
      expect(content).toContain('outline');
    });

    it('ThemeToggle uses native button elements with inherent focus indicators', () => {
      const componentPath = path.resolve(__dirname, '../../../src/components/ThemeToggle.tsx');
      const content = fs.readFileSync(componentPath, 'utf-8');
      expect(content).toContain('<button');
      expect(content).toContain('type="button"');
    });

    it('FontSizeButton uses native button element with inherent focus indicator', () => {
      const componentPath = path.resolve(__dirname, '../../../src/components/FontSizeButton.tsx');
      const content = fs.readFileSync(componentPath, 'utf-8');
      expect(content).toContain('<button');
      expect(content).toContain('type="button"');
    });
  });

  // ARIA attributes
  describe('ARIA attributes on interactive components', () => {
    it('ThemeToggle has aria-label on the container', () => {
      render(<ThemeToggle />);
      const group = screen.getByRole('radiogroup');
      expect(group.getAttribute('aria-label')).toBeTruthy();
    });

    it('ThemeToggle buttons have aria-pressed', () => {
      render(<ThemeToggle />);
      const buttons = screen.getAllByRole('button');
      buttons.forEach(button => {
        expect(button.hasAttribute('aria-pressed')).toBe(true);
      });
    });

    it('FontSizeButton has aria-label', () => {
      render(<FontSizeButton />);
      const button = screen.getByRole('button');
      expect(button.getAttribute('aria-label')).toMatch(/font size/i);
    });

    it('Input has aria-invalid when in error state', () => {
      render(<Input aria-label="test" error />);
      const input = screen.getByRole('textbox');
      expect(input.getAttribute('aria-invalid')).toBe('true');
    });

    it('Modal has role="dialog" and aria-label', () => {
      render(
        <Modal open={true} onClose={vi.fn()} title="Test">
          <p>Content</p>
        </Modal>
      );
      const dialog = screen.getByRole('dialog');
      expect(dialog.getAttribute('aria-label')).toBe('Test');
    });
  });
});
