import { SearchQuery, SearchResult } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function request<T>(url: string, params?: Record<string, unknown>): Promise<T> {
  const qp = new URLSearchParams();
  if (params) {
    for (const [k, v] of Object.entries(params)) {
      if (v === null || v === undefined) continue;
      if (Array.isArray(v)) {
        v.forEach(item => qp.append(k, String(item)));
      } else {
        qp.append(k, String(v));
      }
    }
  }
  const qs = qp.toString();
  const res = await fetch(`${API_BASE}${url}${qs ? '?' + qs : ''}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function searchJobs(params: SearchQuery): Promise<SearchResult> {
  return request<SearchResult>('/api/v1/search', params as unknown as Record<string, unknown>);
}

export async function checkHealth(): Promise<{ status: string; elasticsearch: string; redis: string }> {
  return request<{ status: string; elasticsearch: string; redis: string }>('/api/v1/health');
}
