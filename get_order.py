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
    """Creates a left-aligned address label for 29x90mm labels."""
    address_text = "Alexander Moyer\n1528 thompson lane\nMECHANICSBURG, PA 17055\nUnited States"
    
    # Label dimensions (991x306 pixels)
    width, height = 991, 306
    image = Image.new("1", (width, height), 255)
    draw = ImageDraw.Draw(image)

    # Try common system fonts
    font_paths = [
        "DejaVuSans-Bold.ttf",
        "Arial Bold.ttf",
        "arialbd.ttf",
        "Arial.ttf",
        "FreeSans-Bold.ttf",
        "LiberationSans-Bold.ttf"
    ]
    
    font_size = 120
    font = None

    # Find first available font
    for path in font_paths:
        try:
            font = ImageFont.truetype(path, font_size)
            break
        except (IOError, OSError):
            continue

    # Fallback to default font
    if not font:
        font = ImageFont.load_default()
        print("Using default font")
    else:
        # Adjust font size to fit
        while font_size > 10:
            # Modern text size calculation
            bbox = draw.textbbox((0, 0), address_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            if text_width < width - 50 and text_height < height - 20:
                break
            font_size -= 2
            font = ImageFont.truetype(font.path, font_size)

    # Left alignment with margins
    margin_left = 20
    margin_top = 20

    # Draw text
    draw.multiline_text(
        (margin_left, margin_top),
        address_text,
        font=font,
        fill=0,
        align="left"
    )

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