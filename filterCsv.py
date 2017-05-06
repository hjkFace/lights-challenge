import csv
from os import path, scandir
from argparse import ArgumentParser

unique_fields = set(['ProductID', 'EID', 'PID', 'VID', 'Product Title'])


def parse_args():

    parser = ArgumentParser()

    parser.add_argument('min', type=int, help='Minimal number of occurrences')
    parser.add_argument('-i', '--input', help='Path to original csv file')
    parser.add_argument('-f', '--filtered', help='Path and name of the output filtered file')
    parser.add_argument('-e', '--excess', help='Path and name of the output excess file')

    return vars(parser.parse_args())


def parse_csv(entries, names, products, uniques):

    names.update({idx: name for idx, name in enumerate(next(entries))})

    for entry in entries:
        element = {names[idx]: value for idx, value in enumerate(entry)}
        products.append(element)

        for name in set(names.values()) - unique_fields:
            if not element[name]:
                continue

            uniques.setdefault(name, {})
            uniques[name].setdefault(element[name], 0)
            uniques[name][element[name]] += 1


def update_uniques(uniques, min_value):

    for product in uniques.values():
        for name, count in list(product.items()):
            if count >= min_value:
                del product[name]


def main():

    args = parse_args()

    csv_file = ''

    if args['input']:
        csv_file = args['input']
    else:
        try:
            csv_file = next((path.abspath(entry.path) for entry in scandir(path.curdir) if path.splitext(entry.name)[1] == '.csv'))
        except StopIteration:
            print('csv file not found')
            return
    products = []
    uniques = {}
    names = {}
    try:
        with open(csv_file) as cf:
            entries = csv.reader(cf, lineterminator='\r')
            parse_csv(entries, names, products, uniques)
    except FileNotFoundError:
        print("File not found")
        return

    if not products or not uniques:
        print("File is empty")
        return

    update_uniques(uniques, args['min'])

    csv_path = path.split(csv_file)[0]
    csv_name, csv_ext = path.splitext(csv_file)

    csv_filtered = args['filtered'] if args['filtered'] else path.join(csv_path, csv_name + '_filtered' + csv_ext)
    csv_excess = args['excess'] if args['excess'] else path.join(csv_path, csv_name + '_excess' + csv_ext)

    try:
        file_filtered = open(csv_filtered, 'w')
        file_excess = open(csv_excess, 'w')
    except FileNotFoundError:
        print("I have problems")
        return

    filtered_writer = csv.writer(file_filtered, lineterminator='\r')
    excess_writer = csv.writer(file_excess, lineterminator='\r')

    names_keys = sorted(names.keys())
    names_lst = [names[key] for key in names_keys]

    filtered_writer.writerow(names_lst)
    excess_writer.writerow(names_lst)

    for product in products:
        is_excess = False
        product_row = []
        for key in names_keys:
            if not is_excess and names[key] in uniques and product[names[key]] in uniques[names[key]]:
                is_excess = True
            product_row.append(product[names[key]])
        if is_excess:
            excess_writer.writerow(product_row)
        else:
            filtered_writer.writerow(product_row)

    file_filtered.close()
    file_excess.close()


if __name__ == '__main__':
    main()
