import requests
import pandas as pd
import time

# Etsy API credentials
API_KEY = 'YOUR_etsy_api_key'  # Replace with your Etsy API Key
SHOP_ID = 'YOUR_shop_id'  # Replace with your shop ID
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
