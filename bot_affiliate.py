#!/usr/bin/env python3
"""
Bot Telegram per generare link affiliati AliExpress con PID predefinito
Elimina il link inviato, mostra chi l'ha mandato, invia immagine + descrizione,
poi separa “Link inviato da” e “Link affiliazione” in due righe.
"""

import os
import logging
import asyncio
import requests
from bs4 import BeautifulSoup
from aiohttp import web
from urllib.parse import urlparse, urlencode, urlunparse
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', '0'))
AFFILIATE_ID = os.getenv('AFFILIATE_ID')
PORT = int(os.getenv('PORT', '8080'))

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def make_affiliate_link(url: str) -> str:
    parsed = urlparse(url)
    qs = {'aff_platform': 'link-c', 'aff_trace_key': AFFILIATE_ID}
    new_query = urlencode(qs)
    return urlunparse(parsed._replace(query=new_query))


def fetch_product_info(url: str) -> dict:
    info = {'title': '', 'description': '', 'image': None}
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, 'lxml')
        og_title = soup.find('meta', property='og:title')
        og_desc = soup.find('meta', property='og:description')
        og_img = soup.find('meta', property='og:image')
        if og_title and og_title.get('content'):
            info['title'] = og_title['content']
        if og_desc and og_desc.get('content'):
            info['description'] = og_desc['content']
        if og_img and og_img.get('content'):
            info['image'] = og_img['content']
        if not info['description'] and info['title']:
            info['description'] = (
                f"Scopri ora il fantastico “{info['title']}” su AliExpress: qualità e convenienza "
                "in un’unica soluzione, perfetto per il tuo stile e budget!"
            )
    except Exception as e:
        logger.error(f"Errore fetch info: {e}")
    return info


async def handle_health(request):
    return web.Response(text="OK")


async def start_webserver():
    app = web.Application()
    app.add_routes([web.get('/', handle_health)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    logger.info(f"Web server started on port {PORT}")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Inviami un link AliExpress e restituisco anteprima e link affiliato.")


async def affiliate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user = message.from_user
    url = message.text.strip()

    if 'aliexpress.com' not in url.lower():
        await message.reply_text("❌ Non vedo un link AliExpress valido. Riprova.")
        return

    try:
        await message.delete()
    except:
        pass

    info = fetch_product_info(url)
    aff_link = make_affiliate_link(url)

    caption_lines = []
    if info['title']:
        caption_lines.append(f"*{info['title']}*")
    if info['description']:
        caption_lines.append(info['description'])
    caption = "\n".join(caption_lines)

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

    details = (
        f"🔗 Link inviato da: *{user.full_name}*\n\n"
        f"🛒 Link affiliazione:\n{aff_link}"
    )
    await context.bot.send_message(
        chat_id=message.chat_id,
        text=details,
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
