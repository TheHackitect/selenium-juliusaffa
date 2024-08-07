import time
import sqlite3
import requests
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from art import *
from termcolor import colored
import random

# Telegram Bot Token and Channel ID
TOKEN = "5982304690:AAEHikZumTlJUpZx4Ivmro-CFpDNVILnwj8"
CHAT_ID = -4046830011
TOTAL_TOKENS = 200000000000

# Define inline keyboard buttons
keyboard = [[
    InlineKeyboardButton("🦧 Stake $APE 🦧", url="https://www.stakeapetoken.org/"),
]]
reply_markup = InlineKeyboardMarkup(keyboard)

image_path = "ape2.png"

# Initialize SQLite database
conn = sqlite3.connect('transactions.db')
c = conn.cursor()

# Create table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS transactions
             (txn_hash TEXT PRIMARY KEY, stake_amount TEXT, dollar_value TEXT)''')

API_URL = "https://explorer.bit-rock.io/api/v2/addresses/0xe042DC9d91B5ce6E63579ae1287E993cDf41F8cE/transactions?filter=to%20%7C%20from"

# Function to generate a customized ASCII logo
def generate_logo():
    logo_text = '''$APE'''
    colorful_logo = text2art(logo_text, font='block', chr_ignore=True)
    colorful_logo = colorful_logo.replace('A', colored('A', 'green'))
    colorful_logo = colorful_logo.replace('D', colored('D', 'yellow'))
    colorful_logo = colorful_logo.replace('U', colored('U', 'cyan'))
    colorful_logo = colorful_logo.replace('#', colored('█', 'blue'))
    return colorful_logo

def truncate_transaction_hash(txn_hash, prefix_length=7, suffix_length=7):
    if len(txn_hash) <= prefix_length + suffix_length:
        return txn_hash
    prefix = txn_hash[:prefix_length]
    suffix = txn_hash[-suffix_length:]
    return f"{prefix}...{suffix}"

async def fetch_transactions():
    try:
        response = requests.get(API_URL, verify=False)  # Bypass SSL verification
        response.raise_for_status()
        transactions = response.json().get('items', [])
        return transactions
    except requests.exceptions.RequestException as e:
        print(f"Error fetching transactions: {e}")
        return []
    

async def fetch_address_token_data():
    try:
        response = requests.get("https://explorer.bit-rock.io/api/v2/addresses/0xe042DC9d91B5ce6E63579ae1287E993cDf41F8cE/token-balances", verify=False)  # Bypass SSL verification
        response.raise_for_status()
        token_data = response.json()[0][1]
        return token_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching transactions: {e}")
        return []

async def process_transactions(transactions):
    for transaction in transactions:
        if transaction.get('method') == "stake":
            from_tx_hash = transaction['from']['hash']
            staked_amount_value = transaction['decoded_input']['parameters'][0]['value']
            timestamp = transaction.get('timestamp')
            status = transaction.get('status')
            
            # Check if the transaction ID exists in the database
            c.execute("SELECT * FROM transactions WHERE txn_hash=?", (from_tx_hash,))
            if c.fetchone() is None:
                # Convert and format values for message
                total_staked_value = "{:.3f}".format(float(staked_amount_value.replace(",", "")))
                percentage_staked = float(total_staked_value)/(TOTAL_TOKENS)*100
                percentage_formatted = "{:.0f}".format(percentage_staked)

                txn_hash_link = f"https://explorer.bit-rock.io/tx/{from_tx_hash}"
                truncated_address_text = truncate_transaction_hash(from_tx_hash)
                address_link = f"https://explorer.bit-rock.io/address/{from_tx_hash}"

                message = (f"<b>New $APE STAKE!</b>\n\n<b>🦧 {staked_amount_value} $APE staked ~ {status} </b>\n\n"
                        f"🪪 <a href='{address_link}'>{truncated_address_text}</a> | <a href='{txn_hash_link}'>TXS</a>\n\n"
                        f"<b>Total $APE staked : {total_staked_value} ({percentage_formatted}%)</b>\n\n"
                        f"<a href='https://www.dextools.io/app/en/bitrock/pair-explorer/0x95864a19274a5dfe8cae3a5dbef6dbeb795febde?t=1711652012988/'>Chart</a> | "
                        f"<a href='https://apetoken.net/'>Website</a> | <a href='http://t.me/ApeOnBitrock'>Telegram</a>")

                # Send message with image and inline keyboard
                bot = Bot(token=TOKEN)
                await bot.send_photo(chat_id=CHAT_ID, photo=open(image_path, 'rb'), caption=message, parse_mode="HTML", reply_markup=reply_markup)

                # Add the transaction ID to the SQLite database
                c.execute("INSERT INTO transactions (txn_hash, stake_amount, dollar_value) VALUES (?, ?, ?)", 
                        (from_tx_hash, staked_amount_value, status))
                conn.commit()
            else:
                break
            break

async def main():
    while True:
        transactions = await fetch_transactions()
        await process_transactions(transactions)
        wait_time = random.randint(8, 15)
        await asyncio.sleep(wait_time)

if __name__ == "__main__":
    print(generate_logo())
    asyncio.run(main())

# Close database connection
conn.close()
