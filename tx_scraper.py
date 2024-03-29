import time
import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import undetected_chromedriver as uc
from selenium.webdriver.common.action_chains import ActionChains
import asyncio

# Telegram Bot Token and Channel ID
TOKEN = "5982304690:AAGMGPOrrXUFCCvh-1qx6b1V13ayiw_4Z4E"
CHAT_ID = 1233125771
TOTAL_TOKENS = 200000000000

# Define inline keyboard buttons
keyboard = [[
    InlineKeyboardButton("🦧 Stake $APE 🦧", url="https://www.stakeapetoken.org/"),
]]
reply_markup = InlineKeyboardMarkup(keyboard)

image_path = "ape.jpg"

# Initialize SQLite database
conn = sqlite3.connect('transactions.db')
c = conn.cursor()

# Create table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS transactions
             (txn_hash TEXT PRIMARY KEY, stake_amount TEXT, dollar_value TEXT)''')

# Initialize Chrome WebDriver
chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-gpu")
service = Service('chromedriver.exe')  # Specify the path to your ChromeDriver
driver = uc.Chrome(service=service, options=chrome_options)
# driver = webdriver.Chrome(service=service, options=chrome_options)

# Define function to scrape transactions

def truncate_transaction_hash(txn_hash, prefix_length=7, suffix_length=7):
    if len(txn_hash) <= prefix_length + suffix_length:
        return txn_hash
    prefix = txn_hash[:prefix_length]
    suffix = txn_hash[-suffix_length:]
    return f"{prefix}...{suffix}"

async def scrape_transactions():
    driver.get("https://explorer.bit-rock.io/address/0xe042DC9d91B5ce6E63579ae1287E993cDf41F8cE")

    try:
        # Wait for the transactions to load
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.css-rzw9lk")))
    except TimeoutException:
        print("Timeout while waiting for table rows to load")
        return
    time.sleep(10)
    # Find all spans with class css-rzw9lk
    spans = driver.find_elements(By.CSS_SELECTOR, "span.css-rzw9lk")

    # Find the dropdown element and click on it to expand
    button_element = driver.find_element(By.XPATH, "//button[contains(@class, 'css-b2qlj8')]")
    button_element.click()

    # Now, wait for the total staked element to become visible
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "chakra-skeleton.css-ue9nhm")))


    # Find the <div> element containing the total staked value
    total_staked_element = driver.find_element(By.CLASS_NAME, "chakra-skeleton.css-ue9nhm")
    total_staked_text = total_staked_element.text
    total_staked_raw = total_staked_text.split(" ")[0]
    value_without_commas = total_staked_raw.replace(",", "")


    # Convert to float, round to 3 decimal places, and then convert back to string
    total_staked_value = "{:.3f}".format(float(value_without_commas))
    
    percentage_staked = float(total_staked_value)/(TOTAL_TOKENS)*100
    percentage_formatted = "{:.0f}".format(percentage_staked)
    

    # Find the <p> element containing the dollar value
    dollar_value_element = driver.find_element(By.CLASS_NAME, "chakra-text.css-bjdz1t")
    total_staked_dollar_value = dollar_value_element.text


    # Iterate over the spans
    for span in spans:
        try:
            # Check if the span contains the text "stake"
            if span.text == "stake":
                # Navigate up to the parent row element
                row = span.find_element(By.XPATH, "./ancestor::tr")
                # Re-find the txn hash link within the row
                txn_hash_element = row.find_element(By.CSS_SELECTOR, "a.chakra-link.css-1yfgo13")
                txn_link = txn_hash_element.get_attribute("href")
                # Extract the transaction ID from the href attribute
                txn_hash = txn_hash_element.get_attribute("href").split("/")[-1]
                txn_hash_link = f"https://explorer.bit-rock.io/tx/{txn_hash}"

                # Check if the transaction ID exists in the database
                c.execute("SELECT * FROM transactions WHERE txn_hash=?", (txn_hash,))
                if c.fetchone() is None:
                    print(f"New stake transaction detected! --- Tx Id : {txn_hash}")
                    driver.get(f"{txn_link}")

                    # Wait for the new page to load
                    try:
                        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.css-1qvzvvz")))
                    except TimeoutException:
                        print("Timeout while waiting for the new page to load")
                        return
                    time.sleep(10)


                    address_element = driver.find_element(By.CLASS_NAME, "css-11fgcdr")
                    address_text = address_element.get_attribute("data-hash")
                    truncated_address_text = truncate_transaction_hash(address_text)
                    address_link = f"https://explorer.bit-rock.io/address/{address_text}"
                    
                    stake_elements = driver.find_elements(By.CSS_SELECTOR, ".css-1bb3n0r")  # Find all elements with class "css-1bb3n0r"

                    for element in stake_elements:
                        # Check if this element contains the text "ApeStaking"
                        if "ApeStaking" in element.text:
                            coin_name_element = element.find_element(By.CSS_SELECTOR, "div.chakra-skeleton.css-p69n58")
                            dollar_value_element = element.find_element(By.XPATH, ".//span[contains(text(), 'for')]/following-sibling::span[2]")
                            amount_staked_element = element.find_element(By.XPATH, ".//span[contains(text(), 'for')]/following-sibling::span")
                            
                            # Extract and process the data from these elements
                            coin_name = coin_name_element.text
                            dollar_value = dollar_value_element.text
                            amount_staked = amount_staked_element.text
                            
                            # Process the extracted data (e.g., send Telegram message)
                            print(f"Coin Name: {coin_name}")
                            print(f"Dollar Value: {dollar_value}")
                            print(f"Amount Staked: {amount_staked}")
                            print(f"Address link: {address_link}")
                            print(f"Address Text: {address_text}")

                            message  = f"**New $APE STAKE!\n\n🦧 {amount_staked} $APE staked ~ {dollar_value} $ \n\n🪪 [{truncated_address_text}]({address_link}) |  [TXS]({txn_hash_link})  \n\nTotal $APE staked : {total_staked_value} ({percentage_formatted}%) ~ {total_staked_dollar_value}\n\n[Chart](https://www.dextools.io/app/en/bitrock/pair-explorer/0x95864a19274a5dfe8cae3a5dbef6dbeb795febde?t=1711652012988/) | [Website](https://apetoken.net/) | [Telegram](http://t.me/ApeOnBitrock)**"
                            # Send message with image and inline keyboard
                            bot = Bot(token=TOKEN)
                            # await bot.send_photo(chat_id=CHAT_ID, photo=open(image_path, 'rb'), caption=message, parse_mode="Markdown")
                            await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown",reply_markup=reply_markup, disable_web_page_preview=True)

                            # Add the transaction ID to the SQLite database to keep track of processed transactions
                            c.execute("INSERT INTO transactions (txn_hash) VALUES (?)", (txn_hash,))
                            conn.commit()
                            print("New transaction processed and sent to Telegram:", txn_hash)

                            # Exit the loop after processing the relevant element (optional)
                            break
                        else:
                            pass
                    
                else:
                    print("Transaction already processed:", txn_hash)
                break  # Exit the loop after processing the first "stake" transaction
        except StaleElementReferenceException:
            pass
            continue  # Retry the iteration if a stale element reference exception occurs


# Main loop to continuously scrape transactions
async def main():
    while True:
        await scrape_transactions()
        await asyncio.sleep(5 * 60)  # Scrape every 5 minutes (use 5 * 60 for seconds)

if __name__ == "__main__":
    asyncio.run(main())
# Close database connection and WebDriver
conn.close()
driver.quit()
