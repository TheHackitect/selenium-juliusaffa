import requests

# Replace with your CoinMarketCap API key
CMC_API_KEY = 'cd42bddd-cbae-4ac0-9200-23a807ac2d18'

def get_ape_price_in_usd():
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

def convert_to_usd(transaction_value_wei, ape_price_usd):
    # Convert Wei to Ether (1 Ether = 10^18 Wei)
    transaction_value_ether = int(transaction_value_wei) / 10**18
    
    # Calculate the value in USD
    return transaction_value_ether * ape_price_usd

# The transacted amount in Wei (as per your transaction data)
transaction_value_wei = "33875936"

try:
    ape_price_usd = get_ape_price_in_usd()
    print(ape_price_usd)
    transaction_value_usd = convert_to_usd(transaction_value_wei, ape_price_usd)
    print(f"The value of the transacted amount in USD is: ${transaction_value_usd:.9f}")
except Exception as e:
    print(f"Error: {e}")


# import requests

# # Replace with your CoinMarketCap API key
# CMC_API_KEY = 'your_api_key_here'
# # Contract address for the specific ApeCoin
# CONTRACT_ADDRESS = '0xe042DC9d91B5ce6E63579ae1287E993cDf41F8cE'

# def get_ape_price_in_usd():
#     url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
#     parameters = {
#         'address': CONTRACT_ADDRESS,
#         'convert': 'USD'
#     }
#     headers = {
#         'X-CMC_PRO_API_KEY': CMC_API_KEY
#     }
    
#     response = requests.get(url, headers=headers, params=parameters)
#     data = response.json()
    
#     # Check if the response contains the required data
#     if data and 'data' in data and CONTRACT_ADDRESS.lower() in data['data']:
#         return data['data'][CONTRACT_ADDRESS.lower()]['quote']['USD']['price']
#     else:
#         raise Exception('Could not retrieve APE price')

# def convert_to_usd(transaction_value_wei, ape_price_usd):
#     # Convert Wei to Ether (1 Ether = 10^18 Wei)
#     transaction_value_ether = int(transaction_value_wei) / 10**18
    
#     # Calculate the value in USD
#     return transaction_value_ether * ape_price_usd

# # The transacted amount in Wei (as per your transaction data)
# transaction_value_wei = "33875936000000000"

# try:
#     ape_price_usd = get_ape_price_in_usd()
#     transaction_value_usd = convert_to_usd(transaction_value_wei, ape_price_usd)
#     print(f"The value of the transacted amount in USD is: ${transaction_value_usd:.2f}")
# except Exception as e:
#     print(f"Error: {e}")
