# Getting the outputs of models

After the inference endpoints are deployed, we can use the deployed endpoints to run the models and get the output needed by the experiment.

Using the script `get_answer.py`, you can automatically get the model outputs.

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
