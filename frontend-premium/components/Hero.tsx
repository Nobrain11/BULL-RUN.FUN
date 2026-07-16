'use client';

import { motion } from 'framer-motion';

export function Hero() {
  return (
    <section className="relative pt-40 pb-28 px-6 flex flex-col items-center text-center overflow-hidden">
      <div className="signal-orb -top-40 left-1/2 -translate-x-1/2 animate-pulseGlow" />

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        className="relative z-10 inline-flex items-center gap-2 px-3 py-1 rounded-full border border-border bg-card/60 text-xs font-mono text-muted mb-8"
      >
        <span className="w-1.5 h-1.5 rounded-full bg-emerald animate-pulseGlow" />
        Live Solana signal feed
      </motion.div>

      <motion.h1
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
        className="relative z-10 font-display font-semibold text-[2.5rem] sm:text-6xl leading-[1.05] tracking-tight max-w-3xl"
      >
        Find the next Solana winner{' '}
        <span className="bg-gradient-to-r from-purple to-blue bg-clip-text text-transparent">
          before everyone else.
        </span>
      </motion.h1>

      <motion.p
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
        className="relative z-10 mt-6 text-muted text-base sm:text-lg max-w-xl"
      >
        Discover trending Solana tokens, monitor market momentum, promote your
        project, and track milestones in real time.
      </motion.p>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
        className="relative z-10 mt-10 flex flex-wrap items-center justify-center gap-3"
      >
        <a
          href="#trending"
          className="px-5 py-3 rounded-xl bg-gradient-to-r from-purple to-blue text-white font-medium text-sm hover:opacity-90 transition-opacity"
        >
          Explore Tokens
        </a>
        <a
          href="#submit"
          className="px-5 py-3 rounded-xl border border-border bg-card/60 text-ink font-medium text-sm hover:bg-cardHover transition-colors"
        >
          Submit Token
        </a>
        <a
          href="#pricing"
          className="px-5 py-3 rounded-xl border border-border bg-card/60 text-ink font-medium text-sm hover:bg-cardHover transition-colors"
        >
          Promote Token
        </a>
      </motion.div>
    </section>
  );
}
