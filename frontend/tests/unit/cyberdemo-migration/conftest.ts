/**
 * Unit test isolation guard for cyberdemo-migration tests.
 * These tests should NOT import the full app or infrastructure modules.
 */
import { afterAll } from 'vitest';

afterAll(() => {
  // Check that no infrastructure modules were loaded during unit tests
  const forbidden = ['src/main', 'opensearchpy', 'asyncpg', 'psycopg2'];
  const violations = forbidden.filter(m => Object.keys(require.cache || {}).some(k => k.includes(m)));
  if (violations.length > 0) {
    console.warn(
      `Infrastructure modules imported in unit tests: ${violations.join(', ')}. Move tests to integration/`,
    );
  }
});
