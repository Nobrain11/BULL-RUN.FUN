# bot/bot.py
"""
🐂 Bull Run Telegram Bot
100% button-based bot for token submissions, promotion purchases, and milestone alerts.
"""

import os
import logging
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ─── CONFIG ───
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID', '@your_channel_username')
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', '0'))
WALLET_ADDRESS = os.getenv('WALLET_ADDRESS', 'CKcTpCNiohtJ4WdaHXXQURNnoMeCDC6qt21TXLaQK1VS')
API_URL = os.getenv('API_URL', 'https://your-backend.onrender.com/api')
SOLSCAN_API = 'https://public-api.solscan.io'

# Package pricing
PACKAGES = {
    'top5': {'name': 'Top 1-5', 'price': 2.5, 'duration': 24},
    'top10': {'name': 'Top 6-10', 'price': 1.0, 'duration': 24},
    'pinned': {'name': 'Pinned', 'price': 4.0, 'duration': 72},
    'boost': {'name': 'Boost', 'price': 0.5, 'duration': 5}
}

# Conversation states
MENU, AWAITING_ADDRESS, SELECTING_PACKAGE, AWAITING_PAYMENT = range(4)

# ─── LOGGING ───
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ─── HELPERS ───

def is_valid_solana_address(address):
    """Validate Solana address format"""
    if not address or len(address) < 32 or len(address) > 44:
        return False
    import re
    return bool(re.match(r'^[1-9A-HJ-NP-Za-km-z]+$', address))

def fetch_token_data(address):
    """Fetch token data from API"""
    try:
        resp = requests.get(f"{API_URL}/tokens/{address}", timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        logger.error(f"Fetch token error: {e}")
    return None

def verify_sol_payment(user_wallet, expected_amount, minutes=10):
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

            if WALLET_ADDRESS in str(tx):
                amount = tx.get('lamport', 0) / 1e9
                if abs(amount - expected_amount) < 0.001:
                    return tx.get('signature', '')

        return False
    except Exception as e:
        logger.error(f"Payment verification error: {e}")
        return False

def format_number(num):
    """Format large numbers"""
    if num >= 1e9:
        return f"${num/1e9:.2f}B"
    elif num >= 1e6:
        return f"${num/1e6:.2f}M"
    elif num >= 1e3:
        return f"${num/1e3:.2f}K"
    else:
        return f"${num:.4f}"

def get_main_menu_keyboard():
    """Main menu inline keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Submit Token", callback_data='submit_token')],
        [InlineKeyboardButton("📈 View Trending", callback_data='view_trending')],
        [InlineKeyboardButton("💎 My Promotions", callback_data='my_promotions')],
        [InlineKeyboardButton("❓ Help", callback_data='help')]
    ])

def get_package_keyboard():
    """Package selection keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🥇 Top 1-5", callback_data='pkg_top5')],
        [InlineKeyboardButton("🥈 Top 6-10", callback_data='pkg_top10')],
        [InlineKeyboardButton("📌 Pinned", callback_data='pkg_pinned')],
        [InlineKeyboardButton("⚡ Boost", callback_data='pkg_boost')],
        [InlineKeyboardButton("◀️ Back", callback_data='back_to_menu')]
    ])

def get_payment_keyboard(package):
    """Payment confirmation keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 I've Paid", callback_data=f'confirm_payment_{package}')],
        [InlineKeyboardButton("◀️ Back", callback_data='back_to_packages')]
    ])

# ─── COMMAND HANDLERS ───

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user

    args = context.args
    if args and args[0].startswith('promote_'):
        token_address = args[0].replace('promote_', '')
        if is_valid_solana_address(token_address):
            context.user_data['current_token'] = token_address
            context.user_data['step'] = 'selecting_package'

            token = fetch_token_data(token_address)
            token_name = token.get('name', 'Unknown') if token else 'Unknown'

            await update.message.reply_text(
                f"🚀 <b>Promote Token</b>\n\n"
                f"Token: <code>{token_name}</code>\n"
                f"Address: <code>{token_address}</code>\n\n"
                f"Select a promotion package:",
                reply_markup=get_package_keyboard(),
                parse_mode='HTML'
            )
            return SELECTING_PACKAGE

    welcome_text = (
        f"🐂 <b>Welcome to Bull Run!</b>\n\n"
        f"Discover and promote trending Solana tokens.\n\n"
        f"<b>What you can do:</b>\n"
        f"• 🚀 Submit tokens for listing\n"
        f"• 📈 View trending tokens\n"
        f"• 💎 Buy promotion packages\n"
        f"• 🔔 Get milestone alerts\n\n"
        f"Choose an option below:"
    )

    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode='HTML'
    )
    return MENU

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = (
        "🐂 <b>Bull Run Help</b>\n\n"
        "<b>Commands:</b>\n"
        "/start — Main menu\n"
        "/help — This message\n\n"
        "<b>Promotion Packages:</b>\n"
        "🥇 <b>Top 1-5</b> — 2.5 SOL (24h)\n"
        "🥈 <b>Top 6-10</b> — 1.0 SOL (24h)\n"
        "📌 <b>Pinned</b> — 4.0 SOL (72h)\n"
        "⚡ <b>Boost</b> — 0.5 SOL (5h)\n\n"
        "<b>How it works:</b>\n"
        "1. Select a token to promote\n"
        "2. Choose a package\n"
        "3. Send SOL to the wallet\n"
        "4. Click 'I've Paid'\n"
        "5. Bot verifies and activates!\n\n"
        "<b>Wallet:</b>\n"
        f"<code>{WALLET_ADDRESS}</code>\n\n"
        "Questions? Contact @BullRunSupport"
    )

    await update.message.reply_text(help_text, parse_mode='HTML')

# ─── CALLBACK HANDLERS ───

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all callback queries"""
    query = update.callback_query
    await query.answer()

    data = query.data
    user = update.effective_user

    if data == 'submit_token':
        context.user_data['step'] = 'awaiting_address'
        await query.edit_message_text(
            "🚀 <b>Submit Your Token</b>\n\n"
            "Please send me the Solana token address.\n"
            "The bot will automatically fetch data from DexScreener.\n\n"
            "Example: <code>EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v</code>\n\n"
            "Or click ◀️ Back to cancel.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("◀️ Back", callback_data='back_to_menu')]
            ]),
            parse_mode='HTML'
        )
        return AWAITING_ADDRESS

    elif data == 'view_trending':
        await show_trending(query, context)
        return MENU

    elif data == 'my_promotions':
        await show_promotions(query, context, user.id)
        return MENU

    elif data == 'help':
        help_text = (
            "🐂 <b>Bull Run Help</b>\n\n"
            "<b>Promotion Packages:</b>\n"
            "🥇 <b>Top 1-5</b> — 2.5 SOL (24h)\n"
            "🥈 <b>Top 6-10</b> — 1.0 SOL (24h)\n"
            "📌 <b>Pinned</b> — 4.0 SOL (72h)\n"
            "⚡ <b>Boost</b> — 0.5 SOL (5h)\n\n"
            "<b>How it works:</b>\n"
            "1. Select a token to promote\n"
            "2. Choose a package\n"
            "3. Send SOL to the wallet\n"
            "4. Click 'I've Paid'\n"
            "5. Bot verifies and activates!\n\n"
            "<b>Wallet:</b>\n"
            f"<code>{WALLET_ADDRESS}</code>"
        )
        await query.edit_message_text(
            help_text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("◀️ Back to Menu", callback_data='back_to_menu')]
            ]),
            parse_mode='HTML'
        )
        return MENU

    elif data == 'back_to_menu':
        await query.edit_message_text(
            "🐂 <b>Bull Run</b>\n\n"
            "Discover and promote trending Solana tokens.\n\n"
            "Choose an option:",
            reply_markup=get_main_menu_keyboard(),
            parse_mode='HTML'
        )
        context.user_data.clear()
        return MENU

    elif data == 'back_to_packages':
        context.user_data['step'] = 'selecting_package'
        token_address = context.user_data.get('current_token', '')
        token = fetch_token_data(token_address)
        token_name = token.get('name', 'Unknown') if token else 'Unknown'

        await query.edit_message_text(
            f"🚀 <b>Promote Token</b>\n\n"
            f"Token: <code>{token_name}</code>\n"
            f"Address: <code>{token_address}</code>\n\n"
            f"Select a promotion package:",
            reply_markup=get_package_keyboard(),
            parse_mode='HTML'
        )
        return SELECTING_PACKAGE

    elif data.startswith('pkg_'):
        package = data.replace('pkg_', '')
        context.user_data['selected_package'] = package
        context.user_data['step'] = 'awaiting_payment'

        pkg_info = PACKAGES[package]
        token_address = context.user_data.get('current_token', '')
        token = fetch_token_data(token_address)
        token_name = token.get('name', 'Unknown') if token else 'Unknown'

        await query.edit_message_text(
            f"💰 <b>Payment Required</b>\n\n"
            f"Token: <code>{token_name}</code>\n"
            f"Package: <b>{pkg_info['name']}</b>\n"
            f"Price: <b>{pkg_info['price']} SOL</b>\n"
            f"Duration: <b>{pkg_info['duration']} hours</b>\n\n"
            f"<b>Send exactly {pkg_info['price']} SOL to:</b>\n"
            f"<code>{WALLET_ADDRESS}</code>\n\n"
            f"⚠️ <i>Make sure to send from the wallet you'll use for verification.</i>\n\n"
            f"After sending, click 'I've Paid' below.",
            reply_markup=get_payment_keyboard(package),
            parse_mode='HTML'
        )
        return AWAITING_PAYMENT

    elif data.startswith('confirm_payment_'):
        package = data.replace('confirm_payment_', '')
        await handle_payment_confirmation(query, context, package)
        return MENU

    elif data.startswith('promote_'):
        token_address = data.replace('promote_', '')
        if is_valid_solana_address(token_address):
            context.user_data['current_token'] = token_address
            context.user_data['step'] = 'selecting_package'

            token = fetch_token_data(token_address)
            token_name = token.get('name', 'Unknown') if token else 'Unknown'

            await query.edit_message_text(
                f"🚀 <b>Promote Token</b>\n\n"
                f"Token: <code>{token_name}</code>\n"
                f"Address: <code>{token_address}</code>\n\n"
                f"Select a promotion package:",
                reply_markup=get_package_keyboard(),
                parse_mode='HTML'
            )
            return SELECTING_PACKAGE

    return MENU

async def show_trending(query, context):
    """Show trending tokens"""
    try:
        resp = requests.get(f"{API_URL}/tokens/trending?filter=top10", timeout=10)
        if resp.status_code != 200:
            await query.edit_message_text(
                "❌ Failed to load trending tokens. Please try again.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Retry", callback_data='view_trending')],
                    [InlineKeyboardButton("◀️ Back", callback_data='back_to_menu')]
                ])
            )
            return

        data = resp.json()
        tokens = data.get('tokens', [])

        if not tokens:
            await query.edit_message_text(
                "📈 No trending tokens found yet.\n\n"
                "Submit your token to be the first!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🚀 Submit Token", callback_data='submit_token')],
                    [InlineKeyboardButton("◀️ Back", callback_data='back_to_menu')]
                ])
            )
            return

        text = "📈 <b>Top 10 Trending Tokens</b>\n\n"

        for i, token in enumerate(tokens[:10], 1):
            mcap = format_number(token.get('market_cap', 0))
            mult = token.get('current_multiplier', 1)
            votes = token.get('vote_count', 0)

            badge = ""
            if token.get('is_sponsored'):
                badge = " ⭐"

            text += (
                f"{i}. <b>{token.get('name', 'Unknown')}</b>{badge}\n"
                f"   💰 MCap: {mcap} | 📈 {mult:.2f}x | 👍 {votes}\n"
                f"   <code>{token.get('address', '')}</code>\n\n"
            )

        keyboard = []
        for token in tokens[:5]:
            keyboard.append([
                InlineKeyboardButton(
                    f"💰 Promote {token.get('symbol', 'Token')}",
                    callback_data=f"promote_{token.get('address', '')}"
                )
            ])

        keyboard.append([InlineKeyboardButton("◀️ Back", callback_data='back_to_menu')])

        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

    except Exception as e:
        logger.error(f"Show trending error: {e}")
        await query.edit_message_text(
            "❌ Error loading trending tokens.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("◀️ Back", callback_data='back_to_menu')]
            ])
        )

async def show_promotions(query, context, user_id):
    """Show user's promotions"""
    try:
        resp = requests.get(f"{API_URL}/user/{user_id}/promotions", timeout=10)
        if resp.status_code != 200:
            await query.edit_message_text(
                "❌ Failed to load your promotions.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("◀️ Back", callback_data='back_to_menu')]
                ])
            )
            return

        data = resp.json()
        promotions = data.get('promotions', [])

        if not promotions:
            await query.edit_message_text(
                "💎 <b>My Promotions</b>\n\n"
                "You don't have any active promotions yet.\n\n"
                "Promote your token to see it here!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🚀 Submit Token", callback_data='submit_token')],
                    [InlineKeyboardButton("◀️ Back", callback_data='back_to_menu')]
                ]),
                parse_mode='HTML'
            )
            return

        text = "💎 <b>My Promotions</b>\n\n"

        for promo in promotions:
            status = "🟢 Active" if promo.get('is_active') else "🔴 Expired"
            pkg = PACKAGES.get(promo.get('package', ''), {})
            pkg_name = pkg.get('name', promo.get('package', 'Unknown'))

            text += (
                f"<b>{pkg_name}</b> — {status}\n"
                f"Token: <code>{promo.get('token_address', '')[:20]}...</code>\n"
                f"Price: {promo.get('price', 0)} SOL\n"
                f"Started: {promo.get('start_time', 'N/A')[:10]}\n"
                f"Expires: {promo.get('end_time', 'N/A')[:10]}\n\n"
            )

        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("◀️ Back", callback_data='back_to_menu')]
            ]),
            parse_mode='HTML'
        )

    except Exception as e:
        logger.error(f"Show promotions error: {e}")
        await query.edit_message_text(
            "❌ Error loading promotions.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("◀️ Back", callback_data='back_to_menu')]
            ])
        )

async def handle_payment_confirmation(query, context, package):
    """Handle payment verification"""
    user = query.from_user
    token_address = context.user_data.get('current_token', '')
    pkg_info = PACKAGES.get(package, {})

    if not token_address or not pkg_info:
        await query.edit_message_text(
            "❌ Session expired. Please start over.",
            reply_markup=get_main_menu_keyboard()
        )
        return

    await query.edit_message_text(
        "⏳ <b>Verifying Payment...</b>\n\n"
        "Please send the wallet address you used to send SOL from.\n"
        "The bot will check for the transaction on Solscan.\n\n"
        "Example: <code>YourWalletAddressHere</code>",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ Cancel", callback_data='back_to_packages')]
        ]),
        parse_mode='HTML'
    )

    context.user_data['awaiting_wallet'] = True
    context.user_data['package_to_confirm'] = package

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    user = update.effective_user
    text = update.message.text.strip()
    step = context.user_data.get('step', 'idle')

    if context.user_data.get('awaiting_wallet'):
        wallet = text
        package = context.user_data.get('package_to_confirm', '')
        token_address = context.user_data.get('current_token', '')
        pkg_info = PACKAGES.get(package, {})

        if not is_valid_solana_address(wallet):
            await update.message.reply_text(
                "❌ Invalid wallet address. Please send a valid Solana address.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("◀️ Cancel", callback_data='back_to_packages')]
                ])
            )
            return

        await update.message.reply_text("⏳ Checking Solscan for your payment...")

        tx_signature = verify_sol_payment(wallet, pkg_info['price'])

        if not tx_signature:
            await update.message.reply_text(
                "❌ <b>Payment Not Found</b>\n\n"
                "No matching transaction found in the last 10 minutes.\n\n"
                "Please make sure:\n"
                "• You sent exactly the required amount\n"
                "• You sent to the correct wallet\n"
                "• The transaction is confirmed on Solana\n\n"
                "Try again or contact support.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Try Again", callback_data=f'confirm_payment_{package}')],
                    [InlineKeyboardButton("◀️ Back", callback_data='back_to_packages')]
                ]),
                parse_mode='HTML'
            )
            context.user_data['awaiting_wallet'] = False
            return

        try:
            resp = requests.post(f"{API_URL}/sponsor", json={
                'token_address': token_address,
                'package': package,
                'user_id': user.id,
                'transaction_signature': tx_signature
            }, timeout=10)

            if resp.status_code in [200, 201]:
                result = resp.json()

                token = fetch_token_data(token_address)
                token_name = token.get('name', 'Unknown') if token else 'Unknown'
                token_symbol = token.get('symbol', 'UNKNOWN') if token else 'UNKNOWN'

                channel_text = (
                    f"⭐ <b>New Sponsored Token!</b>\n\n"
                    f"🚀 <b>{token_name}</b> (${token_symbol})\n"
                    f"📦 Package: {pkg_info['name']}\n"
                    f"💰 {pkg_info['price']} SOL paid\n\n"
                    f"Check it out on Bull Run!"
                )

                try:
                    await context.bot.send_message(
                        chat_id=CHANNEL_ID,
                        text=channel_text,
                        parse_mode='HTML'
                    )
                except Exception as e:
                    logger.error(f"Channel announcement error: {e}")

                await update.message.reply_text(
                    f"✅ <b>Payment Verified!</b>\n\n"
                    f"Your {pkg_info['name']} promotion is now active.\n"
                    f"Token: <code>{token_name}</code>\n"
                    f"Expires: {result.get('expires_at', 'N/A')[:10]}\n\n"
                    f"Transaction: <code>{tx_signature[:20]}...</code>\n\n"
                    f"Thank you for using Bull Run! 🐂",
                    reply_markup=get_main_menu_keyboard(),
                    parse_mode='HTML'
                )

                context.user_data.clear()
                return MENU
            else:
                await update.message.reply_text(
                    "❌ Failed to activate promotion. Please contact support.",
                    reply_markup=get_main_menu_keyboard()
                )
                context.user_data.clear()
                return MENU

        except Exception as e:
            logger.error(f"Sponsorship creation error: {e}")
            await update.message.reply_text(
                "❌ Error creating sponsorship. Please contact support.",
                reply_markup=get_main_menu_keyboard()
            )
            context.user_data.clear()
            return MENU

    if step == 'awaiting_address':
        address = text

        if not is_valid_solana_address(address):
            await update.message.reply_text(
                "❌ Invalid Solana address. Please check and try again.\n\n"
                "A valid address is 32-44 characters long and uses base58 characters.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("◀️ Back", callback_data='back_to_menu')]
                ])
            )
            return AWAITING_ADDRESS

        await update.message.reply_text("⏳ Fetching token data from DexScreener...")

        try:
            resp = requests.post(f"{API_URL}/listing-request", json={
                'address': address,
                'submitted_by': user.id
            }, timeout=15)

            result = resp.json()

            if resp.status_code == 201:
                token = result.get('token', {})
                await update.message.reply_text(
                    f"✅ <b>Token Listed Successfully!</b>\n\n"
                    f"Name: <b>{token.get('name', 'Unknown')}</b>\n"
                    f"Symbol: <b>${token.get('symbol', 'UNKNOWN')}</b>\n"
                    f"Price: {format_number(token.get('price', 0))}\n"
                    f"Market Cap: {format_number(token.get('market_cap', 0))}\n\n"
                    f"Your token is now live on Bull Run! 🎉\n\n"
                    f"Want to boost visibility? Promote it now!",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("💰 Promote This Token", callback_data=f"promote_{address}")],
                        [InlineKeyboardButton("◀️ Main Menu", callback_data='back_to_menu')]
                    ]),
                    parse_mode='HTML'
                )
                context.user_data.clear()
                return MENU

            elif resp.status_code == 202:
                await update.message.reply_text(
                    f"⏳ <b>Token Submitted for Review</b>\n\n"
                    f"Address: <code>{address}</code>\n"
                    f"Request ID: #{result.get('request_id', 'N/A')}\n\n"
                    f"We couldn't auto-fetch data from DexScreener. "
                    f"Your token will be reviewed and listed shortly.\n\n"
                    f"You'll be notified once it's approved!",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("◀️ Main Menu", callback_data='back_to_menu')]
                    ]),
                    parse_mode='HTML'
                )
                context.user_data.clear()
                return MENU

            elif resp.status_code == 409:
                token = result.get('token', {})
                await update.message.reply_text(
                    f"ℹ️ <b>Token Already Listed!</b>\n\n"
                    f"Name: <b>{token.get('name', 'Unknown')}</b>\n"
                    f"Symbol: <b>${token.get('symbol', 'UNKNOWN')}</b>\n\n"
                    f"This token is already on Bull Run.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("💰 Promote This Token", callback_data=f"promote_{address}")],
                        [InlineKeyboardButton("◀️ Main Menu", callback_data='back_to_menu')]
                    ]),
                    parse_mode='HTML'
                )
                context.user_data.clear()
                return MENU
            else:
                await update.message.reply_text(
                    f"❌ Error: {result.get('error', 'Unknown error')}",
                    reply_markup=get_main_menu_keyboard()
                )
                context.user_data.clear()
                return MENU

        except Exception as e:
            logger.error(f"Token submission error: {e}")
            await update.message.reply_text(
                "❌ Network error. Please try again later.",
                reply_markup=get_main_menu_keyboard()
            )
            context.user_data.clear()
            return MENU

    await update.message.reply_text(
        "🐂 Use the buttons below to navigate:",
        reply_markup=get_main_menu_keyboard()
    )
    return MENU

# ─── MILESTONE ALERTS (Background Job) ───

async def check_milestones(context: ContextTypes.DEFAULT_TYPE):
    """Background job: Check for new milestones and send alerts"""
    try:
        resp = requests.post(f"{API_URL}/tokens/update-prices", timeout=30)
        if resp.status_code != 200:
            logger.warning("Failed to update token prices")
            return

        data = resp.json()
        alerts = data.get('alerts', [])

        for alert in alerts:
            token_name = alert.get('token_name', 'Unknown')
            token_symbol = alert.get('token_symbol', 'UNKNOWN')
            multiplier = alert.get('multiplier', 0)
            mcap = format_number(alert.get('market_cap', 0))
            volume = format_number(alert.get('volume_24h', 0))
            address = alert.get('token_address', '')

            emoji = "🚀"
            if multiplier >= 10:
                emoji = "🌙"
            elif multiplier >= 8:
                emoji = "🔥"
            elif multiplier >= 6:
                emoji = "⚡"
            elif multiplier >= 4:
                emoji = "💎"

            message = (
                f"{emoji} <b>{token_name} HIT {int(multiplier)}x!</b>\n\n"
                f"💰 MCap: {mcap}\n"
                f"📈 Volume: {volume}\n"
                f"🔗 <code>{address}</code>\n\n"
                f"Track on Bull Run"
            )

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("💰 Promote This Token", callback_data=f"promote_{address}")],
                [InlineKeyboardButton("📊 View Chart", url=f"https://dexscreener.com/solana/{address}")]
            ])

            try:
                await context.bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=message,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
                logger.info(f"Milestone alert sent: {token_name} {multiplier}x")
            except Exception as e:
                logger.error(f"Failed to send milestone alert: {e}")

    except Exception as e:
        logger.error(f"Milestone check error: {e}")

# ─── MAIN ───

def main():
    """Start the bot"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not set! Exiting.")
        return

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.job_queue.run_repeating(
        check_milestones,
        interval=300,
        first=10
    )

    logger.info("🐂 Bull Run Bot started!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
