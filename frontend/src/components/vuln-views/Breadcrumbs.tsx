/**
 * Breadcrumbs - Reusable navigation breadcrumbs component
 *
 * Features:
 * - Renders navigation trail with links
 * - Current page indicator without link
 * - Chevron separators
 * - Accessible markup with aria attributes
 */

import { Link } from "react-router-dom";
import clsx from "clsx";

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

export interface BreadcrumbsProps {
  items: BreadcrumbItem[];
  className?: string;
}

export function Breadcrumbs({ items, className }: BreadcrumbsProps) {
  return (
    <nav
      aria-label="Breadcrumb"
      className={clsx("flex items-center space-x-2 text-sm", className)}
    >
      {items.map((item, index) => {
        const isLast = index === items.length - 1;
        const isFirst = index === 0;

        return (
          <div key={item.label} className="flex items-center space-x-2">
            {!isFirst && (
              <span className="text-gray-500" aria-hidden="true">
                {">"}
              </span>
            )}
            {item.href && !isLast ? (
              <Link
                to={item.href}
                className="text-gray-400 hover:text-cyan-400 transition-colors"
              >
                {item.label}
              </Link>
            ) : (
              <span
                className={clsx(
                  isLast ? "text-white font-medium" : "text-gray-400"
                )}
                aria-current={isLast ? "page" : undefined}
              >
                {item.label}
              </span>
            )}
          </div>
        );
      })}
    </nav>
  );
}
