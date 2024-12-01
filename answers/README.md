# Getting the outputs | marking | generating CSV file

This folder contains the code for getting the output of models, marking the answers and generating CSV files.

# Getting the outputs of models

After the inference endpoints are deployed, we can use the deployed endpoints to run the models and get the output needed by the experiment.

Using the script `get_answer.py`, you can automatically get the model outputs. The outputs will automatically be written to the `answers` folder.

There are some points you need to pay attention to before running the script:

- Note that the script only gets the output from one model at one time, and you need to manually modify which model needs to be run. Do this by modifying this line to others (commented out):

    ```python
    model = Deepseek()
    # model = Llama()
    # model = Mathstral()
    # model = Qwen()
    ```
  
- You need to enter the api_url of your endpoints and your Hugging Face access token in `config.ini` as below:

    ```ini
    [API_URL]
    api_url_deepseek = https://replace.with.your.own.url
    api_url_qwen = https://replace.with.your.own.url
    api_url_mathstral = https://replace.with.your.own.url
    api_url_llama = https://replace.with.your.own.url
    
    [ACCESS_TOKEN]
    access_token = Bearer hf_replace_with_your_access_token
    ```
- Sometimes the inference endpoints experience crashes and will cause the program to exit with errors. You can simply rerun the script and it will automatically continue from where it last failed. Also, you can check the `app.log` file for more information.


## Marking the answers

Use the script `generate_markdown.py`, you can convert all answers in the `answers` folder to Markdown files. These files will be placed under the `Markdown` folder.

- Because when a single Markdown file is too large, performance issues may occur, the script splits the markdown into many files. The number can be set in the file:

    ```python
    number_of_files = 24
    ```

- The gaps that meed filling in are:
    - Mark (0~100/None)
    - Needs rerun (Y/N)
    - Confidence
    - Additional Info (this gap is optional)


## Checking the marks

You can use the script `check.py` to check if the required gaps are all filled correctly. Use

```bash
python check.py markdown/1.md markdown/2.md
```

to run the script. The check results will be printed to the console.
- Both absolute and relative paths are acceptable.
- You can add multiple files to the parameters to check all of them.

## Generating CSV files

After your Markdown files passes the check, you can parse the Markdown files into a CSV file. Here are the procedures:

1. Copy all JSON files under `answers` to a new `corrections` folder. This is to prevent original data from being damaged because of potential errors while running the script.

2. Use the script `mark.py` to parse the Markdown files into JSON. Please note that this needs to be in accordance with what you set when generating Markdown files:

    ```python 
    number_of_files = 24
    ```

    Then, the data in the Markdown files will be written to the JSON files in the `corrections` folder.

3. Use the script `generate_csv.py` to put all data from the JSON files in the `corrections` folder to a CSV file `output.csv`.

4. Open the CSV file, and you can see all data and deal with them. Please note that Excel does not support opening CSV files in `UTF-8` encoding. Please use the `Import data from text/csv` function and save the data to an Excel file instead.
