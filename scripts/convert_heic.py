import os
import argparse
from rembg import remove
from PIL import Image
import numpy as np
import cv2
from wand.image import Image as WandImage

def convert_heic_to_png(input_folder=None, output_folder=None):
    """Convert HEIC files to PNG."""
    input_folder = input_folder or os.getcwd()
    output_folder = output_folder or os.path.join(input_folder, "converted_pngs")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".heic"):
            heic_path = os.path.join(input_folder, filename)
            png_filename = os.path.splitext(filename)[0] + ".png"
            png_path = os.path.join(output_folder, png_filename)

            try:
                with WandImage(filename=heic_path) as img:
                    img.format = 'png'
                    img.save(filename=png_path)
                os.remove(heic_path)
                print(f"Converted and deleted: {filename} -> {png_filename}")
            except Exception as e:
                print(f"Failed to convert {filename}: {e}")

def preprocess_image(image_path):
    """Preprocess the image to improve background removal."""
    # Load the image and convert to grayscale
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply a binary threshold to isolate the card
    _, thresholded_image = cv2.threshold(gray_image, 240, 255, cv2.THRESH_BINARY_INV)

    # Use edge detection (Canny) to highlight edges
    edges = cv2.Canny(thresholded_image, 100, 200)

    # Return the processed image for background removal
    return edges

def remove_background(image_path):
    """Remove the background from an image using rembg."""
    with open(image_path, "rb") as f:
        input_data = f.read()
    output_data = remove(input_data)
    return output_data

def save_removed_image(image_data, output_path):
    """Save the image after background removal."""
    with open(output_path, "wb") as out:
        out.write(image_data)

def crop_to_card(image_path):
    """Crop the image to the card area."""
    image = Image.open(image_path).convert("RGBA")
    np_image = np.array(image)
    alpha = np_image[:, :, 3]

    # Find non-zero alpha values to get the bounding box for the card
    coords = cv2.findNonZero((alpha > 0).astype(np.uint8))
    x, y, w, h = cv2.boundingRect(coords)
    cropped = image.crop((x, y, x + w, y + h))
    return cropped

def process_all_images(input_folder, do_crop=False):
    """Process all images in the input folder, remove backgrounds, and optionally crop."""
    output_folder = os.path.join(input_folder, "output_cards")
    os.makedirs(output_folder, exist_ok=True)

    print("📂 Scanning for .png files in:", input_folder)
    files = os.listdir(input_folder)
    print(f"🔍 Found {len(files)} file(s):", files)

    for file in files:
        input_path = os.path.join(input_folder, file)

        if file.lower().endswith(".png") and not file.startswith("removed_") and not file.startswith("cropped_"):
            try:
                output_removed_path = os.path.join(output_folder, f"removed_{file}")
                output_cropped_path = os.path.join(output_folder, f"cropped_{file}")

                print(f"🔄 Processing: {file}")
                # Preprocess image to improve background removal
                preprocessed_image = preprocess_image(input_path)

                # Remove the background from the preprocessed image
                removed_data = remove_background(input_path)
                save_removed_image(removed_data, output_removed_path)

                if do_crop:
                    # Crop the image after background removal
                    cropped_image = crop_to_card(output_removed_path)
                    cropped_image.save(output_cropped_path)
                    print(f"✅ Saved: {output_cropped_path}")
                else:
                    print(f"✅ Saved: {output_removed_path}")
            except Exception as e:
                print(f"❌ Error processing {file}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert HEIC files to PNG, remove backgrounds, and crop images.")
    parser.add_argument("--input", type=str, default=".", help="Input folder path (default: current directory)")
    parser.add_argument("--output", type=str, help="Output folder for PNG files (optional)")
    parser.add_argument("--crop", action="store_true", help="Crop image after background removal")
    args = parser.parse_args()

    input_folder = os.path.abspath(args.input)

    # Convert HEIC to PNG before processing if input folder contains HEIC files
    convert_heic_to_png(input_folder=input_folder, output_folder=args.output)

    # Process PNG images (background removal and cropping)
    process_all_images(input_folder=input_folder, do_crop=args.crop)
