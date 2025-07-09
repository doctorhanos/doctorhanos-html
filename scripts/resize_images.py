import os
import argparse
from PIL import Image

def resize_images(base_source_folder, set_name):
    # Append the set name to the base source path
    source_folder = os.path.join(os.path.abspath(base_source_folder), set_name)

    if not os.path.isdir(source_folder):
        print(f"❌ Source folder does not exist: {source_folder}")
        return

    # Output folders relative to current working directory
    output_500 = os.path.join(os.getcwd(), set_name, "500")
    output_backup = os.path.join(os.getcwd(), set_name, "backup")

    os.makedirs(output_500, exist_ok=True)
    os.makedirs(output_backup, exist_ok=True)

    supported_exts = (".jpg", ".jpeg", ".png", ".bmp", ".gif")

    print(f"\n📦 Resizing images for set: {set_name}")
    print(f"📂 Source: {source_folder}")
    print(f"📁 Output 1: {output_500}")
    print(f"📁 Output 2: {output_backup}\n")

    images_found = False

    for filename in os.listdir(source_folder):
        if filename.lower().endswith(supported_exts):
            images_found = True
            input_path = os.path.join(source_folder, filename)
            try:
                with Image.open(input_path) as img:
                    new_width = 500
                    scale = new_width / float(img.width)
                    new_height = int(float(img.height) * scale)
                    resized = img.resize((new_width, new_height), Image.LANCZOS)

                    resized.save(os.path.join(output_500, filename))
                    resized.save(os.path.join(output_backup, filename))

                    print(f"✔ Resized: {filename}")
            except Exception as e:
                print(f"✖ Failed to process {filename}: {e}")

    if not images_found:
        print("⚠️ No supported images found.")

    print("\n✅ Done.\n")

def main():
    parser = argparse.ArgumentParser(description="Resize images to 500px width while preserving aspect ratio")
    parser.add_argument("--source", required=True, help="Base path to source image folder")
    parser.add_argument("--set", required=True, help="Set name (subfolder to append to source path and output folder name)")

    args = parser.parse_args()
    resize_images(args.source, args.set)

if __name__ == "__main__":
    main()
