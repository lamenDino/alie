# Telegram AliExpress Affiliate Bot

Bot Telegram per generare link affiliati AliExpress con anteprima prodotto.

## Setup

1. Crea file `.env`:
   ```
   TELEGRAM_BOT_TOKEN=il_tuo_token_bot
   ADMIN_USER_ID=il_tuo_id_telegram
   AFFILIATE_ID=il_tuo_affiliate_id  # es. 46327ec42fb54c13877458a54e994be4-1759353537020-06756-_EHcD5Rs
   PORT=8080
   ```

2. Installa dipendenze:
   ```bash
   pip install -r requirements.txt
   ```

## Deploy su Render

- Tipo di servizio: Web Service
- Espone porta definita da `PORT`
- Start command:
  ```
  python bot_affiliate.py
  ```
