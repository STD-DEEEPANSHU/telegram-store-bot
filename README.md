# ⚡ Telegram Key Store & Automated Delivery Bot

A production-ready Telegram Store Bot built with Python (`aiogram 3.x`), SQLite, Dynamic UPI QR payment generation, and Automated License Key Vault delivery.

---

## 🚀 Features

- 🛒 **Multi-Brand Product Catalog:** Categories, Brands, and Package duration selector (12 Hours, 1D, 3D, 7D, 15D, 30D).
- ⚡ **Direct UPI Checkout QR:** Real-time dynamic FamPay / Paytm / PhonePe UPI QR code generation.
- 🔑 **Instant Automated Delivery:** Pop and deliver unique license keys immediately upon wallet or direct checkout payment.
- 📸 **Manual Payment Screenshot Approval:** Admin review system with inline Accept / Reject buttons.
- 👥 **Referral System:** 15% flat commission with real-time balance tracking.
- 🎁 **Daily Lucky Dice:** Daily reward system to engage users.
- 👑 **Admin Panel:** Complete inventory management (`/admin` command) to view stats, broadcast messages, credit balance, and add license keys.

---

## ☁️ Deploy to Heroku

### Option 1: Via Heroku CLI / Git
```bash
# 1. Login to Heroku
heroku login

# 2. Create app
heroku create your-bot-name

# 3. Set Config Vars
heroku config:set BOT_TOKEN="your_bot_token_here"
heroku config:set ADMIN_IDS="7944664366,7643285650,8299459627"
heroku config:set PAYTM_UPI_ID="7240207031@fam"
heroku config:set PAYEE_NAME="Tanishk Sharma"

# 4. Deploy code
git push heroku main

# 5. Start worker dyno
heroku ps:scale worker=1
```

### Option 2: Connect GitHub Repo in Heroku Dashboard
1. Go to [Heroku Dashboard](https://dashboard.heroku.com/).
2. Click **New** ➔ **Create new app**.
3. Under **Deployment method**, select **GitHub**.
4. Search for `telegram-store-bot` and click **Connect**.
5. In **Settings** ➔ **Config Vars**, add your environment variables (`BOT_TOKEN`, `ADMIN_IDS`, `PAYTM_UPI_ID`, `PAYEE_NAME`).
6. In **Resources** tab, turn **ON** the `worker: python bot.py` dyno!

---

## 💻 Local Setup

```bash
# 1. Clone repository
git clone https://github.com/STD-DEEEPANSHU/telegram-store-bot.git
cd telegram-store-bot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run bot
python bot.py
```
