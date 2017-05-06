from os import scandir, path, rename, mkdir
import csv
from argparse import ArgumentParser
import time


EXIT_SUCCESS = 0
EXIT_INCORRECT_PATH = -1
EXIT_EMPTY_ARG = -2
EXIT_FILE_NOT_FOUND = -3
EXIT_INCORRECT_FILE = -4


def parse_args():

    parser = ArgumentParser(description='Move excess images')

    parser.add_argument('-f', '--dir_from', help='path to directory with images')
    parser.add_argument('-t', '--to', help='path to directory with excess images')
    parser.add_argument('-c', '--csv', help='path to csv file')

    return vars(parser.parse_args())


def main():

    begin = time.time()

    args = parse_args()

    if None in args.values():
        return EXIT_EMPTY_ARG, args

    try:
        if not path.isfile(args['csv']):
            args['csv'] = next((entry.path for entry in scandir(args['csv']) if path.splitext(entry.name)[1] == '.csv')) # and this
        elif path.splitext(args['csv'])[-1] != '.csv':
            return EXIT_INCORRECT_FILE, 'csv'
    except FileNotFoundError:
        return EXIT_INCORRECT_PATH, 'csv'
    except StopIteration:
        return EXIT_FILE_NOT_FOUND, 'csv'

    csv_product_ids = None
    try:
        with open(args['csv'], 'r') as csv_file:
            csv_product_ids = set((row[0]+'.jpg' for row in csv.reader(csv_file))) # check what is faster
    except FileNotFoundError:
        return EXIT_INCORRECT_PATH, 'csv'

    if not csv_product_ids:
        return EXIT_INCORRECT_FILE, 'csv'

    try:
        to_product_ids = [entry.name for entry in scandir(args['dir_from']) if entry.name not in csv_product_ids] # and this too
    except FileNotFoundError:
        return EXIT_INCORRECT_PATH, 'dir_from'

    try:
        if not path.exists(args['to']):
            mkdir(args['to'])
    except FileNotFoundError:
        return EXIT_INCORRECT_PATH, 'to'

    for img in to_product_ids:
        rename(path.join(args['dir_from'], img), path.join(args['to'], img))

    diff = time.time() - begin

    return EXIT_SUCCESS, diff


if __name__ == '__main__':

    ret, addit = main()

    if EXIT_SUCCESS == ret:
        print('secs: {0}'.format(addit))
    elif EXIT_INCORRECT_PATH == ret:
        print("Incorrect path: {0}".format(addit))
    elif EXIT_FILE_NOT_FOUND == ret:
        print("File not found: {0}".format(addit))
    elif EXIT_EMPTY_ARG == ret:
        print("Empty arg(s): {0}".format(addit))
    elif EXIT_INCORRECT_FILE == ret:
        print("Incorrect file: {0}".format(addit))
