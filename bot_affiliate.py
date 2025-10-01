#!/usr/bin/env python3
"""
Bot Telegram per generare link affiliati AliExpress con PID predefinito
Elimina il link inviato, mostra chi l'ha mandato, invia il link affiliato, immagine e descrizione prodotto
"""
import os
import logging
import asyncio
import requests
from bs4 import BeautifulSoup
from aiohttp import web
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from telegram import Update, InputMediaPhoto
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Carica variabili ambiente
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', '0'))
AFFILIATE_ID = os.getenv('AFFILIATE_ID')
PORT = int(os.getenv('PORT', '8080'))

# Configura logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def make_affiliate_link(url: str) -> str:
    parsed = urlparse(url)
    qs = {}
    qs['aff_platform'] = 'link-c'
    qs['aff_trace_key'] = AFFILIATE_ID
    new_query = urlencode(qs)
    return urlunparse(parsed._replace(query=new_query))


def fetch_product_info(url: str):
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, 'lxml')
        title = soup.find('meta', property='og:title')
        desc = soup.find('meta', property='og:description')
        img = soup.find('meta', property='og:image')
        return {
            'title': title['content'] if title else '',
            'description': desc['content'] if desc else '',
            'image': img['content'] if img else None
        }
    except Exception as e:
        logger.error(f"Errore fetch info: {e}")
        return {'title':'','description':'','image':None}

async def handle(request):
    return web.Response(text="OK")

async def start_webserver():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    logger.info(f"Web server started on port {PORT}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Inviami un link AliExpress e ti rispondo con il tuo link affiliato!")

async def affiliate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user = message.from_user
    text = message.text.strip()
    if 'aliexpress.com' not in text.lower():
        await message.reply_text("❌ Non vedo un link AliExpress valido. Riprova.")
        return
    # elimina messaggio originale
    try:
        await message.delete()
    except:
        pass
    # genera link affiliato
    aff_link = make_affiliate_link(text)
    # fetch info
    info = fetch_product_info(text)
    caption = f"🔗 Link affiliato generato da: *{user.full_name}*\n\n"
    caption += f"{info['title']}\n\n"
    caption += f"{info['description']}\n\n"
    caption += f"[Compra ora]({aff_link})"
    # invia immagine e descrizione
    if info['image']:
        await context.bot.send_photo(
            chat_id=message.chat_id,
            photo=info['image'],
            caption=caption,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await context.bot.send_message(
            chat_id=message.chat_id,
            text=caption,
            parse_mode=ParseMode.MARKDOWN
        )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Errore: {context.error}")

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, affiliate_handler))
    app.add_error_handler(error_handler)
    loop = asyncio.get_event_loop()
    loop.create_task(start_webserver())
    logger.info("Bot AliExpress Affiliate avviato...")
    app.run_polling()

if __name__ == "__main__":
    main()
