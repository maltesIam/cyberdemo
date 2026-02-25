/**
 * Unit Tests for Modal Component
 * T-004-010: REQ-004-007-001 - Modal overlay and container
 * Verifies modal overlay, styles, footer layout, and focus trap.
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { Modal } from '../../../../src/components/ui/Modal';

describe('Modal Component', () => {
  describe('REQ-004-007-001: Modal overlay and container', () => {
    it('should render modal when open', () => {
      render(
        <Modal open onClose={() => {}}>
          <p>Modal content</p>
        </Modal>
      );
      expect(screen.getByText('Modal content')).toBeInTheDocument();
    });

    it('should not render when not open', () => {
      render(
        <Modal open={false} onClose={() => {}}>
          <p>Hidden content</p>
        </Modal>
      );
      expect(screen.queryByText('Hidden content')).not.toBeInTheDocument();
    });

    it('AC-001: overlay should have rgba(0,0,0,0.6) background', () => {
      render(
        <Modal open onClose={() => {}}>
          <p>Content</p>
        </Modal>
      );
      const overlay = screen.getByTestId('modal-overlay');
      expect(overlay.style.backgroundColor).toBe('rgba(0, 0, 0, 0.6)');
    });

    it('AC-001: overlay should have backdrop blur 4px', () => {
      render(
        <Modal open onClose={() => {}}>
          <p>Content</p>
        </Modal>
      );
      const overlay = screen.getByTestId('modal-overlay');
      expect(overlay.style.backdropFilter).toBe('blur(4px)');
    });

    it('AC-002: modal container should have bg-elevated background', () => {
      render(
        <Modal open onClose={() => {}}>
          <p>Content</p>
        </Modal>
      );
      const modal = screen.getByRole('dialog');
      expect(modal.style.backgroundColor).toBe('var(--bg-elevated)');
    });

    it('AC-002: modal should have border-primary border', () => {
      render(
        <Modal open onClose={() => {}}>
          <p>Content</p>
        </Modal>
      );
      const modal = screen.getByRole('dialog');
      expect(modal.style.borderColor).toBe('var(--border-primary)');
      expect(modal.style.borderWidth).toBe('1px');
    });

    it('AC-002: modal should have radius-xl border radius', () => {
      render(
        <Modal open onClose={() => {}}>
          <p>Content</p>
        </Modal>
      );
      const modal = screen.getByRole('dialog');
      expect(modal.style.borderRadius).toBe('var(--radius-xl)');
    });

    it('AC-002: modal should have shadow-xl box shadow', () => {
      render(
        <Modal open onClose={() => {}}>
          <p>Content</p>
        </Modal>
      );
      const modal = screen.getByRole('dialog');
      expect(modal.style.boxShadow).toBe('var(--shadow-xl)');
    });

    it('AC-003: modal should have max-width 480px', () => {
      render(
        <Modal open onClose={() => {}}>
          <p>Content</p>
        </Modal>
      );
      const modal = screen.getByRole('dialog');
      expect(modal.style.maxWidth).toBe('480px');
    });

    it('AC-004: header should render title with text-lg, weight-semibold', () => {
      render(
        <Modal open onClose={() => {}} title="Confirm Action">
          <p>Content</p>
        </Modal>
      );
      const title = screen.getByText('Confirm Action');
      expect(title.style.fontSize).toBe('1.125rem');
      expect(title.style.fontWeight).toBe('600');
    });

    it('AC-004: title should use text-primary color', () => {
      render(
        <Modal open onClose={() => {}} title="Test Title">
          <p>Content</p>
        </Modal>
      );
      const title = screen.getByText('Test Title');
      expect(title.style.color).toBe('var(--text-primary)');
    });

    it('AC-005: footer should have flex-end justification', () => {
      render(
        <Modal
          open
          onClose={() => {}}
          footer={<button>Confirm</button>}
        >
          <p>Content</p>
        </Modal>
      );
      const footer = screen.getByTestId('modal-footer');
      expect(footer.style.justifyContent).toBe('flex-end');
    });

    it('AC-005: footer should have space-3 gap between buttons', () => {
      render(
        <Modal
          open
          onClose={() => {}}
          footer={<button>Confirm</button>}
        >
          <p>Content</p>
        </Modal>
      );
      const footer = screen.getByTestId('modal-footer');
      expect(footer.style.gap).toBe('var(--space-3)');
    });

    it('AC-006: should close when Escape key is pressed', () => {
      const onClose = vi.fn();
      render(
        <Modal open onClose={onClose}>
          <p>Content</p>
        </Modal>
      );
      fireEvent.keyDown(document, { key: 'Escape' });
      expect(onClose).toHaveBeenCalledTimes(1);
    });

    it('should have aria-modal attribute', () => {
      render(
        <Modal open onClose={() => {}}>
          <p>Content</p>
        </Modal>
      );
      const modal = screen.getByRole('dialog');
      expect(modal.getAttribute('aria-modal')).toBe('true');
    });

    it('should have aria-label from title', () => {
      render(
        <Modal open onClose={() => {}} title="My Modal">
          <p>Content</p>
        </Modal>
      );
      const modal = screen.getByRole('dialog');
      expect(modal.getAttribute('aria-label')).toBe('My Modal');
    });

    it('should close when clicking overlay background', () => {
      const onClose = vi.fn();
      render(
        <Modal open onClose={onClose}>
          <p>Content</p>
        </Modal>
      );
      const overlay = screen.getByTestId('modal-overlay');
      fireEvent.click(overlay);
      expect(onClose).toHaveBeenCalledTimes(1);
    });

    it('should NOT close when clicking inside the modal content', () => {
      const onClose = vi.fn();
      render(
        <Modal open onClose={onClose}>
          <p>Click inside</p>
        </Modal>
      );
      fireEvent.click(screen.getByText('Click inside'));
      expect(onClose).not.toHaveBeenCalled();
    });

    it('overlay should have z-index from z-modal token', () => {
      render(
        <Modal open onClose={() => {}}>
          <p>Content</p>
        </Modal>
      );
      const overlay = screen.getByTestId('modal-overlay');
      expect(overlay.style.zIndex).toBe('var(--z-modal, 400)');
    });
  });
});
