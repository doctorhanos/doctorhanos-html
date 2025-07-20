import os
import argparse
from rembg import remove
from PIL import Image
import numpy as np
import cv2

# Card area dimensions in the target image
CARD_WIDTH = 310
CARD_HEIGHT = 430
CARD_RADIUS = 20
CARD_POSITION = None  # Will be calculated from background template

# Path to the background template
TEMPLATE_PATH = os.path.abspath("assets/bg/background.png")

def remove_background_from_image(image):
    with Image.new("RGBA", image.size) as new_img:
        new_img.paste(image)
        input_data = new_img.tobytes()
    with open("temp.png", "wb") as temp_file:
        image.save(temp_file.name)
    with open(temp_file.name, "rb") as f:
        input_data = f.read()
    return remove(input_data)

def save_removed_image(image_data, output_path):
    with open(output_path, "wb") as out:
        out.write(image_data)

def crop_to_card(image_path):
    image = Image.open(image_path).convert("RGBA")
    np_image = np.array(image)
    alpha = np_image[:, :, 3]

    coords = cv2.findNonZero((alpha > 0).astype(np.uint8))
    x, y, w, h = cv2.boundingRect(coords)
    cropped = image.crop((x, y, x + w, y + h))
    return cropped

def composite_onto_template(card_image, output_path):
    template = Image.open(TEMPLATE_PATH).convert("RGBA")
    template_width, template_height = template.size
    card_x = (template_width - CARD_WIDTH) // 2
    card_y = (template_height - CARD_HEIGHT) // 2

    card_resized = card_image.resize((CARD_WIDTH, CARD_HEIGHT), Image.Resampling.LANCZOS)
    template.paste(card_resized, (card_x, card_y), card_resized)
    template.save(output_path)

def process_all_images(input_folder, do_crop=False):
    output_folder = os.path.join(input_folder, "output_cards")
    os.makedirs(output_folder, exist_ok=True)

    print("📂 Scanning for .png files in:", input_folder)
    files = os.listdir(input_folder)
    print(f"🔍 Found {len(files)} file(s):", files)

    for file in files:
        if file.lower().endswith(".png") and not file.startswith("removed_") and not file.startswith("cropped_") and not file.startswith("composited_"):
            try:
                input_path = os.path.join(input_folder, file)
                output_removed_path = os.path.join(output_folder, f"removed_{file}")
                output_composite_path = os.path.join(output_folder, f"composited_{file}")

                print(f"🔄 Processing: {file}")

                # Step 1: Remove background
                original_image = Image.open(input_path).convert("RGBA")
                removed_data = remove_background_from_image(original_image)
                save_removed_image(removed_data, output_removed_path)

                card_image = Image.open(output_removed_path).convert("RGBA")
                if do_crop:
                    card_image = crop_to_card(output_removed_path)

                composite_onto_template(card_image, output_composite_path)
                print(f"✅ Saved: {output_composite_path}")
            except Exception as e:
                print(f"❌ Error processing {file}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove background and optionally crop/place card image.")
    parser.add_argument("--input", type=str, default=".", help="Input folder path (default: current directory)")
    parser.add_argument("--crop", action="store_true", help="Crop image after background removal")
    args = parser.parse_args()

    input_folder = os.path.abspath(args.input)
    process_all_images(input_folder=input_folder, do_crop=args.crop)
