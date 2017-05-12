from argparse import ArgumentParser
from os import path, scandir, mkdir
from multiprocessing import cpu_count, Process
from tempfile import gettempdir
from uuid import uuid1
from PIL import Image
from time import time
import logging



def image_processing(img_names_dir, size, out_dir, is_monochrome):

    with open(img_names_dir) as img_names_file:
        img_names = [img for img in img_names_file.read().split('\n') if img]

    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO,
                        filename=path.join(out_dir, path.splitext(path.split(img_names_dir)[1])[0]+'.log'))

    logging.info('Begin')

    #images = {}

    for img_name in img_names:
        try:
            image = Image.open(img_name)
            image.load()
            n_image = image.convert('L') if is_monochrome else image.convert('RGB')
            n_image.thumbnail(size)
            n_image.save(path.join(out_dir, path.split(img_name)[1]))
        except Exception as e:
            logging.info('Got exception: {0}'.format(e))

    logging.info('End')


def parse_args():
    parser = ArgumentParser()

    parser.add_argument('-p', '--path', help='Path to folder', default=path.abspath(path.curdir))
    parser.add_argument('-x', '--width', help='New image width', default=64, type=int)
    parser.add_argument('-y', '--height', help='New image height', default=64, type=int)
    parser.add_argument('-c', '--processes', help='Number of parallel processes', default=cpu_count(), type=int)
    parser.add_argument('-o', '--output', help='Path to converted images')
    parser.add_argument('-m', '--monochrome', help='Make image monochrome', default=1, type=int)

    return vars(parser.parse_args())


def generate_dir():
    return path.join(gettempdir(), str(uuid1()))


def main():
    begin = time()

    args = parse_args()

    size = (args['width'], args['height'])

    temp_dir = generate_dir()

    mkdir(temp_dir)

    image_files = [entry.path for entry in scandir(args['path'])]

    count = args['processes']

    files = [open(path.join(temp_dir, 'image_{0}'.format(i)), 'w') for i in range(count)]

    for ind, name in enumerate(image_files):
        files[ind % count].write(name + '\n')

    for f in files:
        f.close()

    out_dir = args['output'] if args['output'] else path.join(path.pardir, path.split(args['path'])[1]+'_{0}x{1}'.format(size[0], size[1]) + ('_m' if args['monochrome'] else '' ))
    if not path.exists(out_dir):
        mkdir(out_dir)

    processes = []

    for i in range(count):
        p = Process(target=image_processing,
                    args=(path.join(temp_dir, 'image_{0}'.format(i)), size, out_dir, args['monochrome']))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    print('Time: {0} sec'.format(time() - begin))


if __name__ == "__main__":
    main()
