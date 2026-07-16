const API_URL = 'https://bullrun-api-nd1q.onrender.com/api';

export type Token = {
  address: string;
  name: string;
  symbol: string;
  logo_url?: string;
  price: number;
  market_cap: number;
  volume_24h: number;
  current_multiplier?: number;
  highest_multiplier?: number;
  vote_count?: number;
  share_count?: number;
  is_sponsored?: boolean;
  is_featured?: boolean;
  sponsor_position?: number;
};

export type Stats = {
  total_tokens: number;
  active_tokens: number;
  total_votes: number;
  total_revenue_sol: number;
};

async function safeFetch<T>(path: string, fallback: T): Promise<T> {
  try {
    const res = await fetch(`${API_URL}${path}`, { cache: 'no-store' });
    if (!res.ok) return fallback;
    return (await res.json()) as T;
  } catch {
    return fallback;
  }
}

export function getStats() {
  return safeFetch<Stats>('/admin/stats', {
    total_tokens: 0,
    active_tokens: 0,
    total_votes: 0,
    total_revenue_sol: 0,
  });
}

export function getTrending(filter: string = 'all') {
  return safeFetch<{ tokens: Token[] }>(`/tokens/trending?filter=${filter}`, { tokens: [] });
}

export function getNew() {
  return safeFetch<{ tokens: Token[] }>('/tokens/new', { tokens: [] });
}

export function getSponsored() {
  return safeFetch<{ tokens: Token[] }>('/tokens/sponsored', { tokens: [] });
}

export function formatCurrency(value: number | undefined) {
  const v = value || 0;
  if (v >= 1e9) return '$' + (v / 1e9).toFixed(2) + 'B';
  if (v >= 1e6) return '$' + (v / 1e6).toFixed(2) + 'M';
  if (v >= 1e3) return '$' + (v / 1e3).toFixed(2) + 'K';
  if (v >= 1) return '$' + v.toFixed(2);
  return '$' + v.toFixed(6);
}

export function shortenAddress(address: string) {
  if (!address) return '';
  return address.slice(0, 4) + '…' + address.slice(-4);
}
