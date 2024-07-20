import json
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext

# Load data from JSON
def load_data():
    try:
        with open('data.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Save data to JSON
def save_data(data):
    with open('data.json', 'w') as file:
        json.dump(data, file, indent=4)

data = load_data()

# Generate a random reception code
def generate_reception_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

def get_user_data(user_id):
    if str(user_id) not in data:
        data[str(user_id)] = {
            "workers": 1,
            "balance": 0.0,
            "address": "",
            "hashrate": 1,
            "wallet": "",
            "boosters": {
                "GRINCUCKATOO32": {"hashrate": 25, "price": 250},
                "NEXAPOW": {"hashrate": 17, "price": 100},
                "FISHHASH": {"hashrate": 12, "price": 50},
                "ETCHASH": {"hashrate": 6, "price": 25},
                "CRYPTONIGHTR": {"hashrate": 3, "price": 10}
            }
        }
        save_data(data)
    return data[str(user_id)]

async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Start Mining🚀", callback_data='start_mining')],
        [InlineKeyboardButton("Owner Pixelmoon", url='https://t.me/yogakokxd')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🚀 Pixelmoon Mining USDT\n\nGet Free USDT Ton/Tron Just By Keeping The Server Active 24/7\nTask : Keeping Servers Active 24/7\nHashrate : 1 GH/s⚡\nNote : Do not use 3rd party applications or suspend accounts!\n\nClick below to continue",
        reply_markup=reply_markup
    )

async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_data = get_user_data(user_id)
    
    if query.data == 'start_mining':
        keyboard = [
            [InlineKeyboardButton("Ton🚀", callback_data='choose_ton')],
            [InlineKeyboardButton("Tron✨", callback_data='choose_tron')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="Good Jobs!, Now choose the wallet you want to mine! (Don't choose wrongly, only choose once.)",
            reply_markup=reply_markup
        )

    elif query.data == 'choose_ton':
        user_data['wallet'] = 'Ton'
        save_data(data)
        await query.edit_message_text(
            text="Now that your mining is running, please type in your USDT TON address:"
        )
        context.user_data['awaiting_address'] = True

    elif query.data == 'choose_tron':
        user_data['wallet'] = 'Tron'
        save_data(data)
        await query.edit_message_text(
            text="Now that your mining is running, please type in your USDT TRC20 address:"
        )
        context.user_data['awaiting_address'] = True

    elif query.data == 'check_balance' or query.data == 'back_to_info':
        await show_info(update, context)

    elif query.data.startswith('boost_'):
        boost_name = query.data.split('_')[1]
        boost = user_data['boosters'][boost_name]
        context.user_data['selected_boost'] = boost_name
        keyboard = [
            [InlineKeyboardButton("Yeps Buy This!", callback_data='buy_boost')],
            [InlineKeyboardButton("No, Back To Boost", callback_data='back_to_boost')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=f"🔮 Do You Want to Buy This GPU Miner?\n\nName: {boost_name}\nHashrate: +{boost['hashrate']} GH/s\nPrice: ${boost['price']}",
            reply_markup=reply_markup
        )

    elif query.data == 'buy_boost':
        boost_name = context.user_data['selected_boost']
        boost = user_data['boosters'][boost_name]
        user_data['hashrate'] += boost['hashrate']
        user_data['workers'] += 1
        save_data(data)
        await query.edit_message_text(
            text=f"✅Done, you have purchased the GPU device and your workers\n\nDevice Name: {boost_name}\nHashrate: {boost['hashrate']} GH/s\nPrice: ${boost['price']}\n\nThank you for purchasing, good luck miners!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back Mining", callback_data='back_to_info')]])
        )

    elif query.data == 'back_to_boost':
        await show_boost(update, context)

    elif query.data == 'withdraw':
        await withdraw(update, context)

    elif query.data == 'confirm_withdraw':
        await confirm_withdraw(update, context)

async def receive_address(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_data = get_user_data(user_id)
    if context.user_data.get('awaiting_address'):
        user_data['address'] = update.message.text
        save_data(data)
        context.user_data['awaiting_address'] = False
        await update.message.reply_text(
            "Very good, now your mining is running. Type /info to see your statistics\n\nIf your server dies then mining won't work, so please always maintain it.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Check Balance", callback_data='check_balance')]])
        )

async def show_info(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id
    user_data = get_user_data(user_id)
    await (update.message.reply_text if update.message else update.callback_query.edit_message_text)(
        f"Hi Miners. Here are statistics about your mining\n\n🔮 Workers: {user_data['workers']} Miner Device\n🧧 USDT Balance: {user_data['balance']}\n🔑 Your address: {user_data['address']}\n🚀 Hashrate : {user_data['hashrate']} GH/s⚡\n📦 Your wallet: {user_data['wallet']}\n\nIf you want to speed up your earning of USDT, you can upgrade/hire workers to speed up mining!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Withdraw USDT Now✨", callback_data='withdraw')],
            [InlineKeyboardButton("Upgrade Miner🔥", callback_data='show_boost')]
        ])
    )

async def show_boost(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("GRINCUCKATOO32 +25 GH/s $250", callback_data='boost_GRINCUCKATOO32')],
        [InlineKeyboardButton("NEXAPOW +17 GH/s $100", callback_data='boost_NEXAPOW')],
        [InlineKeyboardButton("FISHHASH +12 GH/s $50", callback_data='boost_FISHHASH')],
        [InlineKeyboardButton("ETCHASH +6 GH/s $25", callback_data='boost_ETCHASH')],
        [InlineKeyboardButton("CRYPTONIGHTR +3 GH/s $10", callback_data='boost_CRYPTONIGHTR')],
        [InlineKeyboardButton("Back To Info", callback_data='back_to_info')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await (update.message.reply_text if update.message else update.callback_query.edit_message_text)(
        "Welcome to Booster Mining🚀\nPlease Choose Your Booster:",
        reply_markup=reply_markup
    )

async def withdraw(update: Update, context: CallbackContext) -> None:
    user_id = update.callback_query.from_user.id
    user_data = get_user_data(user_id)
    min_withdraw = 1 if user_data['wallet'] == 'Ton' else 3
    gas_fee = 0 if user_data['wallet'] == 'Ton' else 2
    total_amount = user_data['balance'] - gas_fee

    if user_data['balance'] < min_withdraw + gas_fee:
        await update.callback_query.edit_message_text(
            text="❌ Oops!, you cannot withdraw for the reason: Insufficient balance"
        )
        return

    keyboard = [
        [InlineKeyboardButton("Yups", callback_data='confirm_withdraw')],
        [InlineKeyboardButton("Back To Info", callback_data='back_to_info')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        text=f"⚠️ Are you sure you want to withdraw now with a USDT amount of: {total_amount}\n\nMinimum Withdraw Ton is: 1 USDT\nMinimum Tron withdrawal is: 3 USDT with a gas fee of 2 USDT",
        reply_markup=reply_markup
    )

async def confirm_withdraw(update: Update, context: CallbackContext) -> None:
    user_id = update.callback_query.from_user.id
    user_data = get_user_data(user_id)
    min_withdraw = 1 if user_data['wallet'] == 'Ton' else 3
    gas_fee = 0 if user_data['wallet'] == 'Ton' else 2
    total_amount = user_data['balance'] - gas_fee

    if user_data['balance'] < min_withdraw + gas_fee:
        await update.callback_query.edit_message_text(
            text="❌ Oops!, you cannot withdraw for the reason: Insufficient balance"
        )
        return

    reception_code = generate_reception_code()
    user_data['balance'] = 0
    save_data(data)

    await update.callback_query.edit_message_text(
        text=f"✅ Successful Withdrawal Please Wait 1x24 Hours To Receive Your USDT, Please Contact Admin If An Error Occurs\n\nReception Code: {reception_code}"
    )

def main() -> None:
    application = Application.builder().token("7494312090:AAEv4bscFgoVwHUVJC4euDltzqFbPvBOGxw").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_address))
    application.add_handler(CommandHandler("info", show_info))
    application.add_handler(CommandHandler("boost", show_boost))

    application.run_polling()

if __name__ == '__main__':
    main()
