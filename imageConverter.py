from argparse import ArgumentParser
from os import path, scandir, mkdir, rmdir
from multiprocessing import cpu_count, Process
import tempfile
import uuid
from PIL import Image


def image_processing(temp_dir, filename, size, out_dir):
    img_names = (img for img in open(path.join(temp_dir, filename)).read().split('\n') if img)
    for img_name in img_names:
        try:
            image = Image.open(img_name)
            gray = image.convert('L') # gray is here
            gray.thumbnail(size)
            gray.save(path.join(out_dir, path.split(img_name)[1]))
        except Exception:
            pass


def parse_args():
    parser = ArgumentParser()

    parser.add_argument('-p', '--path', help='Path to folder', default=path.abspath(path.curdir))
    parser.add_argument('-x', '--width', help='New image width', default=64, type=int)
    parser.add_argument('-y', '--height', help='New image height', default=64, type=int)
    parser.add_argument('-c', '--processes', help='Number of parallel processes', default=cpu_count()*2, type=int)
    parser.add_argument('-o', '--output', help='Path to converted images')

    return vars(parser.parse_args())


def generate_dir():
    return path.join(tempfile.gettempdir(), str(uuid.uuid1()))


def main():
    args = parse_args()

    temp_dir = generate_dir()
    mkdir(temp_dir)

    image_files = [entry.path for entry in scandir(args['path'])]

    count = args['processes']

    files = [open(path.join(temp_dir, 'image_{0}'.format(i)), 'w') for i in range(count)]

    for ind, name in enumerate(image_files):
        files[ind % count].write(name + '\n')

    map(lambda x: x.close(), files)

    out_dir = args['output'] if args['output'] else path.join(path.pardir, 'images_ {0}_{1}'.format(args['width'], args['height']))

    if not path.exists(out_dir):
        mkdir(out_dir)

    print(temp_dir)

    processes = []

    for i in range(count):
        p = Process(target=image_processing, args=(temp_dir, 'image_{0}'.format(i), (args['width'], args['height']), out_dir))
        processes.append(p)
        p.start()

    for p in processes:
       p.join()


if __name__ == "__main__":
    main()