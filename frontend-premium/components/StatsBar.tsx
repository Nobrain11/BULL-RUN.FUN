'use client';

import { useEffect, useState } from 'react';
import { Stats } from '@/lib/api';

function CountUp({ value }: { value: number }) {
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    const duration = 900;
    const start = performance.now();
    let raf: number;

    function tick(now: number) {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplay(Math.floor(value * eased));
      if (progress < 1) raf = requestAnimationFrame(tick);
    }
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [value]);

  return <>{display.toLocaleString()}</>;
}

export function StatsBar({ stats }: { stats: Stats }) {
  const items = [
    { label: 'Tokens Listed', value: stats.total_tokens },
    { label: 'Active Now', value: stats.active_tokens },
    { label: 'Total Votes', value: stats.total_votes },
    { label: 'Revenue (SOL)', value: Math.round(stats.total_revenue_sol) },
  ];

  return (
    <section className="border-y border-border bg-card/40 px-6 py-10">
      <div className="max-w-6xl mx-auto grid grid-cols-2 sm:grid-cols-4 gap-6">
        {items.map((s) => (
          <div key={s.label} className="text-center">
            <div className="font-display font-semibold text-2xl sm:text-3xl">
              <CountUp value={s.value} />
            </div>
            <div className="text-xs text-muted font-mono mt-1 uppercase tracking-wide">
              {s.label}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
