'use client';

import { Token, formatCurrency } from '@/lib/api';

export function MilestoneFeed({ tokens }: { tokens: Token[] }) {
  const reached = tokens
    .filter((t) => (t.highest_multiplier || 1) >= 2)
    .sort((a, b) => (b.highest_multiplier || 0) - (a.highest_multiplier || 0))
    .slice(0, 6);

  return (
    <section id="milestones" className="max-w-6xl mx-auto px-6 py-24">
      <div className="text-center mb-14">
        <div className="inline-block text-xs font-mono uppercase tracking-wider text-blue mb-3">
          Milestones
        </div>
        <h2 className="font-display font-semibold text-3xl sm:text-4xl">Latest breakouts</h2>
        <p className="text-muted mt-3">2x, 4x, 6x, 8x, and 10x achievements, as they happen.</p>
      </div>

      {reached.length === 0 ? (
        <div className="text-center py-16 border border-dashed border-border rounded-2xl">
          <div className="text-3xl mb-3 opacity-60">🏆</div>
          <div className="font-medium">No milestones yet</div>
          <div className="text-sm text-muted mt-1">The first breakout will appear here.</div>
        </div>
      ) : (
        <div className="space-y-2">
          {reached.map((t) => (
            <div
              key={t.address}
              className="flex items-center justify-between rounded-xl border border-border bg-card px-5 py-3.5"
            >
              <div className="flex items-center gap-3 min-w-0">
                <span className="font-display font-semibold text-emerald">
                  {(t.highest_multiplier || 1).toFixed(1)}x
                </span>
                <span className="font-medium truncate">{t.name}</span>
                <span className="text-xs text-muted font-mono">${t.symbol}</span>
              </div>
              <span className="text-sm text-muted font-mono">{formatCurrency(t.market_cap)}</span>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

export function Footer() {
  return (
    <footer className="border-t border-border px-6 py-12 mt-12">
      <div className="max-w-6xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-6">
        <div>
          <div className="font-display font-semibold">Bull Run</div>
          <p className="text-xs text-muted mt-1">Find the next Solana winner before everyone else.</p>
        </div>
        <div className="flex gap-6 text-sm text-muted">
          <a href="#trending" className="hover:text-ink transition-colors">Trending</a>
          <a href="#new" className="hover:text-ink transition-colors">New</a>
          <a href="#pricing" className="hover:text-ink transition-colors">Promote</a>
        </div>
        <div className="flex gap-3">
          <a
            href="https://t.me/BullRunBot"
            target="_blank"
            className="text-sm px-4 py-2 rounded-lg border border-border hover:bg-cardHover transition-colors"
          >
            Telegram
          </a>
        </div>
      </div>
      <p className="text-center text-xs text-muted mt-10">© 2026 Bull Run. All rights reserved.</p>
    </footer>
  );
}
