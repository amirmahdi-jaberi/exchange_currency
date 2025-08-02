# ExchangeBot ⚡️ – Telegram Exchange Bot

<p align="center">
  <a href="https://github.com/amirmahdi-jaberi/exchange_currency">
    <img src="https://img.shields.io/badge/platform-telegram-green.svg?logo=telegram" alt="Telegram">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/github/license/amirmahdi-jaberi/exchange_currency.svg" alt="License: MIT">
  </a>
  <img src="https://img.shields.io/librariesio/release/pypi/telebot?logo=python" alt="Dependencies">
</p>

**ExchangeBot** — A Telegram bot powering exchange services for Iranian users, featuring real-time cryptocurrency pricing, trade operations, admin functionality, and more.

---

## 🚀 Features

- Real-time price lookup for cryptocurrencies  
- Buy and sell operations (mock/payment-integration as per `config.py`)  
- Deposit and withdrawal support  
- Admin panel (role-based access)  
- In-bot listing of currencies with detailed search  
- Favorites list per user

---

## 📂 Project Structure

```
exchange_currency/
├── DDL.py           # Database schema definitions
├── DML.py           # Insert/update queries (e.g., users, orders)
├── DQL.py           # Read queries (price fetch, analytics)
├── config.py        # Configuration (DB, Telegram token, bank info)
├── main.py          # Main bot logic and command handlers
├── persian_text.py  # Persian-language messages and responses
├── requirements.txt
└── LICENSE          # MIT License
```

---

## 🛠️ Prerequisites

- Python 3.9 or later  
- MySql 
- A Telegram Bot token via [@BotFather](https://t.me/BotFather)  
- (Optional) Bank account/card details loaded via environment variables or `config.py`

---

## ⚙️ Setup & Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/amirmahdi-jaberi/exchange_currency.git
   cd exchange_currency
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate      # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install --no-cache-dir -r requirements.txt
   ```

4. Create a `.env` file (recommended) or edit `config.py`:
   ```env
   TELEGRAM_TOKEN=your_bot_token_here
   DATABASE_URL=postgresql://user:pass@host/dbname
   BANK_CARD_NUMBER=xxxx-xxxx-xxxx-xxxx
   BANK_CARD_PHOTO=/path/to/card-image.png
   ```

   > ⚠️ **Never commit sensitive data (e.g. tokens, photos, DB credentials).**  
   > Use `.gitignore` to exclude `.env` and any image files.

5. Initialize database schema:
   ```bash
   python DDL.py
   ```

6. Optionally, seed the database:
   ```bash
   python DML.py
   ```

7. Start the bot:
   ```bash
   python main.py
   ```

---
## ✅ Contributing

Contributions are welcome! Please:

1. Fork the repository  
2. Create a feature branch: `git checkout -b feature/awesome-feature`  
3. Commit your changes: `git commit -am "Add awesome feature"`  
4. Push to branch: `git push origin feature/awesome-feature`  
5. Open a Pull Request

Please follow PEP 8 and include docstrings or comments in English for any new modules or functions.

---

## 📄 License

This project is licensed under the **MIT License**. See the `LICENSE` file for full details.

---


## Created by
amir mahdi jaberi

