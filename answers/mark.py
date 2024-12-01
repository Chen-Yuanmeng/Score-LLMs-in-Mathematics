import json
import os
from os import PathLike
from typing import Any
from answers.check import single_markdown_checker


def markdown_parser(filepath: int | str | bytes | PathLike[str] | PathLike[bytes], encoding="UTF-8") -> None:
    """
    Parse one Markdown (.md) file pieced together from multiple Answer.to_markdown() return values to obtain:

    - mark
    - need_rerun
    - confidence_level
    - additional_info

    :param filepath: Path to Markdown file that needs to be parsed.
    :param encoding: Encoding of Markdown file. Defaults to `UTF-8`.
    :return: None
    """
    with open(filepath, 'r', encoding=encoding) as f:
        text = f.read()

    for segment in text.split("---<!-- This is the end of this segment -->"):
        if segment.strip():
            write_information_to_file(single_markdown_checker(segment))

def write_information_to_file(parsed_info: dict[str, Any]):
    file_path = "corrections/" + parsed_info['unique_ID'] + "_" + parsed_info['model'] + ".json"

    with open(file_path, 'r', encoding='UTF-8') as f:
        original = json.load(f)

    new = []

    for i in original:
        if i['occurrence'] == parsed_info['occurrence']:
            tmp = dict(i)
            tmp['mark'] = parsed_info['mark']
            tmp['need_rerun'] = parsed_info['need_rerun']
            tmp['confidence_level'] = parsed_info['confidence_level']
            tmp['additional_info'] = parsed_info['additional_info']
            new.append(tmp)
        else:
            new.append(i)

    os.makedirs('corrections', exist_ok=True)
    with open(file_path, 'w', encoding='UTF-8') as g:
        json.dump(new, g, ensure_ascii=False, indent=4)


def main():
    number_of_files = 24

    for i in range(1, number_of_files + 1):
        filepath = 'markdown/' + str(i) + '.md'

        markdown_parser(filepath)

if __name__ == '__main__':
    main()
