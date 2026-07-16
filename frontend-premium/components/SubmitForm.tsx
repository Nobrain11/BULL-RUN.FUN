'use client';

import { useState } from 'react';
import { Loader2, CheckCircle2, Clock } from 'lucide-react';

type Status = 'idle' | 'loading' | 'listed' | 'pending' | 'error';

export function SubmitForm() {
  const [address, setAddress] = useState('');
  const [status, setStatus] = useState<Status>('idle');
  const [message, setMessage] = useState('');

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = address.trim();

    if (trimmed.length < 32 || trimmed.length > 44) {
      setStatus('error');
      setMessage('Invalid Solana address. Must be 32–44 characters.');
      return;
    }

    setStatus('loading');
    try {
      const res = await fetch('https://bullrun-api-nd1q.onrender.com/api/listing-request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ address: trimmed }),
      });
      const result = await res.json();

      if (res.status === 201) {
        setStatus('listed');
        setMessage(result.message || 'Token listed successfully.');
      } else if (res.status === 202) {
        setStatus('pending');
        setMessage(result.message || 'Submitted for review.');
      } else {
        setStatus('error');
        setMessage(result.error || 'Something went wrong.');
      }
    } catch {
      setStatus('error');
      setMessage('Network error. Please try again.');
    }
  }

  return (
    <section id="submit" className="max-w-2xl mx-auto px-6 py-24">
      <div className="text-center mb-10">
        <div className="inline-block text-xs font-mono uppercase tracking-wider text-emerald mb-3">
          Submit
        </div>
        <h2 className="font-display font-semibold text-3xl sm:text-4xl">List your token</h2>
        <p className="text-muted mt-3">Auto-listing via DexScreener.</p>
      </div>

      <form onSubmit={handleSubmit} className="rounded-2xl border border-border bg-card p-6">
        <label className="text-sm font-medium block mb-2">Token address</label>
        <input
          value={address}
          onChange={(e) => setAddress(e.target.value)}
          placeholder="Enter Solana token address…"
          className="w-full px-4 py-3.5 rounded-xl bg-cardHover border border-border font-mono text-sm outline-none focus:border-purple/50 transition-colors"
        />
        <p className="text-xs text-muted mt-2">32–44 character base58 address</p>

        <button
          type="submit"
          disabled={status === 'loading'}
          className="w-full mt-5 py-3.5 rounded-xl bg-gradient-to-r from-purple to-blue text-white font-medium text-sm flex items-center justify-center gap-2 disabled:opacity-60 hover:opacity-90 transition-opacity"
        >
          {status === 'loading' ? (
            <>
              <Loader2 size={16} className="animate-spin" /> Submitting…
            </>
          ) : (
            'Submit Token'
          )}
        </button>

        {status === 'listed' && (
          <div className="mt-4 flex items-center gap-2 text-sm text-emerald bg-emerald/10 border border-emerald/25 rounded-xl px-4 py-3">
            <CheckCircle2 size={16} /> {message}
          </div>
        )}
        {status === 'pending' && (
          <div className="mt-4 flex items-center gap-2 text-sm text-blue bg-blue/10 border border-blue/25 rounded-xl px-4 py-3">
            <Clock size={16} /> {message}
          </div>
        )}
        {status === 'error' && (
          <div className="mt-4 text-sm text-danger bg-danger/10 border border-danger/25 rounded-xl px-4 py-3">
            {message}
          </div>
        )}
      </form>
    </section>
  );
}
