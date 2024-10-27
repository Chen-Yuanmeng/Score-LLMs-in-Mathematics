import argparse
import json
import time


def main():
    parser = argparse.ArgumentParser(description='Merge some files.')
    parser.add_argument('files', nargs='+', help='List of input files')
    args = parser.parse_args()
    
    new_lst = []

    for file in args.files:
        with open(file, 'r', encoding='UTF-8') as f:
            new_lst += json.load(f)

    with open(f'merged-output-{str(int(time.time()))}.json', 'w', encoding='UTF-8') as g:
        json.dump(new_lst, g, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()
