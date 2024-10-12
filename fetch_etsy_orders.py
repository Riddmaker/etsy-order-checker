import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Etsy API credentials
API_KEY = os.getenv('ETSY_API_KEY')  # Store actual key in .env file
SHOP_ID = os.getenv('ETSY_SHOP_ID')  # Store actual ID in .env file
URL = f'https://openapi.etsy.com/v2/shops/{SHOP_ID}/receipts?api_key={API_KEY}'

def fetch_orders():
    response = requests.get(URL)
    if response.status_code == 200:
        orders = response.json()['results']
        return orders
    else:
        print("Error fetching orders:", response.status_code)
        return []

def main():
    while True:
        orders = fetch_orders()
        if orders:
            df = pd.DataFrame(orders)
            print(df)  # You can also save it to a CSV file if needed
        time.sleep(7200)  # Sleep for 2 hours

if __name__ == '__main__':
    main()
