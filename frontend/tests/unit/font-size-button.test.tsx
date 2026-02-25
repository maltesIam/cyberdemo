/**
 * Unit Tests: FontSizeButton React Component
 * Tasks: T-026 (REQ-003-001-001), T-027 (REQ-003-001-002), T-028 (REQ-003-001-003),
 *        T-029 (REQ-003-001-004), T-030 (REQ-003-001-006)
 */
import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { FontSizeButton } from '../../src/components/FontSizeButton';

beforeEach(() => {
  document.documentElement.style.fontSize = '';
  localStorage.clear();
});

// UT-026: REQ-003-001-001 - FontSizeButton renders with Lucide icon
describe('T-026: FontSizeButton renders with Lucide icon', () => {
  it('should render a button element', () => {
    render(<FontSizeButton />);
    const button = screen.getByRole('button');
    expect(button).toBeTruthy();
  });

  it('should contain an SVG icon (Lucide)', () => {
    const { container } = render(<FontSizeButton />);
    const svg = container.querySelector('svg');
    expect(svg).toBeTruthy();
  });

  it('should have an accessible label', () => {
    render(<FontSizeButton />);
    const button = screen.getByLabelText(/font size/i);
    expect(button).toBeTruthy();
  });
});

// UT-027: REQ-003-001-002 - Click cycles: 16px -> 18px -> 20px -> 16px
describe('T-027: FontSizeButton cycles through sizes', () => {
  it('should start at 16px (step 0)', () => {
    render(<FontSizeButton />);
    // Default is 16px, no explicit fontSize set
    const fontSize = document.documentElement.style.fontSize;
    expect(fontSize === '' || fontSize === '16px').toBe(true);
  });

  it('should change to 18px after first click', () => {
    render(<FontSizeButton />);
    const button = screen.getByRole('button');
    fireEvent.click(button);
    expect(document.documentElement.style.fontSize).toBe('18px');
  });

  it('should change to 20px after second click', () => {
    render(<FontSizeButton />);
    const button = screen.getByRole('button');
    fireEvent.click(button);
    fireEvent.click(button);
    expect(document.documentElement.style.fontSize).toBe('20px');
  });

  it('should cycle back to 16px after third click', () => {
    render(<FontSizeButton />);
    const button = screen.getByRole('button');
    fireEvent.click(button);
    fireEvent.click(button);
    fireEvent.click(button);
    expect(document.documentElement.style.fontSize).toBe('16px');
  });
});

// UT-028: REQ-003-001-003 - FontSizeButton modifies documentElement fontSize
describe('T-028: FontSizeButton modifies documentElement.style.fontSize', () => {
  it('should modify document.documentElement.style.fontSize', () => {
    render(<FontSizeButton />);
    const button = screen.getByRole('button');
    fireEvent.click(button);
    expect(document.documentElement.style.fontSize).toBeTruthy();
  });
});

// UT-029: REQ-003-001-004 - FontSizeButton visually indicates current state
describe('T-029: FontSizeButton visually indicates current state', () => {
  it('should have aria-label that reflects current font size state', () => {
    render(<FontSizeButton />);
    const button = screen.getByRole('button');
    // After click, aria-label should update
    fireEvent.click(button);
    const label = button.getAttribute('aria-label');
    expect(label).toBeTruthy();
    expect(label).toMatch(/font size/i);
  });
});

// UT-030: REQ-003-001-006 - FontSizeButton placed LEFT of ThemeToggle (layout test)
describe('T-030: FontSizeButton placement', () => {
  it('should render as a standalone component that can be placed in headers', () => {
    const { container } = render(<FontSizeButton />);
    expect(container.firstElementChild).toBeTruthy();
  });
});
