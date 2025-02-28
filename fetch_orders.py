import os
import requests
import pandas as pd
from dotenv import load_dotenv
from auth import EtsyAuthManager

load_dotenv()

# Configuration - adjust these to match your .env variable names
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
SHOP_ID = os.getenv("SHOP_ID")  # Changed from ETSY_SHOP_ID
CLIENT_ID = os.getenv("CLIENT_ID")

def format_price(price_dict):
    """Convert Etsy price object to formatted string"""
    if not price_dict:
        return "0.00"
    amount = price_dict.get('amount', 0) / price_dict.get('divisor', 100)
    return f"{amount:.2f} {price_dict.get('currency_code', '')}"

def get_unshipped_orders():

    access_token = EtsyAuthManager.get_valid_token()

    load_dotenv()

    headers = {
        "x-api-key": CLIENT_ID,
        "Authorization": f"Bearer {access_token}"
    }

    base_url = f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/receipts"
    orders = []
    page = 1

    while True:
        params = {
            "state": "open",
            "limit": 100,
            "page": page
        }

        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        for receipt in data.get('results', []):
            # Filter for unshipped orders
            if not receipt.get('is_shipped', True):
                order_data = {
                    "order_id": receipt['receipt_id'],
                    "order_date": pd.to_datetime(receipt['created_timestamp'], unit='s'),
                    "buyer_name": receipt.get('name'),
                    "buyer_email": receipt.get('buyer_email'),
                    "status": receipt.get('status'),
                    "is_paid": receipt.get('is_paid', False),
                    "total_price": format_price(receipt.get('total_price')),
                    "subtotal": format_price(receipt.get('subtotal')),
                    "shipping_cost": format_price(receipt.get('total_shipping_cost')),
                    "tax_cost": format_price(receipt.get('total_tax_cost')),
                    "discount": format_price(receipt.get('discount_amt')),
                    "shipping_address": receipt.get('formatted_address'),
                    "city": receipt.get('city'),
                    "state": receipt.get('state'),
                    "zip": receipt.get('zip'),
                    "country": receipt.get('country_iso'),
                    "items": []
                }

                # Process transactions
                for transaction in receipt.get('transactions', []):
                    item = {
                        "item_id": transaction.get('listing_id'),
                        "title": transaction.get('title'),
                        "quantity": transaction.get('quantity', 0),
                        "price": format_price(transaction.get('price')),
                        "shipping_cost": format_price(transaction.get('shipping_cost')),
                        "processing_days": f"{transaction.get('min_processing_days', '?')}-{transaction.get('max_processing_days', '?')}"
                    }
                    order_data['items'].append(item)

                orders.append(order_data)

        # Pagination
        if data.get('pagination', {}).get('next_page'):
            page += 1
        else:
            break

    # Create flattened DataFrame
    rows = []
    for order in orders:
        base_order = {k:v for k,v in order.items() if k != 'items'}
        for item in order['items']:
            rows.append({**base_order, **item})
    
    return pd.DataFrame(rows)

if __name__ == "__main__":
    df = get_unshipped_orders()
    
    if not df.empty:
        print(f"Found {len(df)} unshipped orders")
        print(df[['order_id', 'order_date', 'buyer_name', 'title', 
                 'quantity', 'price', 'city', 'status']])
        df.to_csv('orders/unshipped_orders.csv', index=False)
        print("\nSaved to ./orders/unshipped_orders.csv")
    else:
        print("No unshipped orders found")