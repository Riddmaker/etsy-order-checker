# In release!
This project has been tested on my local computer and works for me.
As of writing this, I haven't received feedback if it works for others fresh from clone.

# etsy-order-checker
Gets current etsy orders and prints shipping label on brother label printer.

## 0. Prerequisits

See the full etsy API documentation here: https://developers.etsy.com/documentation/ This is useful to understand the auth flow and to understand the env variables: CLIENT_ID, CLIENT_SECRET, SHOP_ID, ACCESS_TOKEN, REFRESH_TOKEN, and SCOPES.

See the full brother-ql library here: https://github.com/pklaus/brother_ql This is useful to understand how your label is going to be printed and to understand the env variables: PRINTER_IP, PRINTER_MODEL, and LABEL_SIZE

1. Go to etsy for developers and register your app. (Search the web on how to do that, you will land on the right page in no time).
2. In the registering form, mention that you only want to use the app for yourself and that the access will be used sparsely.
3. If your app takes a long time to register, contact the etsy developrt support. (Search the web on that aswell).
4. When your app is registered you will receive CLIENT_KEY / CLIENT_ID and CLIENT_SECRET_KEY / CLIENT_SECRET which are needed further down.
5. Click on your now registered app on etsy, and set the following callback uri: https://localhost:5000/callback
6. Make sure your brother label printer is powered on, connected to the internet via the same network as from where you run this script, and has a label roll correctly inserted.

## 0.1 Postman
To receive my first ACCESS_TOKEN, REFRESH_TOKEN and SHOP_ID, I used postman. You need two requests. The first one to get ACCESS_TOKEN and REFRESH_TOKEN, the second one to get SHOP_ID. Make sure to set the additional callback URI of postman in the etsy app, as done before for your localhost callback. This all is tricky if you have no or not much coding experience in the area of working with API's. Hit me up if you have trouble with this. Maybe I can do a video on the process in the future. Theoretically all needed info for this is the registered etsy app, the etsy api documentation and the registered postman callback uri in the etsy app.

## 1. Install manual
1. Clone directory and open it in the editor of your choice.
2. Add a .env file and store the following variables in there:
    1. CLIENT_ID=client_key_from_your_etsy_app
    2. CLIENT_SECRET=client_secrect_from_your_etsy_app
    3. SHOP_ID=your_shop_id (See [Postman](##-0.1-Postman) chapter in this docu, just above.)
    4. ACCESS_TOKEN=your_access_token (See [Postman](##-0.1-Postman) chapter in this docu, just above.)
    5. REFRESH_TOKEN=your_refresh_token (See [Postman](##-0.1-Postman) chapter in this docu, just above.)
    6. SCOPES=your_scopes_according_to_etsy_docu (For this script to work it is transactions_r.)
    7. PRINTER_IP=ip_from_brother_label_printer
    8. PRINTER_MODEL=name_of_your_printer_according_to_brother_ql_docu
    9. LABEL_SIZE=label_size_in_your_printer_according_to_brother_ql_docu (It's the column with "29x90" and similar entries.)
    10. LABEL_WIDTH=pixel_label_width_in_your_printer_according_to_brother_ql_docu
    11. LABEL_HEIGHT=pixel_label_height_in_your_printer_according_to_brother_ql_docu
    12. FONT_SIZE=120 (Trial and error, there's logic that adjusts font size automatically a bit.)
    13. REDIRECT_URI=https://localhost:5000/callback (As mentioned earlier, make sure you have the same URI saved in your etsy app.)
    14. FLASK_SECRET_KEY=random_string_of_characters (Choose your own length.)
3. Open a Terminal in the project directory and run the following commands:
    1. Install the necessary venv via something like: python3 -m venv venv or python -m venv venv
    2. Source the virtual environment. On Linux/Mac it usually is: source ./venv/bin/activate On Windows it usually is: .\venv\Scripts\activate
    3. Install the necessary requirements to run the script: pip install -r requirements.txt
4. In your created .env file, make sure you adjust your label size, label pixels according to brother-ql documentation readme.
5. Adjust font size in the main print script. (Had to figure this one out iteratively).
6. Make sure you have openSSL installed on your system, cd into the cert folder of this project and run: ´openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 -subj "/CN=localhost"´

## 2. Setup check
If you have set up everything correctly, you will now have in addition to what you had initially in the folder:
1. A .env file with the following content:
    1. CLIENT_ID
    2. CLIENT_SECRET
    3. SHOP_ID
    4. ACCESS_TOKEN
    5. REFRESH_TOKEN
    6. SCOPES
    7. PRINTER_IP
    8. PRINTER_MODEL
    9. LABEL_SIZE
    10. LABEL_WIDTH
    11. LABEL_HEIGHT
    12. FONT_SIZE
    13. REDIRECT_URI
    14. FLASK_SECRET_KEY
2. cert.pem and key.pem in the cert folder.

## 3. Print label
Run print_shipping_labels.py to print all shipping labels for all orders that are unshipped and paid.