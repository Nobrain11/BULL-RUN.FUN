'use client';

import { Token } from '@/lib/api';
import { TokenCard, EmptyState } from './TokenCard';

export function TokenSection({
  id,
  eyebrow,
  eyebrowColor,
  title,
  subtitle,
  tokens,
  emptyIcon,
  emptyTitle,
  emptySubtitle,
}: {
  id: string;
  eyebrow: string;
  eyebrowColor: string;
  title: string;
  subtitle: string;
  tokens: Token[];
  emptyIcon: string;
  emptyTitle: string;
  emptySubtitle: string;
}) {
  return (
    <section id={id} className="max-w-6xl mx-auto px-6 py-16">
      <div className="text-center mb-12">
        <div className={`inline-block text-xs font-mono uppercase tracking-wider mb-3 ${eyebrowColor}`}>
          {eyebrow}
        </div>
        <h2 className="font-display font-semibold text-3xl sm:text-4xl">{title}</h2>
        <p className="text-muted mt-3">{subtitle}</p>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {tokens.length === 0 ? (
          <EmptyState icon={emptyIcon} title={emptyTitle} subtitle={emptySubtitle} />
        ) : (
          tokens.map((t, i) => <TokenCard key={t.address} token={t} index={i} />)
        )}
      </div>
    </section>
  );
}
