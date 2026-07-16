'use client';

const packages = [
  { name: 'Boost', price: '0.5', duration: '5 Hours', desc: 'Highlighted card, quick visibility', featured: false },
  { name: 'Top 6–10', price: '1', duration: '24 Hours', desc: 'Position 6–10 in trending', featured: false },
  { name: 'Top 1–5', price: '2.5', duration: '24 Hours', desc: 'Position 1–5, sponsored badge', featured: true },
  { name: 'Pinned', price: '4', duration: '72 Hours', desc: 'Featured on homepage, top priority', featured: false },
];

export function Pricing() {
  return (
    <section id="pricing" className="max-w-6xl mx-auto px-6 py-24">
      <div className="text-center mb-14">
        <div className="inline-block text-xs font-mono uppercase tracking-wider text-purple mb-3">
          Promote
        </div>
        <h2 className="font-display font-semibold text-3xl sm:text-4xl">Promotion packages</h2>
        <p className="text-muted mt-3">Boost your token&apos;s visibility. Paid in SOL.</p>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {packages.map((p) => (
          <div
            key={p.name}
            className={`rounded-2xl border p-6 flex flex-col ${
              p.featured
                ? 'border-purple/40 bg-gradient-to-b from-purple/10 to-transparent'
                : 'border-border bg-card'
            }`}
          >
            {p.featured && (
              <span className="text-[10px] font-mono uppercase tracking-wide text-purple mb-3">
                Most popular
              </span>
            )}
            <div className="font-medium text-lg">{p.name}</div>
            <div className="font-display font-semibold text-3xl mt-3">
              {p.price} <span className="text-base font-body font-normal text-muted">SOL</span>
            </div>
            <div className="text-xs text-muted font-mono mt-1">{p.duration}</div>
            <p className="text-sm text-muted mt-4 flex-1">{p.desc}</p>
            <a
              href="https://t.me/BullRunBot"
              target="_blank"
              className={`mt-6 text-center py-2.5 rounded-xl text-sm font-medium transition-opacity hover:opacity-90 ${
                p.featured ? 'bg-gradient-to-r from-purple to-blue text-white' : 'border border-border text-ink'
              }`}
            >
              Select
            </a>
          </div>
        ))}
      </div>
    </section>
  );
}
