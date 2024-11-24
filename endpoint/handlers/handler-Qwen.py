import time
import random
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

class EndpointHandler:
    """
    Custom handler for `Qwen/Qwen2.5-Math-7B-Instruct`.
    """
    def __init__(self, path=""):
        """
        Initialize model and tokenizer.
        :param path: Path to model and tokenizer
        """
        self.tokenizer = AutoTokenizer.from_pretrained(path)
        self.model = AutoModelForCausalLM.from_pretrained(path, torch_dtype="auto", device_map="auto")

    def __call__(self, data: dict):
        """
        Execute model based on input data.

        :param data: Input parameters for the model.
            Should be in the following form:
            `{"inputs": "input_string", "parameters": {"parameter_1": 0, "parameter_2": 0}}`

        :return: dict (answer, num_new_token, speed)
        """

        question = data.get("inputs", None)
        max_new_tokens = data.get("max_new_tokens", 1024)
        parameters = data.get("parameters", {})

        if not question:
            raise ValueError("Input prompt is missing.")

        messages = [
            {"role": "system", "content": "Please reason step by step, and put your final answer within \\boxed{}."},
            {"role": "user", "content": question + " Then, give your confidence level regarding your answer."}
        ]

        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        model_inputs = self.tokenizer([text], return_tensors="pt").to("cuda")

        torch.manual_seed(random.randint(0, 2 ** 32 - 1))

        time_start = time.time()
        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=max_new_tokens,
            temperature=1.0,
            do_sample=True,
            top_p=0.9,
            **parameters
        )
        time_end = time.time()

        num_new_tokens = len(generated_ids[0]) - len(model_inputs[0])

        generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in
                         zip(model_inputs.input_ids, generated_ids)]

        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

        speed = num_new_tokens / (time_end - time_start)

        return {
            "answer": response,
            "num_new_tokens": num_new_tokens,
            "speed": speed
        }

