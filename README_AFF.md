# Telegram AliExpress Affiliate Bot

Bot Telegram per generare link affiliati AliExpress automatizzati.

## Setup

1. Crea un file `.env` con:
   ```
   TELEGRAM_BOT_TOKEN=il_tuo_token_bot
   ADMIN_USER_ID=il_tuo_id_telegram
   AFFILIATE_ID=il_tuo_affiliate_id  # es. 46327ec42fb54c13877458a54e994be4-1759353537020-06756-_EHcD5Rs
   ```

2. Installa dipendenze:
   ```bash
   pip install -r requirements.txt
   ```

## Deploy su Render

- Tipo di servizio: Background Worker (solo polling)
- Start command:
  ```
  python bot_affiliate.py
  ```

## Utilizzo

Invia un link AliExpress nel bot e riceverai il link affiliato corrispondente.
