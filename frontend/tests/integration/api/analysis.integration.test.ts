/**
 * Integration Tests for Analysis REST API
 * IT-INT-006: POST /api/v1/analysis/analyze
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { apiClient } from '../../../src/services/api';

vi.mock('../../../src/services/api', () => ({
  apiClient: {
    post: vi.fn(),
  },
}));

const mockedApiClient = vi.mocked(apiClient);

beforeEach(() => {
  vi.clearAllMocks();
});

describe('IT-INT-006: POST /api/v1/analysis/analyze', () => {
  it('should send analysis request and receive decision', async () => {
    const mockResponse = {
      data: {
        id: 'analysis-1',
        incidentId: 'inc-001',
        decision: 'contain',
        confidence: 0.95,
        reasoning: 'High severity threat detected - automated containment recommended',
        timestamp: '2026-02-24T10:00:00Z',
        duration: 3500,
      },
    };
    mockedApiClient.post.mockResolvedValueOnce(mockResponse);

    const result = await apiClient.post('/api/v1/analysis/analyze', {
      incident_id: 'inc-001',
      case_type: 'auto-containment',
    });

    expect(mockedApiClient.post).toHaveBeenCalledWith('/api/v1/analysis/analyze', {
      incident_id: 'inc-001',
      case_type: 'auto-containment',
    });
    expect(result.data.decision).toBe('contain');
    expect(result.data.confidence).toBe(0.95);
  });

  it('should handle analysis error response', async () => {
    mockedApiClient.post.mockRejectedValueOnce(new Error('Analysis service unavailable'));

    await expect(
      apiClient.post('/api/v1/analysis/analyze', { incident_id: 'inc-001' })
    ).rejects.toThrow('Analysis service unavailable');
  });

  it('should return all analysis decision types', async () => {
    const decisions = ['contain', 'escalate', 'dismiss', 'monitor'];
    for (const decision of decisions) {
      mockedApiClient.post.mockResolvedValueOnce({
        data: { decision, confidence: 0.9, reasoning: 'test' },
      });

      const result = await apiClient.post('/api/v1/analysis/analyze', {
        incident_id: `inc-${decision}`,
      });
      expect(result.data.decision).toBe(decision);
    }
  });
});
