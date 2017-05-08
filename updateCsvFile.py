from argparse import ArgumentParser
from os import path, scandir


def parse_args():

    parser = ArgumentParser()
    parser.add_argument('-p', '--path', help='Path to file or folder with file', default=path.curdir)

    return vars(parser.parse_args())


def main():
    args = parse_args()

    try:
        if path.isfile(args['path']):
            csv_file = args['path']
        else:
            csv_file = next((entry.path for entry in scandir(args['path']) if path.splitext(entry)[1] == '.csv'))

        with open(csv_file, 'rb') as f:
            data = f.read()
            data = data.replace(b'\r', b'')
        with open(path.splitext(csv_file)[0] + '_update.csv', 'wb') as f:
            f.write(data)
    except (FileNotFoundError, StopIteration):
        print('File not found')
        return


if __name__ == '__main__':
    main()
