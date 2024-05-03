import os
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()


def convert_heic_to_jpg(input_folder, output_folder):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Iterate over all files in the input folder
    for filename in os.listdir(input_folder):
        if filename.lower().endswith('.heic'):
            try:
                # Open the HEIC file
                input_path = os.path.join(input_folder, filename)
                img = Image.open(input_path)

                # Save as JPG
                output_path = os.path.join(output_folder, os.path.splitext(filename)[0] + '.jpg')
                img.convert('RGB').save(output_path, 'JPEG')

                print(f'Converted: {filename}')
            except Exception as e:
                print(f'Error converting {filename}: {e}')

if __name__ == "__main__":
    input_folder = input("Enter the input folder path: ")
    output_folder = input("Enter the output folder path: ")

    convert_heic_to_jpg(input_folder, output_folder)