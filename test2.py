import requests

# Replace with your CoinMarketCap API key
CMC_API_KEY = 'cd42bddd-cbae-4ac0-9200-23a807ac2d18'

def get_brock_price_in_usd():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = {
        'symbol': 'BROCK',
        'convert': 'USD'
    }
    headers = {
        'X-CMC_PRO_API_KEY': CMC_API_KEY
    }
    
    response = requests.get(url, headers=headers, params=parameters)
    data = response.json()
    
    # Check if the response contains the required data
    if data and 'data' in data and 'BROCK' in data['data']:
        return data['data']['BROCK']['quote']['USD']['price']
    else:
        raise Exception('Could not retrieve BROCK price')

def convert_brock_to_usd(brock_amount):
    brock_price_usd = get_brock_price_in_usd()
    return brock_amount * brock_price_usd

def convert_ape_to_brock(ape_amount):
    brock_price_usd = get_brock_price_in_usd()
    ape_to_brock_rate = 1 / brock_price_usd  # 1 USD in BROCK
    brock_amount = ape_amount * ape_to_brock_rate
    return brock_amount

def calculate_ape_to_usd_rate():
    # APE to USD rate based on Bitrock website data
    ape_amount = 33875936  # 33,875,936 APE
    usd_value = 11.98  # $11.98
    ape_to_usd_rate = usd_value / ape_amount
    return ape_to_usd_rate

def convert_ape_to_usd(ape_amount):
    ape_to_usd_rate = calculate_ape_to_usd_rate()
    usd_amount = ape_amount * ape_to_usd_rate
    return usd_amount

# Example usage based on your provided transaction data
transaction_value_wei = "33875936000000000"  # transaction value in Wei

try:
    # Convert APE to BROCK
    ape_amount = int(transaction_value_wei) / 10**18  # converting Wei to APE amount
    brock_amount = convert_ape_to_brock(ape_amount)
    print(f"The value of {ape_amount:.8f} APE is approximately {brock_amount:.8f} BROCK")

    # Convert APE to USD
    ape_to_usd_amount = convert_ape_to_usd(ape_amount)
    print(f"The value of {ape_amount:.8f} APE is approximately ${ape_to_usd_amount:.9f} USD")
except Exception as e:
    print(f"Error: {e}")
