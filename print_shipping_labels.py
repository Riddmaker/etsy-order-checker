import os
import subprocess
import pandas as pd
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

PRINTER_IP = os.getenv("PRINTER_IP")
PRINTER_MODEL = os.getenv("PRINTER_MODEL", "QL-820NWB")
LABEL_SIZE = os.getenv("LABEL_SIZE", "29x90")  # Default to 29x90
LABEL_IMAGE_PATH = os.path.join(os.getcwd(), "labels", "label.png")

# Read label dimensions & font size from environment, convert to int
LABEL_WIDTH = int(os.getenv("LABEL_WIDTH", "991"))
LABEL_HEIGHT = int(os.getenv("LABEL_HEIGHT", "306"))
FONT_SIZE = int(os.getenv("FONT_SIZE", "120"))

# Read needed backend
BACKEND = os.getenv("BACKEND", "network")

def create_address_label(address_text):
    """Creates a left-aligned address label for 29x90mm labels."""
    width, height = LABEL_WIDTH, LABEL_HEIGHT
    image = Image.new("1", (width, height), 255)
    draw = ImageDraw.Draw(image)

    font_paths = [
        "/usr/share/fonts/noto/NotoSansCJK-Regular.ttc",
        "DejaVuSans-Bold.ttf",
        "Arial Bold.ttf",
        "arialbd.ttf",
        "Arial.ttf",
        "FreeSans-Bold.ttf",
        "LiberationSans-Bold.ttf"
    ]
    font_size = FONT_SIZE
    font = None

    for path in font_paths:
        try:
            font = ImageFont.truetype(path, font_size)
            break
        except (IOError, OSError):
            continue

    if not font:
        font = ImageFont.load_default()
        print("Using default font")
    else:
        # Adjust font size to fit:
        while font_size > 10:
            bbox = draw.textbbox((0, 0), address_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            if text_width < width - 50 and text_height < height - 20:
                break
            font_size -= 2
            font = ImageFont.truetype(font.path, font_size)

    draw.multiline_text((20, 0), address_text, font=font, fill=0, align="left")
    image.save(LABEL_IMAGE_PATH)
    print(f"Label image saved at: {LABEL_IMAGE_PATH}")

def print_label():
    """Prints the label using the brother_ql command-line tool."""
    if not PRINTER_IP:
        print("Error: PRINTER_IP is not set. Please check your .env file.")
        return

    command = [
        "brother_ql",
        "--backend", f"{BACKEND}",
        "--model", PRINTER_MODEL,
        "--printer", f"tcp://{PRINTER_IP}:9100",
        "print",
        "-l", LABEL_SIZE,
        LABEL_IMAGE_PATH
    ]

    print(f"Executing: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("Print successful:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error printing label:", e.stderr)

def main():
    # 1. Run fetch_orders.py to generate orders/unshipped_orders.csv
    try:
        print("Running fetch_orders.py...")
        subprocess.run(["python", "fetch_orders.py"], check=True)
    except subprocess.CalledProcessError as e:
        print("Error running fetch_orders.py:", e)
        return

    # 2. Load the CSV
    csv_path = os.path.join("orders", "unshipped_orders.csv")
    if not os.path.isfile(csv_path):
        print(f"Could not find CSV at {csv_path}")
        return

    df = pd.read_csv(csv_path)

    # 3. Keep only rows with status = 'Paid'
    df = df[df['status'] == 'Paid']

    # 4. Flatten to one row per order_id by dropping duplicates
    df = df.drop_duplicates(subset='order_id')

    # 5. Keep columns: order_id, status, shipping_address
    #    (assuming 'shipping_address' is the name in your CSV)
    df = df[['order_id', 'status', 'shipping_address']]

    # 6. Loop over each row, printing the label
    if df.empty:
        print("No orders found with status = 'Paid'.")
        return

    for _, row in df.iterrows():
        address_text = row['shipping_address']
        
        # Ensure newlines are recognized—if your shipping_address already 
        # contains "\n", it's good to go.
        
        create_address_label(address_text)
        print_label()

if __name__ == "__main__":
    main()
