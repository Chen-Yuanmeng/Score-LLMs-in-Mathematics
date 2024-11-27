import json
import os
from answer import Answer

ls_files = []

os.makedirs('markdown', exist_ok=True)

for _, _, c in os.walk("answers"):
    ls_files += c

counter = 0

for file_name in ls_files:
    with open("./answers/" + file_name, 'r', encoding="UTF-8") as f:
        original_output = json.load(f)

    converted_md = []

    for ans in original_output:
        converted_md.append(Answer.from_dct(ans).to_markdown())

    counter += 1

    with open(f"markdown/{counter % 24 + 1}.md", 'a', encoding="UTF-8") as g:
        print("".join(converted_md), file=g)

