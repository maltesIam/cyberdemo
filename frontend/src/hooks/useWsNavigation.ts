/**
 * useWsNavigation - Navigate to a page when MCP state includes currentPage
 *
 * REQ-001-001-002: When state update includes `currentPage`, navigate to that page
 * with a brief toast notification "Vega navigated to [page]"
 */

import { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '../utils/toast';

/**
 * Hook that navigates to a page when the currentPage value changes.
 * Shows a toast: "Vega navigated to [pageName]".
 */
export function useWsNavigation(currentPage: string | undefined): void {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const prevPageRef = useRef<string | undefined>(undefined);

  useEffect(() => {
    if (!currentPage) return;
    if (currentPage === prevPageRef.current) return;

    prevPageRef.current = currentPage;
    navigate(currentPage);

    // Format page name: strip leading slash for display
    const pageName = currentPage.replace(/^\//, '');
    showToast('info', `Vega navigated to ${pageName}`, 3000);
  }, [currentPage, navigate, showToast]);
}
