# Still in Beta!
This project is still in Beta!
Currently only manually printing the label works by running the appropriate python file.
Auth and fetcher are still in work.

# etsy-order-checker
Gets current etsy orders and prints shipping label on brother label printer.

## Install manual
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
9. Run the script