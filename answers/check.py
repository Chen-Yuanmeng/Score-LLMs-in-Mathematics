import argparse
import json
import re
from os import PathLike

with open("ls_uids.json", 'r') as f:
    ls_UIDs = json.load(f)

def markdown_checker(filepath: int | str | bytes | PathLike[str] | PathLike[bytes], encoding="UTF-8") -> None:
    """
    Check one Markdown (.md) file to see whether your file can be accepted

    :param filepath: Path to Markdown file that needs to be checked.
    :param encoding: Encoding of Markdown file. Defaults to `UTF-8`.
    :return: None
    """
    with open(filepath, 'r', encoding=encoding) as f:
        text = f.read()

    for segment in text.split("---<!-- This is the end of this segment -->"):
        if segment.strip():
            single_markdown_checker(segment)


def single_markdown_checker(text):
    unique_id_match = re.search(r'(?<=## UID:\s)[^\n]+', text)
    model_match = re.search(r'(?<=<!-- Model:\s)[^-]+', text)
    instance_match = re.search(r'(?<=Instance\s)[^\n]', text)

    mark_match = re.search(r'(?<=\*\*Mark \(0~100/None\):\*\*)[^\n]+', text)
    need_rerun_match = re.search(r'(?<=\*\*Needs rerun \(Y/N\):\*\*)[^\n]+', text)
    confidence_match = re.search(r'(?<=\*\*Confidence:\*\*)[^\n]+', text)
    additional_info_match = re.search(r'(?<=\*\*Additional Info:\*\*)[^\n]+', text)

    uid = check_uid(unique_id_match)

    return {
        "unique_ID": uid,
        "model": check_model(model_match, uid),
        "occurrence": check_instance(instance_match, uid),
        "mark": check_mark(mark_match, uid),
        "need_rerun": check_need_rerun(need_rerun_match, uid),
        "confidence_level": check_confidence(confidence_match, uid),
        "additional_info": check_additional_info(additional_info_match)
    }


def check_uid(uid_match: re.Match[str] | None) -> str | None:
    if uid_match is None:
        print('Error: Some UID is empty. Please check.')
        return None
    else:
        name = uid_match.group().strip()
        if name == '':
            print('Error: Some UID is empty. Please check.')
            return None
        if name not in ls_UIDs:
            print('UID', name, 'is not in the UID list. Check if you accidentally edited it.')
            return None
        return name


def check_model(model_match: re.Match[str] | None, uid) -> str | None:
    if model_match is None:
        print(f'Error: model for UID {str(uid)} is empty. Please check.')
        return None
    else:
        name = model_match.group().strip()
        if name == '':
            print(f'Error: model for UID {str(uid)} is empty. Please check.')
            return None
        if name.upper() not in ['DEEPSEEK', 'LLAMA', 'MATHSTRAL', 'QWEN']:
            print('Error: Model', name, 'is not in the model list. Check if you accidentally edited it.')
            return None
        return name


def check_instance(instance_match: re.Match[str] | None, uid) -> int | None:
    if instance_match is None:
        print(f'Error: Instance for UID {str(uid)} is empty. Please check.')
        return None
    else:
        inst = instance_match.group().strip()
        if inst == '':
            print(f'Error: Instance for UID {str(uid)} is empty. Please check.')
            return None
        if inst not in ['1', '2', '3']:
            print('Error: Instance', str(inst), 'is not in [1, 2, 3]. Check if you accidentally edited it.')
            return None
        return int(inst)

def check_mark(mark_match: re.Match[str] | None, uid) -> int | None:
    if mark_match is None:
        print(f'Error: Mark for UID {str(uid)} is empty. Please check.')
        return None
    else:
        mark = mark_match.group().strip()
        if mark == '':
            print(f'Error: Mark for UID {str(uid)} is empty. Please check.')
            return None
        if mark == 'None':
            return -1
        elif 0 <= int(mark) <= 100:
            return int(mark)
        else:
            print("Error: Mark", mark, f"for UID {str(uid)} is illegal input.")
            return None

def check_need_rerun(rerun_match: re.Match[str] | None, uid) -> bool | None:
    if rerun_match is None:
        print(f'Error: Need_rerun for UID {str(uid)} is empty. Please check.')
        return None
    else:
        rerun = rerun_match.group().strip()
        if rerun == '':
            print(f'Error: Need_rerun for UID {str(uid)} is empty. Please check.')
            return None
        if rerun == 'Y':
            return True
        elif rerun == 'N':
            return False
        else:
            print("Error: Need_rerun", rerun, f"for UID {str(uid)} is illegal input.")
            return None


def check_confidence(confidence_match: re.Match[str] | None, uid) -> str | None:
    if confidence_match is None:
        print(f'Error: confidence for UID {str(uid)} is empty. Please check.')
        return None
    else:
        confidence = confidence_match.group().strip()
        if confidence == '':
            print(f'Error: confidence for UID {str(uid)} is empty. Please check.')
            return None
        return confidence

def check_additional_info(addi_info_match: re.Match[str] | None) -> str:
    if addi_info_match is None:
        return ""
    addi_info = addi_info_match.group().strip()
    return addi_info


def main():
    parser = argparse.ArgumentParser(description='Check the format of your markdown output.')
    parser.add_argument('files', nargs='+', help='List of input files')
    args = parser.parse_args()

    for file in args.files:
        markdown_checker(file)


if __name__ == '__main__':
    main()
