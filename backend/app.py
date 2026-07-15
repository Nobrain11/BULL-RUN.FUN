# backend/app.py
```python
# backend/app.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
import os
import requests
import re
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost/bullrun')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False

db = SQLAlchemy(app)
CORS(app)

# ─── CONFIG ───
WALLET_ADDRESS = os.getenv('WALLET_ADDRESS', 'CKcTpCNiohtJ4WdaHXXQURNnoMeCDC6qt21TXLaQK1VS')
SOLSCAN_API = 'https://public-api.solscan.io'
DEXSCREENER_API = 'https://api.dexscreener.com/latest/dex/tokens'
BIRDEYE_API = 'https://public-api.birdeye.so/defi'

# ─── MODELS ───

class Token(db.Model):
    __tablename__ = 'tokens'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(44), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text)
    logo_url = db.Column(db.String(500))
    twitter = db.Column(db.String(200))
    telegram = db.Column(db.String(200))
    website = db.Column(db.String(200))
    price = db.Column(db.Float, default=0.0)
    market_cap = db.Column(db.Float, default=0.0)
    volume_24h = db.Column(db.Float, default=0.0)
    baseline_mcap = db.Column(db.Float, default=0.0)
    current_multiplier = db.Column(db.Float, default=1.0)
    highest_multiplier = db.Column(db.Float, default=1.0)
    vote_count = db.Column(db.Integer, default=0)
    share_count = db.Column(db.Integer, default=0)
    is_sponsored = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    sponsor_position = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    milestones = db.relationship('Milestone', backref='token', lazy=True, cascade='all, delete-orphan')
    sponsorships = db.relationship('Sponsored', backref='token', lazy=True, cascade='all, delete-orphan')
    votes = db.relationship('Vote', backref='token', lazy=True, cascade='all, delete-orphan')

class Milestone(db.Model):
    __tablename__ = 'milestones'
    id = db.Column(db.Integer, primary_key=True)
    token_address = db.Column(db.String(44), db.ForeignKey('tokens.address', ondelete='CASCADE'), nullable=False, index=True)
    multiplier = db.Column(db.Float, nullable=False)
    mcap_at_milestone = db.Column(db.Float, nullable=False)
    reached_at = db.Column(db.DateTime, default=datetime.utcnow)
    alert_sent = db.Column(db.Boolean, default=False)

class Sponsored(db.Model):
    __tablename__ = 'sponsored'
    id = db.Column(db.Integer, primary_key=True)
    token_address = db.Column(db.String(44), db.ForeignKey('tokens.address', ondelete='CASCADE'), nullable=False, index=True)
    package = db.Column(db.String(20), nullable=False)  # top5, top10, pinned, boost
    price = db.Column(db.Float, nullable=False)
    position = db.Column(db.Integer, default=0)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    transaction_signature = db.Column(db.String(100))
    user_id = db.Column(db.BigInteger, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ListingRequest(db.Model):
    __tablename__ = 'listing_requests'
    id = db.Column(db.Integer, primary_key=True)
    token_address = db.Column(db.String(44), nullable=False, index=True)
    name = db.Column(db.String(100))
    symbol = db.Column(db.String(20))
    description = db.Column(db.Text)
    logo_url = db.Column(db.String(500))
    twitter = db.Column(db.String(200))
    telegram = db.Column(db.String(200))
    website = db.Column(db.String(200))
    submitted_by = db.Column(db.BigInteger)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)

class Vote(db.Model):
    __tablename__ = 'votes'
    id = db.Column(db.Integer, primary_key=True)
    token_address = db.Column(db.String(44), db.ForeignKey('tokens.address', ondelete='CASCADE'), nullable=False, index=True)
    ip_address = db.Column(db.String(45), nullable=False)
    voted_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('token_address', 'ip_address', name='unique_vote'),)

class Revenue(db.Model):
    __tablename__ = 'revenue'
    id = db.Column(db.Integer, primary_key=True)
    token_address = db.Column(db.String(44), nullable=False, index=True)
    user_id = db.Column(db.BigInteger, nullable=False)
    package = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    paid_at = db.Column(db.DateTime, default=datetime.utcnow)
    transaction_signature = db.Column(db.String(100))

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.BigInteger, unique=True, nullable=False)
    username = db.Column(db.String(100))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    wallet_address = db.Column(db.String(44))
    total_spent = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BotSession(db.Model):
    __tablename__ = 'bot_sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.BigInteger, unique=True, nullable=False)
    current_step = db.Column(db.String(50), default='idle')
    current_token = db.Column(db.String(44))
    temp_data = db.Column(db.JSON)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ─── HELPERS ───

def is_valid_solana_address(address):
    """Validate Solana address format (base58, 32-44 chars)"""
    if not address or len(address) < 32 or len(address) > 44:
        return False
    return bool(re.match(r'^[1-9A-HJ-NP-Za-km-z]+$', address))

def fetch_token_data(address):
    """Fetch token data from DexScreener, fallback to Birdeye"""
    try:
        # Try DexScreener first
        resp = requests.get(f"{DEXSCREENER_API}/{address}", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('pairs') and len(data['pairs']) > 0:
                pair = data['pairs'][0]
                return {
                    'name': pair.get('baseToken', {}).get('name', 'Unknown'),
                    'symbol': pair.get('baseToken', {}).get('symbol', 'UNKNOWN'),
                    'price': float(pair.get('priceUsd', 0) or 0),
                    'market_cap': float(pair.get('marketCap', 0) or 0),
                    'volume_24h': float(pair.get('volume', {}).get('h24', 0) or 0),
                    'logo_url': pair.get('info', {}).get('imageUrl', '')
                }
    except Exception as e:
        app.logger.error(f"DexScreener error: {e}")

    try:
        # Fallback to Birdeye
        headers = {'X-API-KEY': os.getenv('BIRDEYE_API_KEY', '')}
        resp = requests.get(f"{BIRDEYE_API}/token_price?address={address}", headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('success'):
                return {
                    'name': 'Unknown',
                    'symbol': 'UNKNOWN',
                    'price': float(data.get('data', {}).get('value', 0) or 0),
                    'market_cap': 0,
                    'volume_24h': 0,
                    'logo_url': ''
                }
    except Exception as e:
        app.logger.error(f"Birdeye error: {e}")

    return None

def verify_sol_payment(user_wallet, expected_amount, minutes=5):
    """Verify SOL payment via Solscan"""
    try:
        resp = requests.get(
            f"{SOLSCAN_API}/account/{user_wallet}/transactions?limit=20",
            timeout=10
        )
        if resp.status_code != 200:
            return False

        transactions = resp.json()
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)

        for tx in transactions:
            tx_time = datetime.fromtimestamp(tx.get('blockTime', 0))
            if tx_time < cutoff:
                continue

            # Check if transaction involves our wallet
            if WALLET_ADDRESS in str(tx):
                # Parse amount from lamports (1 SOL = 1e9 lamports)
                amount = tx.get('lamport', 0) / 1e9
                if abs(amount - expected_amount) < 0.001:
                    return tx.get('signature', '')

        return False
    except Exception as e:
        app.logger.error(f"Payment verification error: {e}")
        return False

def token_to_dict(token):
    """Serialize token to dict"""
    return {
        'address': token.address,
        'name': token.name,
        'symbol': token.symbol,
        'description': token.description,
        'logo_url': token.logo_url,
        'twitter': token.twitter,
        'telegram': token.telegram,
        'website': token.website,
        'price': token.price,
        'market_cap': token.market_cap,
        'volume_24h': token.volume_24h,
        'current_multiplier': token.current_multiplier,
        'highest_multiplier': token.highest_multiplier,
        'vote_count': token.vote_count,
        'share_count': token.share_count,
        'is_sponsored': token.is_sponsored,
        'is_featured': token.is_featured,
        'sponsor_position': token.sponsor_position,
        'status': token.status,
        'created_at': token.created_at.isoformat() if token.created_at else None,
        'updated_at': token.updated_at.isoformat() if token.updated_at else No<response clipped><NOTE>Result is longer than **10000 characters**, will be **truncated**.</NOTE>
