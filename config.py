import os

# ==========================================
# ⚡ STORE BOT - CONFIGURATION
# ==========================================

# 1. Telegram Bot Token (Get from @BotFather)
BOT_TOKEN = os.getenv("BOT_TOKEN", "9092141822:AAEojFzqLewKuK9tOGBAKBO_uOvg12l21-s")

# 2. Admin Telegram User IDs (Can be passed as comma-separated string in env)
_admin_ids_env = os.getenv("ADMIN_IDS", "7944664366,7643285650,8299459627")
ADMIN_IDS = [int(x.strip()) for x in _admin_ids_env.split(",") if x.strip().isdigit()]

# 3. Store Branding
STORE_NAME = os.getenv("STORE_NAME", "FF PANEL STORE")
STORE_TAGLINE = os.getenv("STORE_TAGLINE", "Next-Gen Automated Key Vault")
SUPPORT_LINK = os.getenv("SUPPORT_LINK", "https://t.me/PanelStoreSupport")
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "PanelStoreSupport")

# 4. Currency Conversion (INR to USD approx rate)
INR_TO_USD_RATE = float(os.getenv("INR_TO_USD_RATE", "0.0111"))  # ₹100 ~ $1.11

# 5. Payment Details
PAYTM_UPI_ID = os.getenv("PAYTM_UPI_ID", "7240207031@fam")         # UPI ID (FamPay / UPI)
PAYEE_NAME = os.getenv("PAYEE_NAME", "Tanishk Sharma")           # Payee Name
BINANCE_PAY_ID = os.getenv("BINANCE_PAY_ID", "")                     # Aapka Binance Pay ID
BKASH_NUMBER = os.getenv("BKASH_NUMBER", "")                       # Aapka bKash number
BKASH_RATE_TK = float(os.getenv("BKASH_RATE_TK", "1.20"))                    # 100 INR = 120 Taka (1.20 Tk/INR)

# 6. Referral Commission
REFERRAL_PERCENT = int(os.getenv("REFERRAL_PERCENT", "15"))  # 15% flat commission

# 7. External Channel Links
DOWNLOAD_CHANNEL_URL = os.getenv("DOWNLOAD_CHANNEL_URL", "https://t.me/+GFMaxSxDzsE2NGI1")
TUTORIAL_VIDEO_URL = os.getenv("TUTORIAL_VIDEO_URL", "https://t.me/+GFMaxSxDzsE2NGI1")

# 8. Database Path
DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "store.db"))
