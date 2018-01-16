import sys
from os import listdir, path, makedirs, remove
from os.path import isfile, join
from PIL import Image, ImageChops
import img2pdf


def remove_jpg_images(target_dir, extension):
    filelist = [ f for f in listdir(target_dir) if f.endswith(".{}".format(extension)) ]
    for f in filelist:
        remove(join(target_dir, f))


def create_new_files_dir(destiny, folder_name):
    full_path = '{}/{}'.format(destiny, folder_name)
    if not path.exists(full_path):
        makedirs(full_path)


def find_images_path(target_dir, extension):
    file_paths = []
    for file_path in listdir(target_dir):
        if isfile(join(target_dir, file_path)) and file_path.endswith(extension):
            file_paths.append('{}/{}'.format(target_dir, file_path))
            
    return file_paths


def trim(pil_image):
    bg = Image.new(pil_image.mode, pil_image.size, pil_image.getpixel((0,0)))
    diff = ImageChops.difference(pil_image, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return pil_image.crop(bbox)


def crop_images(image):
    pil_image = Image.open(image)
    pil_image = trim(pil_image)
    return pil_image


def remove_bottom_border(pil_image):
    width = pil_image.size[0]
    height = pil_image.size[1]
    return pil_image.crop((0, 0, width, height - 50))


def convert_images(image_list):
    for image in image_list:
        if 'webp' in image:
            pil_image = Image.open(image).convert('RGB')
            if '_01_' not in image:
                pil_image = trim(remove_bottom_border(pil_image))

            pil_image.save(image.replace('webp', 'jpg'), 'jpeg')


def convert_to_pdf(image_list, output_name, extension):
    pdf_bytes = img2pdf.convert(image_list)
    with open(output_name, 'wb') as file:
        file.write(pdf_bytes)


if __name__ == '__main__':
    FOLDER = sys.argv[1]
    OUTPUT_NAME = sys.argv[2]

    print('Folder name {}'.format(FOLDER))

    print('====Finding files on directory====')
    IMAGE_LIST = find_images_path(FOLDER, '.webp')

    print('====Files found====')
    print(IMAGE_LIST)

    print('====Converting and cropping images====')
    convert_images(IMAGE_LIST)
    CONVERTED_IMAGES = find_images_path(FOLDER, '.jpg')
    print(CONVERTED_IMAGES)

    print('====Converting to PDF====')
    JPG_LIST = find_images_path(FOLDER, '.jpg')
    OUTPUT_FILE = '{}/{}'.format(FOLDER, OUTPUT_NAME)
    convert_to_pdf(JPG_LIST, OUTPUT_FILE, '.jpg')

    print('====Removing JPG files====')
    remove_jpg_images(FOLDER, 'jpg')
