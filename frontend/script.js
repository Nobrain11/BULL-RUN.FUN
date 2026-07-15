// frontend/script.js (continued from where it was cut)
= "${token.address}">
            <div class="token-header">
                <img src="${token.logo_url || 'https://via.placeholder.com/52?text=?'}" 
                     alt="${token.name}" 
                     class="token-logo"
                     onerror="this.src='https://via.placeholder.com/52?text=?'">
                <div class="token-info">
                    <div class="token-name">${escapeHtml(token.name)}</div>
                    <div class="token-symbol">$${escapeHtml(token.symbol)}</div>
                </div>
                <div class="token-badges">
                    ${badges}
                </div>
            </div>

            <div class="token-metrics">
                <div class="metric">
                    <div class="metric-value">${price}</div>
                    <div class="metric-label">Price</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${mcap}</div>
                    <div class="metric-label">Market Cap</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${volume}</div>
                    <div class="metric-label">Volume 24h</div>
                </div>
            </div>

            <div class="token-multiplier">
                <span>📈</span>
                <span class="multiplier-value">${multiplier.toFixed(2)}x</span>
                <span style="color: var(--text-muted); font-size: 0.85rem;">(High: ${highest.toFixed(2)}x)</span>
            </div>

            <div class="token-actions">
                <button class="action-btn vote-btn ${isVoted ? 'voted' : ''}" data-action="vote" data-address="${token.address}">
                    <span>👍</span> ${token.vote_count || 0}
                </button>
                <button class="action-btn share-btn" data-action="share" data-address="${token.address}">
                    <span>🔗</span> Share
                </button>
                <button class="action-btn promote-btn" data-action="promote" data-address="${token.address}">
                    <span>💰</span> Promote
                </button>
            </div>
        </div>
    `;
}

// ─── ATTACH CARD LISTENERS ───
function attachCardListeners() {
    // Card click → open modal
    document.querySelectorAll('.token-card').forEach(card => {
        card.addEventListener('click', (e) => {
            if (e.target.closest('.action-btn')) return;
            const address = card.dataset.address;
            openTokenModal(address);
        });
    });

    // Action buttons
    document.querySelectorAll('.action-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const action = btn.dataset.action;
            const address = btn.dataset.address;

            switch (action) {
                case 'vote':
                    handleVote(address, btn);
                    break;
                case 'share':
                    handleShare(address, btn);
                    break;
                case 'promote':
                    handlePromote(address);
                    break;
            }
        });
    });
}

// ─── HANDLE VOTE ───
async function handleVote(address, btn) {
    if (votedTokens.includes(address)) {
        showToast('You already voted for this token!', 'error');
        return;
    }

    try {
        const res = await fetch(`${API_URL}/vote/${address}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await res.json();

        if (res.ok) {
            votedTokens.push(address);
            localStorage.setItem('bullrun_voted', JSON.stringify(votedTokens));

            btn.classList.add('voted');
            btn.innerHTML = `<span>👍</span> ${data.vote_count}`;
            showToast('Vote recorded! 🎉', 'success');
        } else {
            showToast(data.error || 'Failed to vote', 'error');
        }
    } catch (err) {
        showToast('Network error. Try again.', 'error');
    }
}

// ─── HANDLE SHARE ───
async function handleShare(address, btn) {
    const shareUrl = `https://bullrun.app/token/${address}`;

    try {
        await navigator.clipboard.writeText(shareUrl);

        fetch(`${API_URL}/share/${address}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        }).catch(() => {});

        showToast('Link copied to clipboard! 🔗', 'success');
    } catch (err) {
        const textArea = document.createElement('textarea');
        textArea.value = shareUrl;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showToast('Link copied! 🔗', 'success');
    }
}

// ─── HANDLE PROMOTE ───
function handlePromote(address) {
    const botUrl = `https://t.me/BullRunBot?start=promote_${address}`;
    window.open(botUrl, '_blank');
}

// ─── TOKEN MODAL ───
async function openTokenModal(address) {
    const modal = document.getElementById('tokenModal');
    const body = document.getElementById('modalBody');

    body.innerHTML = `
        <div class="loading-state" style="padding: 40px;">
            <div class="spinner"></div>
            <p>Loading token details...</p>
        </div>
    `;

    modal.classList.add('active');
    document.body.style.overflow = 'hidden';

    try {
        const res = await fetch(`${API_URL}/tokens/${address}`);
        if (!res.ok) throw new Error('Failed to load token');

        const token = await res.json();

        const milestones = token.milestones || [];
        const milestoneTargets = [2, 4, 6, 8, 10];

        body.innerHTML = `
            <div class="modal-token-header">
                <img src="${token.logo_url || 'https://via.placeholder.com/64?text=?'}" 
                     alt="${token.name}" 
                     class="modal-token-logo"
                     onerror="this.src='https://via.placeholder.com/64?text=?'">
                <div class="modal-token-info">
                    <h2>${escapeHtml(token.name)}</h2>
                    <p>$${escapeHtml(token.symbol)} • ${shortenAddress(token.address)}</p>
                </div>
            </div>

            <div class="modal-metrics">
                <div class="modal-metric">
                    <div class="modal-metric-label">Price</div>
                    <div class="modal-metric-value">${formatCurrency(token.price)}</div>
                </div>
                <div class="modal-metric">
                    <div class="modal-metric-label">Market Cap</div>
                    <div class="modal-metric-value">${formatCurrency(token.market_cap)}</div>
                </div>
                <div class="modal-metric">
                    <div class="modal-metric-label">Volume 24h</div>
                    <div class="modal-metric-value">${formatCurrency(token.volume_24h)}</div>
                </div>
                <div class="modal-metric">
                    <div class="modal-metric-label">Multiplier</div>
                    <div class="modal-metric-value" style="background: var(--gradient-primary); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                        ${(token.current_multiplier || 1).toFixed(2)}x
                    </div>
                </div>
            </div>

            <div class="modal-milestones">
                <h3>🏆 Milestone History</h3>
                <div class="milestone-list">
                    ${milestoneTargets.map(target => {
                        const reached = milestones.find(m => Math.abs(m.multiplier - target) < 0.1);
                        const isReached = !!reached;
                        return `
                            <div class="milestone-item ${isReached ? 'reached' : 'pending'}">
                                <div>
                                    <strong>${target}x</strong>
                                    ${isReached ? `<span style="color: var(--accent-green); margin-left: 8px;">✓ Reached</span>` : ''}
                                </div>
                                <div style="color: var(--text-muted); font-size: 0.85rem;">
                                    ${isReached ? formatCurrency(reached.mcap_at_milestone) : 'Pending'}
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>

            <div style="margin-top: 24px; display: flex; gap: 12px;">
                <a href="https://dexscreener.com/solana/${token.address}" target="_blank" class="btn btn-primary" style="flex: 1; justify-content: center;">
                    📊 View Chart
                </a>
                <button class="btn btn-secondary" style="flex: 1; justify-content: center;" onclick="handlePromote('${token.address}')">
                    💰 Promote
                </button>
            </div>
        `;
    } catch (err) {
        body.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⚠️</div>
                <h3>Error Loading Token</h3>
                <p>Unable to fetch token details.</p>
            </div>
        `;
    }
}

function initModal() {
    const modal = document.getElementById('tokenModal');
    const overlay = document.getElementById('modalOverlay');
    const closeBtn = document.getElementById('modalClose');

    function closeModal() {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }

    overlay.addEventListener('click', closeModal);
    closeBtn.addEventListener('click', closeModal);

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
    });
}

// ─── FORM SUBMISSION ───
function initForm() {
    const form = document.getElementById('submitForm');
    const message = document.getElementById('formMessage');

    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        const address = data.address.trim();
        if (!address || address.length < 32 || address.length > 44) {
            showFormMessage('Invalid Solana address. Must be 32-44 characters.', 'error');
            return;
        }

        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<span>⏳</span> Submitting...';
        submitBtn.disabled = true;

        try {
            const res = await fetch(`${API_URL}/listing-request`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await res.json();

            if (res.ok || res.status === 201 || res.status === 202) {
                showFormMessage(result.message || 'Token submitted successfully!', 'success');
                form.reset();

                setTimeout(() => {
                    loadAllData();
                }, 1000);
            } else {
                showFormMessage(result.error || 'Failed to submit token.', 'error');
            }
        } catch (err) {
            showFormMessage('Network error. Please try again.', 'error');
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    });
}

function showFormMessage(text, type) {
    const message = document.getElementById('formMessage');
    message.textContent = text;
    message.className = `form-message ${type}`;

    setTimeout(() => {
        message.className = 'form-message';
    }, 5000);
}

// ─── TOAST ───
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// ─── UTILITIES ───
function formatCurrency(value) {
    if (!value || value === 0) return '$0';

    if (value >= 1e9) {
        return '$' + (value / 1e9).toFixed(2) + 'B';
    } else if (value >= 1e6) {
        return '$' + (value / 1e6).toFixed(2) + 'M';
    } else if (value >= 1e3) {
        return '$' + (value / 1e3).toFixed(2) + 'K';
    } else if (value >= 1) {
        return '$' + value.toFixed(2);
    } else {
        return '$' + value.toFixed(6);
    }
}

function shortenAddress(address) {
    if (!address) return '';
    return address.slice(0, 6) + '...' + address.slice(-4);
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ─── NAVBAR SCROLL EFFECT ───
let lastScroll = 0;
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    const currentScroll = window.pageYOffset;

    if (currentScroll > 50) {
        navbar.style.background = 'rgba(10, 10, 15, 0.95)';
        navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.3)';
    } else {
        navbar.style.background = 'rgba(10, 10, 15, 0.85)';
        navbar.style.boxShadow = 'none';
    }

    lastScroll = currentScroll;
});
