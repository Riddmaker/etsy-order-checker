# fetch_etsy_orders.py
import os
import requests
from dotenv import load_dotenv
from auth import access_token

# Load environment variables
load_dotenv()

# Etsy API URLs
ORDERS_URL = "https://openapi.etsy.com/v3/application/shops/{shop_id}/receipts"

def get_orders(shop_id):
    if not access_token:
        raise Exception("You must authenticate first by running auth.py and visiting /connect")

    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(ORDERS_URL.format(shop_id=shop_id), headers=headers)

    if response.status_code == 200:
        orders = response.json()
        order_list = ''
        for order in orders:
            order_list += f"Order ID: {order['order_id']}, Buyer: {order['buyer_user_id']}, Total: {order['grandtotal']}\n"

        return order_list or 'No orders found.'
    else:
        raise Exception('Error: Could not fetch orders.')

if __name__ == '__main__':
    # Replace with your shop_id
    shop_id = 'your_shop_id'
    orders = get_orders(shop_id)
    print(orders)


# Old one pager workflow that works. New workflow above tries to split auth workflow from main work workflow.
'''
import requests
import os
from dotenv import load_dotenv
from flask import Flask, request, redirect

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Etsy API, initial credentials
CLIENT_ID = os.getenv('KEYSTRING')  # Etsy API key
CLIENT_SECRET = os.getenv('SHARED_SECRET')  # Etsy shared secret

# Etsy API URLs
REQUEST_TOKEN_URL = "https://openapi.etsy.com/v3/public/oauth/token"
AUTHORIZE_URL = "https://www.etsy.com/oauth/connect"
ACCESS_TOKEN_URL = "https://openapi.etsy.com/v3/public/oauth/token"
ORDERS_URL = "https://openapi.etsy.com/v3/application/shops/{shop_id}/receipts"

# Global variable to store the access token once obtained
access_token = None

@app.route('/')
def home():
    return 'Welcome! To connect with Etsy, visit /connect'

@app.route('/connect')
def connect():
    # Step 1: Get authorization URL
    redirect_uri = 'http://localhost:5000/callback'
    authorization_url = f"{AUTHORIZE_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={redirect_uri}&scope=transactions_r"

    # Redirect user to Etsy authorization page
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    # Get the authorization code from the request URL
    code = request.args.get('code')

    if code:
        # Step 2: Exchange the code for an access token
        global access_token
        response = requests.post(ACCESS_TOKEN_URL, data={
            'grant_type': 'authorization_code',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code,
            'redirect_uri': 'http://localhost:5000/callback'
        })

        if response.status_code == 200:
            access_token = response.json()['access_token']
            return 'Authorization successful! Now visit /get_shop_id to retrieve your shop ID.'
        else:
            return 'Error: Failed to get access token.'

    return 'Error: Authorization failed.'

@app.route('/get_shop_id')
def get_shop_id():
    if not access_token:
        return 'You must authorize first by visiting /connect.'

    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get("https://openapi.etsy.com/v3/application/users/me/shops", headers=headers)

    if response.status_code == 200:
        shop_id = response.json()[0]['shop_id']
        return f"Your shop ID is: {shop_id}"
    else:
        return 'Error: Could not fetch shop information.'

@app.route('/orders')
def get_orders():
    if not access_token:
        return 'You must authorize first by visiting /connect.'

    # Replace with your shop_id obtained from /get_shop_id
    shop_id = 'your_shop_id'

    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(ORDERS_URL.format(shop_id=shop_id), headers=headers)

    if response.status_code == 200:
        orders = response.json()
        order_list = ''
        for order in orders:
            order_list += f"Order ID: {order['order_id']}, Buyer: {order['buyer_user_id']}, Total: {order['grandtotal']}<br>"

        return order_list or 'No orders found.'
    else:
        return 'Error: Could not fetch orders.'

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True)
'''
