# Still in Beta!
This project is still in Beta!
Currently only manually printing the label works by running the appropriate python file.
Also the auth works when looking at the instructions below.
Connecting the auth flow to the rest of the project is still missing. No auto-flow.
Order fetcher when auth is established is still missing.

# etsy-order-checker
Gets current etsy orders and prints shipping label on brother label printer.

## 1. Install manual
1. Clone directory and open it in the editor of your choice.
2. Add a .env file and store the following variables in there:
2.1 ETSY_CLIENT_KEY=client_key_from_your_etsy_app
2.2 ETSY_CLIENT_SECRET=client_secrect_from_your_etsy_app
2.3 ETSY_SHOP_ID=your_shop_id
2.4 PRINTER_IP=ip_from_brother_label_printer
2.5 PRINTER_MODEL=name_from_your_printer_according_to_brother_ql_docu
2.6 LABEL_SIZE=label_size_in_your_printer_according_to_brother_ql_docu_(e.g._29x90)
3. Open a Terminal in the project directory and run the following commands:
4. Install the necessary venv via something like: python3 -m venv venv or python -m venv venv
5. Source the virtual environment. In bash it is: source venv/bin/activate in powershell it is: .\venv\Scripts\activate
6. Install the necessary requirements to run the script: pip install -r requirements.txt
7. Adjust your label size, label pixels according to brother-ql readme.
8. Adjust font size in the main print script.
9. Make sure you have openSSL installed on your system, cd into the cert folder and run: ´openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 -subj "/CN=localhost"´
10. Run the auth file and go to https://localhost:5000/start_auth to authenticate once.

## 2. Print label
1. Run the get_order.py to print a label