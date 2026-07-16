'use client';

import { Token, formatCurrency } from '@/lib/api';

const links = [
  { href: '#trending', label: 'Trending' },
  { href: '#new', label: 'New' },
  { href: '#sponsored', label: 'Sponsored' },
  { href: '#milestones', label: 'Milestones' },
  { href: '#pricing', label: 'Promote' },
  { href: '#submit', label: 'Submit' },
];

export function Nav() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass border-b border-border">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <a href="#" className="flex items-center gap-2">
          <span className="font-display font-semibold text-lg tracking-tight">Bull Run</span>
        </a>
        <ul className="hidden md:flex items-center gap-1">
          {links.map((l) => (
            <li key={l.href}>
              <a
                href={l.href}
                className="px-3 py-2 text-sm text-muted hover:text-ink transition-colors rounded-lg hover:bg-white/5"
              >
                {l.label}
              </a>
            </li>
          ))}
        </ul>
        <a
          href="https://t.me/BullRunBot"
          target="_blank"
          className="text-sm font-medium px-4 py-2 rounded-lg bg-gradient-to-r from-purple to-blue text-white hover:opacity-90 transition-opacity"
        >
          Open Bot
        </a>
      </div>
    </nav>
  );
}

export function Ticker({ tokens }: { tokens: Token[] }) {
  const items = tokens.length ? tokens : [];

  if (!items.length) {
    return (
      <div className="fixed top-16 left-0 right-0 z-40 bg-card/80 border-b border-border h-9 flex items-center px-6">
        <span className="text-xs font-mono text-muted">Waiting for live market data…</span>
      </div>
    );
  }

  const loop = [...items, ...items];

  return (
    <div className="fixed top-16 left-0 right-0 z-40 bg-card/80 border-b border-border h-9 overflow-hidden ticker-mask">
      <div className="flex items-center h-full gap-8 animate-ticker whitespace-nowrap w-max">
        {loop.map((t, i) => {
          const mult = t.current_multiplier || 1;
          const up = mult >= 1;
          return (
            <div key={i} className="flex items-center gap-2 font-mono text-xs">
              <span className="text-ink font-medium">${t.symbol}</span>
              <span className="text-muted">{formatCurrency(t.market_cap)}</span>
              <span className={up ? 'text-emerald' : 'text-danger'}>
                {mult.toFixed(2)}x
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
