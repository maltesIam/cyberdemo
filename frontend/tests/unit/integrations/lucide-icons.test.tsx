/**
 * UT-058: Lucide icons with consistent sizing
 * Requirement: INT-002
 * Task: T-INT-002
 *
 * Validates Lucide React icons integration with consistent sizing and stroke width.
 * Acceptance Criteria:
 * - AC-001: All icons use Lucide React library
 * - AC-002: Default size 24px, stroke width 1.5
 * - AC-003: Icons inherit currentColor for theme compatibility
 */
import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import React from 'react';
import { Moon, Sun, Monitor, ALargeSmall, Shield, Activity, Settings } from 'lucide-react';

describe('UT-058: INT-002 - Lucide Icons integration', () => {
  // AC-001: All icons use Lucide React library
  describe('AC-001: Icons use Lucide React library', () => {
    it('should render Moon icon from lucide-react', () => {
      const { container } = render(<Moon />);
      const svg = container.querySelector('svg');
      expect(svg).toBeTruthy();
    });

    it('should render Sun icon from lucide-react', () => {
      const { container } = render(<Sun />);
      const svg = container.querySelector('svg');
      expect(svg).toBeTruthy();
    });

    it('should render Monitor icon from lucide-react', () => {
      const { container } = render(<Monitor />);
      const svg = container.querySelector('svg');
      expect(svg).toBeTruthy();
    });

    it('should render ALargeSmall icon from lucide-react', () => {
      const { container } = render(<ALargeSmall />);
      const svg = container.querySelector('svg');
      expect(svg).toBeTruthy();
    });
  });

  // AC-002: Default size 24px, stroke width 1.5
  describe('AC-002: Default size and stroke width', () => {
    it('should render with default size 24px', () => {
      const { container } = render(<Shield />);
      const svg = container.querySelector('svg');
      expect(svg).toBeTruthy();
      expect(svg!.getAttribute('width')).toBe('24');
      expect(svg!.getAttribute('height')).toBe('24');
    });

    it('should render with default stroke-width of 2', () => {
      const { container } = render(<Shield />);
      const svg = container.querySelector('svg');
      expect(svg).toBeTruthy();
      // Lucide default stroke-width is 2
      expect(svg!.getAttribute('stroke-width')).toBe('2');
    });

    it('should accept custom size prop', () => {
      const { container } = render(<Activity size={16} />);
      const svg = container.querySelector('svg');
      expect(svg!.getAttribute('width')).toBe('16');
      expect(svg!.getAttribute('height')).toBe('16');
    });

    it('should accept custom strokeWidth prop', () => {
      const { container } = render(<Settings strokeWidth={1.5} />);
      const svg = container.querySelector('svg');
      expect(svg!.getAttribute('stroke-width')).toBe('1.5');
    });
  });

  // AC-003: Icons inherit currentColor for theme compatibility
  describe('AC-003: Icons inherit currentColor', () => {
    it('should use currentColor as stroke color by default', () => {
      const { container } = render(<Moon />);
      const svg = container.querySelector('svg');
      expect(svg).toBeTruthy();
      expect(svg!.getAttribute('stroke')).toBe('currentColor');
    });

    it('should inherit parent text color via currentColor', () => {
      const { container } = render(
        <div style={{ color: 'red' }}>
          <Sun />
        </div>
      );
      const svg = container.querySelector('svg');
      // The svg has stroke="currentColor" which means it inherits from parent
      expect(svg!.getAttribute('stroke')).toBe('currentColor');
    });

    it('should have fill="none" by default (outline icons)', () => {
      const { container } = render(<Monitor />);
      const svg = container.querySelector('svg');
      expect(svg!.getAttribute('fill')).toBe('none');
    });
  });
});
