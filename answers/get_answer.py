import configparser
import json
import os
import time
import sys
import logging
import requests
from answer import Answer
from typing import Any

# Read config from config.ini
config = configparser.ConfigParser()
config.read("config.ini")

API_URL_deepseek = config.get("API_URL", "api_url_deepseek")
API_URL_qwen = config.get("API_URL", "api_url_qwen")
API_URL_mathstral = config.get("API_URL", "api_url_mathstral")
API_URL_llama = config.get("API_URL", "api_url_llama")

HEADERS = {
    "Accept": "application/json",
    "Authorization": config.get('ACCESS_TOKEN', "access_token"),
    "Content-Type": "application/json"
}

# Log information
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="app.log",
    filemode="a",
    encoding="UTF-8"
)


# Log unhandled exception
def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

# 设置全局未捕获异常处理
sys.excepthook = handle_uncaught_exception


# Construct self-defined `request`
# Prevent occasional network disconnections
def web_request(url, method='GET', max_retries=3, **kwargs):
    """
    Below are the params of ``requests.get``:

    def get(url: str | bytes, params, *, data, headers, cookies, files, auth, timeout,
    allow_redirects: bool, proxies, hooks, stream: bool | None, verify,
    cert, json: Any | None) -> Response

    We mimic the ``requests.get``, ``requests.post`` and so on , specify param timeout,
    and add param max_tries to the original ``requests.request``
    to better use it under various circumstances.

    :param url: URL for the new :class:`Request` object.
    :param method: method for the new :class:`Request` object: ``GET``, ``OPTIONS``,
        ``HEAD``, ``POST``, ``PUT``, ``PATCH``, or ``DELETE``. Defaults to ``GET``
    :param timeout: How many seconds to wait for the server
        to send data before giving up, as a float, or a :ref:`(connect timeout, read
        timeout) <timeouts>` tuple. Defaults to 0.2 seconds.
    :type timeout: float or tuple
    :param max_retries: Defaults to 3.

    Below are the optional parameters that need to be provided in the form of keyword arguments:

    - param params: (optional) Dictionary, list of tuples or bytes to send in the query string for the :class:`Request`.

    - param data: (optional) Dictionary, list of tuples, bytes, or file-like object to send in the body of the :class:`Request`.

    - param json: (optional) A JSON serializable Python object to send in the body of the :class:`Request`.

    - param headers: (optional) Dictionary of HTTP Headers to send with the :class:`Request`.

    - param cookies: (optional) Dict or CookieJar object to send with the :class:`Request`.

    - param files: (optional) Dictionary of ``'name': file-like-objects`` (or ``{'name': file-tuple}``) for multipart encoding upload. ``file-tuple`` can be a 2-tuple ``('filename', fileobj)``, 3-tuple ``('filename', fileobj, 'content_type')`` or a 4-tuple ``('filename', fileobj, 'content_type', custom_headers)``, where ``'content-type'`` is a string defining the content type of the given file and ``custom_headers`` a dict-like object containing additional headers to add for the file.

    - param auth: (optional) Auth tuple to enable Basic/Digest/Custom HTTP Auth.

    - param allow_redirects: (optional) Boolean. Enable/disable GET/OPTIONS/POST/PUT/PATCH/DELETE/HEAD redirection. Defaults to ``True``.

    - param proxies: (optional) Dictionary mapping protocol to the URL of the proxy.

    - param verify: (optional) Either a boolean, in which case it controls whether we verify     the server's TLS certificate, or a string, in which case it must be a path     to a CA bundle to use. Defaults to ``True``.

    - param stream: (optional) if ``False``, the response content will be immediately downloaded.

    - param cert: (optional) if String, path to ssl client cert file (.pem). If Tuple, ('cert', 'key') pair.

    :return: :class:`requests.Response<Response>` object
    """

    response = None
    err_msg = ''
    additional = ''

    try:
        response = requests.request(method, url, **kwargs)
    except requests.ConnectionError as e:
        # Retry and record error information
        for retry in range(max_retries - 1):
            try:
                response = requests.request(method, url, **kwargs)
            except requests.ConnectionError as f:
                err_msg = 'It seems that connection to the host is blocked. Try pinging the host in command: ' + str(f)
            except requests.RequestException as f:
                err_msg = str(f)
            else:
                err_msg = ''
                break
    except requests.RequestException as e:
        # Retry and record error information
        for retry in range(max_retries - 1):
            try:
                response = requests.request(method, url, **kwargs)
            except requests.RequestException as f:
                err_msg = str(f)
            else:
                additional = ' The request ended with ' + retry + 2 + ' retries.'
                err_msg = ''
                break

    if err_msg:
        raise RuntimeError(err_msg)
    else:
        logging.info('Web request successful: ' + method + " " + url + additional)
        return response


# Base class for models
class Model:
    """
    Base class for all models.

    Used for helping post answers from endpoints.
    """
    API_URL = ""
    name = "AutoModel"

    def __init__(self):
        logging.debug("Successfully set model parameters: name = " + self.name + ", API_URL = " + self.API_URL)

    @classmethod
    def ask(cls, question: dict[str, str | int | float], occurrence: int, max_new_tokens=4096,
            parameters: dict = None):
        # Example question:
        # question = {
        #     "Unique ID": "asus.1732070916",
        #     "Category": "MP",
        #     "Sub-category": "C1",
        #     "Question in Chinese": "计算$6+  \\left ( 5- 8 \\right ) {\\div} 3\\times \\sqrt{4}$.",
        #     "Question in English": "Calculate $ 6+  \\left ( 5- 8 \\right ) {\\div} 3\\times \\sqrt{4}$.",
        #     "Answer": "4"
        # }

        if parameters is None:
            parameters = {}

        payload = {
            "inputs": question["Question in English"],
            "max_new_tokens": max_new_tokens,
            "parameters": parameters
        }

        response = web_request(cls.API_URL, 'POST', headers=HEADERS, json=payload).json()

        # Example response:
        # response = {
        #     "answer": "Example answer",
        #     "num_new_tokens": 200,
        #     "speed": 30.0
        # }

        logging.info("Received model output for question " + question["Unique ID"] + ", occurrence " + str(occurrence))

        return Answer(
            unique_ID=question["Unique ID"],
            category=question["Category"],
            sub_category=question["Sub-category"],
            question_in_Chinese=question["Question in Chinese"],
            question_in_English=question["Question in English"],
            answer=question["Answer"],
            occurrence=occurrence,  # Could be 1, 2, 3
            model_output=response["answer"],  # Output from model
            num_new_tokens=response["num_new_tokens"],  # Length of model output in tokens
            speed=response["speed"],  # Speed of model output in tokens per second
            model=cls.name  # Model name
        )


class Deepseek(Model):
    name = "Deepseek"
    API_URL = API_URL_deepseek

    def __init__(self):
        super().__init__()


class Llama(Model):
    name = "Llama"
    API_URL = API_URL_llama

    def __init__(self):
        super().__init__()


class Mathstral(Model):
    name = "Mathstral"
    API_URL = API_URL_mathstral

    def __init__(self):
        super().__init__()


class Qwen(Model):
    name = "Qwen"
    API_URL = API_URL_qwen

    def __init__(self):
        super().__init__()


def get_output(question: dict[str, str], model: Model) -> list[dict[str, Any]]:
    """
    Get the model output (3 occurrences) to a question given by the model.

    :param question: Question to ask model, in standard format
    :param model: One of `Deepseek`, `Llama`, `Mathstral`, `Qwen`.
    :return: List of the three answers given by `model` in the form given by `Answer.to_dct`.
    """
    answer_output = []

    for i in [1, 2, 3]:
        answer_output.append(model.ask(question=question, occurrence=i).to_dct())

    return answer_output


def get_answer_and_write_to_file(question: dict[str, str], model: Model, force: bool = False) -> None:
    """
    Get the designated model's output of a question, and save it to file.

    :param question: Question to ask model, in standard format
    :param model: One of `Deepseek`, `Llama`, `Mathstral`, `Qwen`.
    :param force: If `force=True`, will overwrite file that already exists. Otherwise, files that already exist will be ignored.
    """

    os.makedirs('answers', exist_ok=True)
    file_path = "answers/" + question["Unique ID"] + "_" + model.name + ".json"

    if os.path.exists(file_path) and (not force):
        logging.info("File " + file_path + " has been created. Return immediately.")
        return

    output = get_output(question, model)

    with open(file_path, 'w', encoding="UTF-8") as g:
        json.dump(
            output,
            g,
            indent=4,
            ensure_ascii=False
        )

    logging.info("Saved model output to " + file_path)


def main():
    question_file_paths = [
        "../questions/Calculation.json",
        "../questions/Calculus.json",
        "../questions/Differential_Equation_Solving.json",
        "../questions/Geometry.json",
        "../questions/Linear_Algebra.json",
        "../questions/Mathematical_Statistics.json"
    ]

    model = Qwen()

    for file in question_file_paths:
        with open(file, 'r', encoding='UTF-8') as f:
            question_list = json.load(f)

        for q in question_list:
            get_answer_and_write_to_file(q, model)


if __name__ == '__main__':
    main()
