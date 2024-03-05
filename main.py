import os
import sys
import math
from PIL import Image


# Returns True if `img' is image
def is_image(img):
    try:
        img.verify()  # will raise if `img' is not a valid image
        return True
    except (IOError, SyntaxError):
        print("not an image")
        return False


# Calculates best grid size for a folder
def calculate_grid_size(num_images):
    factors = []
    for i in range(1, int(math.sqrt(num_images)) + 1):
        if num_images % i == 0:
            factors.append((num_images // i, i))

    min_diff = float('inf')
    best_factors = (num_images, 1)
    for factor in factors:
        diff = abs(factor[0] - factor[1])
        if diff < min_diff:
            min_diff = diff
            best_factors = factor
    return best_factors


THUMBNAIL_SIZE = 200
SPACING = 10
MARGIN = 50
extensions = ['.jpg', '.jpeg', '.png']  # image extensions


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py folder1 [folder2 ...]")
        sys.exit(1)

    folder_names = sys.argv[1:]
    output_filename = "Result.tiff"

    # dict for images and grid size for each folder
    images_per_page = {}

    # find images in each folder
    for folder in folder_names:
        images = []

        folder_path = os.path.join(os.getcwd(), folder)
        if os.path.isdir(folder_path):
            for filename in os.listdir(folder_path):
                if any(filename.endswith(ext) for ext in extensions):
                    image_path = os.path.join(folder_path, filename)
                    img = Image.open(image_path)
                    img.thumbnail((THUMBNAIL_SIZE, THUMBNAIL_SIZE))
                    images.append(img)
        else:
            print(f"{folder} is not a directory. Skipping...")
            continue

        num_images = len(images)
        if num_images == 0:
            print(f"No images found in {folder}. Skipping...")
            continue

        grid_size = calculate_grid_size(num_images)

        images_per_page[folder] = {
            'images': images,
            'grid_size': grid_size
        }

    if not images_per_page:
        print("No images found in any folder. Exiting...")
        sys.exit(0)

    # calculate total width and height of the page
    max_grid_width = max([grid_size[0] for grid_size in [v['grid_size'] for v in images_per_page.values()]])
    max_grid_height = max([grid_size[1] for grid_size in [v['grid_size'] for v in images_per_page.values()]])
    page_width_px = (max_grid_width * THUMBNAIL_SIZE) + ((max_grid_width - 1) * SPACING) + (2 * MARGIN)
    page_height_px = (max_grid_height * THUMBNAIL_SIZE) + ((max_grid_height - 1) * SPACING) + (2 * MARGIN)

    # create a blank white page
    pages = []
    page = Image.new('RGB', (page_width_px, page_height_px), color='white')

    # paste images in a grid into pages
    for folder, data in images_per_page.items():
        images = data['images']
        grid_size = data['grid_size']

        grid_width_px = (grid_size[0] * THUMBNAIL_SIZE) + ((grid_size[0] - 1) * SPACING)
        grid_height_px = (grid_size[1] * THUMBNAIL_SIZE) + ((grid_size[1] - 1) * SPACING)

        for i, img in enumerate(images):
            x = MARGIN + (i // grid_size[1]) * (THUMBNAIL_SIZE + SPACING)
            y = MARGIN + (i % grid_size[1]) * (THUMBNAIL_SIZE + SPACING)
            page.paste(img, (x, y))

        pages.append(page)

        # clear page for next iteration
        page = Image.new('RGB', (page_width_px, page_height_px), color='white')

    # save resulting TIFF file
    pages[0].save(output_filename, save_all=True, append_images=pages[1:])
