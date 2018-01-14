from os import listdir, path, makedirs, remove
from os.path import isfile, join
import sys
import glob
import threading
import asyncio
import time
import aiofiles
import img2pdf
from PIL import Image, ImageChops


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


def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)


def crop_images(image):
    im = Image.open(image)
    im = trim(im)
    return im


def remove_bottom_border(pil_image):
    width = pil_image.size[0]
    height = pil_image.size[1]
    return pil_image.crop((0, 0, width, height - 50))


def convert_single_image(image):
    im = Image.open(image).convert('RGB')
    if '_01_' not in image:
        im = trim(remove_bottom_border(im))

    im.save(image.replace('webp', 'jpg'), 'jpeg')


async def convert_single_image(image):
    im = Image.open(image).convert('RGB')
    if '_01_' not in image:
        await asyncio.sleep(0)
        im = trim(remove_bottom_border(im))
    
    await asyncio.sleep(0)
    im.save(image.replace('webp', 'jpg'), 'jpeg')


async def convert_image_list(image_list):
    for image in image_list:
        if 'webp' in image:
            await asyncio.gather(
                convert_single_image(image)
            )


def convert_to_pdf(image_list, output_name):
    pdf_bytes = img2pdf.convert(image_list)
    with open(output_name, 'wb') as f:
        f.write(pdf_bytes)
        f.flush()


def run_async(task):
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(task)
    finally:
        loop.close()


def show_list_formated(list):
    for l in list:
        print(l)


def main():
    folder = sys.argv[1]
    output_name = sys.argv[2]

    print('Folder name {}'.format(folder))
    
    print('====Finding files on directory====')
    image_list = find_images_path(folder, '.webp')
    
    print('====Files found====') 
    show_list_formated(image_list)

    print('====Converting and cropping images====')
    run_async(convert_image_list(image_list))
    converted_images = find_images_path(folder, '.jpg')
    show_list_formated(converted_images)

    print('====Converting to PDF====')
    jpg_list = find_images_path(folder, '.jpg')
    output_file = '{}/{}'.format(folder, output_name)
    convert_to_pdf(jpg_list, output_file)

    print('====Removing JPG files====')
    remove_jpg_images(folder, 'jpg')


if __name__ == '__main__':
    start = time.time()
    main()    
    end = time.time()
    print("Total time: {}".format(end - start))
