'use client';

import { motion } from 'framer-motion';
import { Token, formatCurrency, shortenAddress } from '@/lib/api';
import { ThumbsUp, Share2, Rocket } from 'lucide-react';

export function TokenCard({ token, index }: { token: Token; index: number }) {
  const mult = token.current_multiplier || 1;
  const highest = token.highest_multiplier || 1;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-40px' }}
      transition={{ duration: 0.5, delay: Math.min(index * 0.04, 0.3) }}
      className={`card-glow rounded-2xl border p-5 bg-card transition-all ${
        token.is_sponsored ? 'border-purple/30' : 'border-border'
      }`}
    >
      <div className="flex items-start gap-3">
        <img
          src={token.logo_url || 'https://api.dicebear.com/7.x/shapes/svg?seed=' + token.symbol}
          alt={token.name}
          className="w-11 h-11 rounded-xl object-cover bg-cardHover border border-border"
        />
        <div className="min-w-0 flex-1">
          <div className="font-medium truncate">{token.name}</div>
          <div className="text-xs text-muted font-mono">${token.symbol}</div>
        </div>
        <div className="flex gap-1">
          {token.is_sponsored && (
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-purple/15 text-purple border border-purple/30 font-mono uppercase">
              Sponsored
            </span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-2 mt-4 py-3 border-y border-border/60">
        <div>
          <div className="text-xs text-muted">Price</div>
          <div className="font-mono text-sm mt-0.5">{formatCurrency(token.price)}</div>
        </div>
        <div>
          <div className="text-xs text-muted">Mkt Cap</div>
          <div className="font-mono text-sm mt-0.5">{formatCurrency(token.market_cap)}</div>
        </div>
        <div>
          <div className="text-xs text-muted">Vol 24h</div>
          <div className="font-mono text-sm mt-0.5">{formatCurrency(token.volume_24h)}</div>
        </div>
      </div>

      <div className="flex items-center justify-between mt-3">
        <div className="flex items-baseline gap-2">
          <span
            className={`font-display font-semibold text-lg ${
              mult >= 1 ? 'text-emerald' : 'text-danger'
            }`}
          >
            {mult.toFixed(2)}x
          </span>
          <span className="text-xs text-muted font-mono">high {highest.toFixed(2)}x</span>
        </div>
        <span className="text-xs text-muted font-mono">{shortenAddress(token.address)}</span>
      </div>

      <div className="grid grid-cols-3 gap-2 mt-4">
        <button className="flex items-center justify-center gap-1.5 py-2 rounded-lg border border-border text-xs text-muted hover:text-ink hover:border-emerald/40 transition-colors">
          <ThumbsUp size={13} /> {token.vote_count || 0}
        </button>
        <button className="flex items-center justify-center gap-1.5 py-2 rounded-lg border border-border text-xs text-muted hover:text-ink hover:border-blue/40 transition-colors">
          <Share2 size={13} /> Share
        </button>
        <a
          href={`https://t.me/BullRunBot?start=promote_${token.address}`}
          target="_blank"
          className="flex items-center justify-center gap-1.5 py-2 rounded-lg border border-border text-xs text-muted hover:text-ink hover:border-purple/40 transition-colors"
        >
          <Rocket size={13} /> Promote
        </a>
      </div>
    </motion.div>
  );
}

export function EmptyState({ icon, title, subtitle }: { icon: string; title: string; subtitle: string }) {
  return (
    <div className="col-span-full text-center py-16 border border-dashed border-border rounded-2xl">
      <div className="text-3xl mb-3 opacity-60">{icon}</div>
      <div className="font-medium">{title}</div>
      <div className="text-sm text-muted mt-1">{subtitle}</div>
    </div>
  );
}
