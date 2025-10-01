#!/usr/bin/env python3
"""
Bot Telegram per generare link affiliati AliExpress con PID predefinito
Autore: Il tuo nome
Descrizione: Trasforma URL AliExpress in link affiliati usando aff_trace_key
"""

import os
import logging
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Carica variabili ambiente
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', '0'))
AFFILIATE_ID = os.getenv('AFFILIATE_ID')  # es. 46327ec42fb54c13877458a54e994be4-1759353537020-06756-_EHcD5Rs

# Configura logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def make_affiliate_link(url: str) -> str:
    parsed = urlparse(url)
    # Costruisci query con aff_platform e aff_trace_key
    qs = parse_qs(parsed.query)
    qs.clear()
    qs['aff_platform'] = ['link-c']
    qs['aff_trace_key'] = [AFFILIATE_ID]
    new_query = urlencode(qs, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Inviami un link AliExpress e ti rispondo con il tuo link affiliato!"
    )


async def affiliate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if 'aliexpress.com' not in text.lower():
        await update.message.reply_text(
            "❌ Non vedo un link AliExpress valido. Riprova."
        )
        return
    # Genera link affiliato
    aff_link = make_affiliate_link(text)
    await update.message.reply_text(
        f"🔗 Ecco il tuo link affiliato:
{aff_link}",
        parse_mode=ParseMode.MARKDOWN
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Errore: {context.error}")


def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, affiliate_handler))
    app.add_error_handler(error_handler)
    logger.info("Bot AliExpress Affiliate avviato...")
    app.run_polling()


if __name__ == "__main__":
    main()
