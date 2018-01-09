import sys
from os import listdir, path, makedirs, remove
from os.path import isfile, join
from PIL import Image, ImageChops
import glob
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


def convert_images(image_list):
    for image in image_list:
        if 'webp' in image:
            im = Image.open(image).convert('RGB')
            if '_01_' not in image:
                im = trim(remove_bottom_border(im))

            im.save(image.replace('webp', 'jpg'), 'jpeg')


def convert_to_pdf(image_list, output_name, extension):
    pdf_bytes = img2pdf.convert(image_list)
    with open(output_name, 'wb') as file:
        file.write(pdf_bytes)


if __name__ == '__main__':
    folder = sys.argv[1]
    output_name = sys.argv[2]

    print('Folder name {}'.format(folder))
    
    print('====Finding files on directory====')
    image_list = find_images_path(folder, '.webp')
    
    print('====Files found====') 
    print(image_list)

    print('====Converting and cropping images====')
    convert_images(image_list)
    converted_images = find_images_path(folder, '.jpg')
    print(converted_images)

    print('====Converting to PDF====')
    jpg_list = find_images_path(folder, '.jpg')
    output_file = '{}/{}'.format(folder, output_name)
    convert_to_pdf(jpg_list, output_file, '.jpg')

    print('====Removing JPG files====')
    remove_jpg_images(folder, 'jpg')
