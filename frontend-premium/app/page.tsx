'use client';

import { useEffect, useState } from 'react';
import { Nav, Ticker } from '@/components/NavAndTicker';
import { Hero } from '@/components/Hero';
import { StatsBar } from '@/components/StatsBar';
import { TokenSection } from '@/components/TokenSection';
import { Pricing } from '@/components/Pricing';
import { MilestoneFeed, Footer } from '@/components/MilestonesAndFooter';
import { SubmitForm } from '@/components/SubmitForm';
import { getStats, getTrending, getNew, getSponsored, Stats, Token } from '@/lib/api';

export default function Home() {
  const [stats, setStats] = useState<Stats>({
    total_tokens: 0,
    active_tokens: 0,
    total_votes: 0,
    total_revenue_sol: 0,
  });
  const [trending, setTrending] = useState<Token[]>([]);
  const [fresh, setFresh] = useState<Token[]>([]);
  const [sponsored, setSponsored] = useState<Token[]>([]);

  useEffect(() => {
    async function load() {
      const [s, t, n, sp] = await Promise.all([
        getStats(),
        getTrending('all'),
        getNew(),
        getSponsored(),
      ]);
      setStats(s);
      setTrending(t.tokens);
      setFresh(n.tokens);
      setSponsored(sp.tokens);
    }
    load();
    const interval = setInterval(load, 60000);
    return () => clearInterval(interval);
  }, []);

  const allForTicker = [...sponsored, ...trending].slice(0, 12);
  const allForMilestones = [...trending, ...fresh, ...sponsored];

  return (
    <main>
      <Nav />
      <Ticker tokens={allForTicker} />
      <div className="pt-9">
        <Hero />
        <StatsBar stats={stats} />

        <TokenSection
          id="sponsored"
          eyebrow="Sponsored"
          eyebrowColor="text-purple"
          title="Featured tokens"
          subtitle="Premium placements, backed by the community."
          tokens={sponsored}
          emptyIcon="⭐"
          emptyTitle="No sponsored tokens yet"
          emptySubtitle="Be the first to promote your token."
        />

        <TokenSection
          id="trending"
          eyebrow="Trending"
          eyebrowColor="text-blue"
          title="Top performers"
          subtitle="Sorted by momentum. Sponsored tokens pinned first."
          tokens={trending}
          emptyIcon="📈"
          emptyTitle="No tokens found"
          emptySubtitle="Check back soon for new listings."
        />

        <TokenSection
          id="new"
          eyebrow="New"
          eyebrowColor="text-emerald"
          title="Fresh listings"
          subtitle="Recently submitted. Be the first to discover."
          tokens={fresh}
          emptyIcon="🆕"
          emptyTitle="No new listings"
          emptySubtitle="Submit your token to be the first."
        />

        <MilestoneFeed tokens={allForMilestones} />
        <Pricing />
        <SubmitForm />
        <Footer />
      </div>
    </main>
  );
}
