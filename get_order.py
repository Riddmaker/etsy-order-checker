import os
import subprocess
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

# Load environment variables from .env file
load_dotenv()

# Read values from .env
PRINTER_IP = os.getenv("PRINTER_IP")
PRINTER_MODEL = os.getenv("PRINTER_MODEL", "QL-820NWB")
LABEL_SIZE = os.getenv("LABEL_SIZE", "29x90")  # Default to 29x90

# Set label image path inside "labels/" directory (Assuming it exists)
LABEL_IMAGE_PATH = os.path.join(os.getcwd(), "labels", "label.png")  # Overwrite existing file

def create_address_label():
    """Creates an image of the address label for a 29mm x 90mm label."""
    address_text = "Samuel Kamas\nTocil 51F\n51F\nCoventry, West Midlands CV4 7ES\nUnited Kingdom"
    
    # Correct pixel dimensions for 29x90 labels (991px x 306px), taken from here: https://github.com/pklaus/brother_ql
    width, height = 991, 306
    image = Image.new("1", (width, height), 255)  # B/W image
    
    draw = ImageDraw.Draw(image)
    
    # Try loading a system font, fallback if necessary
    try:
        font = ImageFont.truetype("arial.ttf", 80)  # Adjust font size
    except IOError:
        font = ImageFont.load_default()
    
    # Position text to be centered on the label
    text_x = 20  # Small left margin
    text_y = 50  # Adjust to position text vertically centered

    draw.text((text_x, text_y), address_text, font=font, fill=0)
    
    # Overwrite existing file
    image.save(LABEL_IMAGE_PATH)
    print(f"Label image saved at: {LABEL_IMAGE_PATH}")

def print_label():
    """Prints the label using the brother_ql command-line tool."""
    if not PRINTER_IP:
        print("Error: PRINTER_IP is not set. Please check your .env file.")
        return

    command = [
        "brother_ql",
        "--backend", "network",
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

if __name__ == "__main__":
    create_address_label()
    print_label()