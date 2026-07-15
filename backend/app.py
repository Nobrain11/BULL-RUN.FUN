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
        'updated_at': token.updated_at.isoformat() if token.updated_at else None
    }

# ─── API ENDPOINTS ───

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'service': 'Bull Run API'})

@app.route('/api/tokens/trending', methods=['GET'])
def get_trending():
    """Get trending tokens: sponsored first, then by multiplier desc"""
    filter_type = request.args.get('filter', 'all')

    query = Token.query.filter(Token.status == 'active')

    if filter_type == 'sponsored':
        query = query.filter(Token.is_sponsored == True)
    elif filter_type == 'top10':
        query = query.order_by(Token.current_multiplier.desc()).limit(10)
    else:
        # Sponsored first, then by multiplier
        query = query.order_by(
            Token.is_sponsored.desc(),
            Token.sponsor_position.asc(),
            Token.current_multiplier.desc()
        ).limit(50)

    tokens = query.all()
    return jsonify({
        'tokens': [token_to_dict(t) for t in tokens],
        'count': len(tokens)
    })

@app.route('/api/tokens/new', methods=['GET'])
def get_new():
    """Get 10 most recently listed tokens"""
    tokens = Token.query.filter(Token.status == 'active').order_by(
        Token.created_at.desc()
    ).limit(10).all()

    return jsonify({
        'tokens': [token_to_dict(t) for t in tokens],
        'count': len(tokens)
    })

@app.route('/api/tokens/sponsored', methods=['GET'])
def get_sponsored():
    """Get active sponsored tokens"""
    tokens = Token.query.filter(
        Token.is_sponsored == True,
        Token.status == 'active'
    ).order_by(Token.sponsor_position.asc()).all()

    return jsonify({
        'tokens': [token_to_dict(t) for t in tokens],
        'count': len(tokens)
    })

@app.route('/api/tokens/<address>', methods=['GET'])
def get_token_detail(address):
    """Get full token details + milestone history"""
    if not is_valid_solana_address(address):
        return jsonify({'error': 'Invalid Solana address'}), 400

    token = Token.query.filter_by(address=address).first()
    if not token:
        return jsonify({'error': 'Token not found'}), 404

    milestones = Milestone.query.filter_by(token_address=address).order_by(
        Milestone.multiplier.asc()
    ).all()

    result = token_to_dict(token)
    result['milestones'] = [{
        'multiplier': m.multiplier,
        'mcap_at_milestone': m.mcap_at_milestone,
        'reached_at': m.reached_at.isoformat() if m.reached_at else None,
        'alert_sent': m.alert_sent
    } for m in milestones]

    return jsonify(result)

@app.route('/api/listing-request', methods=['POST'])
def submit_listing():
    """Submit token for listing - auto-approve if data fetch succeeds"""
    data = request.get_json() or {}

    address = data.get('address', '').strip()
    if not is_valid_solana_address(address):
        return jsonify({'error': 'Invalid Solana address'}), 400

    # Check if already exists
    existing = Token.query.filter_by(address=address).first()
    if existing:
        return jsonify({'error': 'Token already listed', 'token': token_to_dict(existing)}), 409

    # Fetch token data
    token_data = fetch_token_data(address)

    if token_data:
        # Auto-approve
        token = Token(
            address=address,
            name=token_data.get('name', data.get('name', 'Unknown')),
            symbol=token_data.get('symbol', data.get('symbol', 'UNKNOWN')),
            description=data.get('description', ''),
            logo_url=token_data.get('logo_url', data.get('logo_url', '')),
            twitter=data.get('twitter', ''),
            telegram=data.get('telegram', ''),
            website=data.get('website', ''),
            price=token_data.get('price', 0),
            market_cap=token_data.get('market_cap', 0),
            volume_24h=token_data.get('volume_24h', 0),
            baseline_mcap=token_data.get('market_cap', 0) or 1,
            current_multiplier=1.0,
            status='active'
        )
        db.session.add(token)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Token auto-listed successfully',
            'token': token_to_dict(token)
        }), 201
    else:
        # Create pending request
        req = ListingRequest(
            token_address=address,
            name=data.get('name'),
            symbol=data.get('symbol'),
            description=data.get('description'),
            logo_url=data.get('logo_url'),
            twitter=data.get('twitter'),
            telegram=data.get('telegram'),
            website=data.get('website'),
            submitted_by=data.get('submitted_by'),
            status='pending'
        )
        db.session.add(req)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Listing request submitted for review',
            'request_id': req.id
        }), 202

@app.route('/api/vote/<address>', methods=['POST'])
def vote_token(address):
    """Register a vote (IP-based duplicate prevention)"""
    if not is_valid_solana_address(address):
        return jsonify({'error': 'Invalid address'}), 400

    token = Token.query.filter_by(address=address).first()
    if not token:
        return jsonify({'error': 'Token not found'}), 404

    # Get IP address
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip:
        ip = ip.split(',')[0].strip()

    # Check for existing vote
    existing = Vote.query.filter_by(token_address=address, ip_address=ip).first()
    if existing:
        return jsonify({'error': 'Already voted from this IP'}), 429

    vote = Vote(token_address=address, ip_address=ip)
    db.session.add(vote)
    token.vote_count += 1
    db.session.commit()

    return jsonify({
        'success': True,
        'vote_count': token.vote_count
    })

@app.route('/api/share/<address>', methods=['POST'])
def share_token(address):
    """Increment share count"""
    if not is_valid_solana_address(address):
        return jsonify({'error': 'Invalid address'}), 400

    token = Token.query.filter_by(address=address).first()
    if not token:
        return jsonify({'error': 'Token not found'}), 404

    token.share_count += 1
    db.session.commit()

    share_url = f"https://bullrun.app/token/{address}"

    return jsonify({
        'success': True,
        'share_count': token.share_count,
        'share_url': share_url
    })

@app.route('/api/sponsor', methods=['POST'])
def create_sponsorship():
    """Create a sponsorship (called by bot)"""
    data = request.get_json() or {}

    address = data.get('token_address', '').strip()
    package = data.get('package', '').strip()
    user_id = data.get('user_id')
    tx_signature = data.get('transaction_signature', '')

    if not is_valid_solana_address(address):
        return jsonify({'error': 'Invalid token address'}), 400

    if package not in ['top5', 'top10', 'pinned', 'boost']:
        return jsonify({'error': 'Invalid package type'}), 400

    token = Token.query.filter_by(address=address).first()
    if not token:
        return jsonify({'error': 'Token not found'}), 404

    # Package pricing
    prices = {'top5': 2.5, 'top10': 1.0, 'pinned': 4.0, 'boost': 0.5}
    price = prices.get(package, 0.5)

    # Calculate position and duration
    position = 0
    duration_hours = 24

    if package == 'top5':
        position = 1
        duration_hours = 24
    elif package == 'top10':
        position = 6
        duration_hours = 24
    elif package == 'pinned':
        token.is_featured = True
        duration_hours = 72
    elif package == 'boost':
        duration_hours = 5

    # Create sponsorship record
    sponsor = Sponsored(
        token_address=address,
        package=package,
        price=price,
        position=position,
        start_time=datetime.utcnow(),
        end_time=datetime.utcnow() + timedelta(hours=duration_hours),
        is_active=True,
        transaction_signature=tx_signature,
        user_id=user_id
    )

    # Update token
    token.is_sponsored = True
    if position > 0:
        token.sponsor_position = position

    # Record revenue
    revenue = Revenue(
        token_address=address,
        user_id=user_id,
        package=package,
        amount=price,
        transaction_signature=tx_signature
    )

    # Update user spending
    user = User.query.filter_by(user_id=user_id).first()
    if user:
        user.total_spent += price

    db.session.add(sponsor)
    db.session.add(revenue)
    db.session.commit()

    return jsonify({
        'success': True,
        'sponsorship_id': sponsor.id,
        'package': package,
        'price': price,
        'expires_at': sponsor.end_time.isoformat()
    })

@app.route('/api/admin/stats', methods=['GET'])
def get_admin_stats():
    """Return dashboard stats"""
    total_tokens = Token.query.count()
    active_tokens = Token.query.filter_by(status='active').count()
    total_votes = db.session.query(db.func.sum(Token.vote_count)).scalar() or 0
    total_revenue = db.session.query(db.func.sum(Revenue.amount)).scalar() or 0
    pending_requests = ListingRequest.query.filter_by(status='pending').count()
    active_sponsorships = Sponsored.query.filter_by(is_active=True).count()

    return jsonify({
        'total_tokens': total_tokens,
        'active_tokens': active_tokens,
        'total_votes': int(total_votes),
        'total_revenue_sol': round(total_revenue, 4),
        'pending_requests': pending_requests,
        'active_sponsorships': active_sponsorships
    })

@app.route('/api/user/<int:user_id>/promotions', methods=['GET'])
def get_user_promotions(user_id):
    """Get user's promotions"""
    sponsorships = Sponsored.query.filter_by(user_id=user_id).order_by(
        Sponsored.created_at.desc()
    ).all()

    return jsonify({
        'promotions': [{
            'id': s.id,
            'token_address': s.token_address,
            'package': s.package,
            'price': s.price,
            'is_active': s.is_active,
            'start_time': s.start_time.isoformat() if s.start_time else None,
            'end_time': s.end_time.isoformat() if s.end_time else None
        } for s in sponsorships]
    })

@app.route('/api/tokens/update-prices', methods=['POST'])
def update_token_prices():
    """Background endpoint to update all token prices and check milestones"""
    tokens = Token.query.filter(Token.status == 'active').all()
    alerts = []

    for token in tokens:
        try:
            data = fetch_token_data(token.address)
            if not data:
                continue

            token.price = data.get('price', token.price)
            token.market_cap = data.get('market_cap', token.market_cap)
            token.volume_24h = data.get('volume_24h', token.volume_24h)
            token.updated_at = datetime.utcnow()

            # Calculate multiplier
            if token.baseline_mcap > 0:
                token.current_multiplier = token.market_cap / token.baseline_mcap

            if token.current_multiplier > token.highest_multiplier:
                token.highest_multiplier = token.current_multiplier

            # Check milestones (2x, 4x, 6x, 8x, 10x)
            milestones_to_check = [2, 4, 6, 8, 10]
            for m in milestones_to_check:
                if token.current_multiplier >= m:
                    existing = Milestone.query.filter_by(
                        token_address=token.address,
                        multiplier=m
                    ).first()

                    if not existing:
                        milestone = Milestone(
                            token_address=token.address,
                            multiplier=m,
                            mcap_at_milestone=token.market_cap,
                            alert_sent=False
                        )
                        db.session.add(milestone)
                        alerts.append({
                            'token_address': token.address,
                            'token_name': token.name,
                            'token_symbol': token.symbol,
                            'multiplier': m,
                            'market_cap': token.market_cap,
                            'volume_24h': token.volume_24h
                        })

            db.session.commit()
        except Exception as e:
            app.logger.error(f"Error updating token {token.address}: {e}")
            db.session.rollback()

    return jsonify({
        'updated': len(tokens),
        'new_milestones': len(alerts),
        'alerts': alerts
    })

# ─── ERROR HANDLERS ───

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

# ─── INIT ───

# Create tables on startup — runs both under `python app.py` and under
# gunicorn (Render's production server), since gunicorn imports this
# module directly and never hits the __main__ block below.
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=False)
