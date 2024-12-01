import csv
import os
import json
from answer import Answer


def main():
    file_lst = []

    output_file = open('output.csv', 'w', newline='', encoding="UTF-8")
    writer = csv.writer(output_file)

    # Write heading
    writer.writerow([
        "Unique ID", "Category", "Sub-category", "Question in Chinese",
        "Question in English", "Answer", "Occurrence", "Model output",
        "Number of new tokens", "Speed", "Model", "Mark", "Need rerun",
        "Confidence level", "Additional info"
    ])

    for a, b, c in os.walk(os.path.join(os.getcwd(), "corrections")):
        file_lst = c

    for file in file_lst:
        with open("corrections/" + file, 'r', encoding='UTF-8') as f:
            tmp = json.load(f)

            for i in tmp:
                writer.writerow(Answer.from_dct(i).to_csv())

    output_file.close()


if __name__ == '__main__':
    main()