import time
import torch
import random
from transformers import AutoTokenizer, AutoModelForCausalLM

class EndpointHandler:
    """
    Custom handler for `meta-llama/Llama-3.1-8B-Instruct`.
    """
    def __init__(self, path=""):
        """
        Initialize model and tokenizer.
        :param path: Path to model and tokenizer
        """
        self.tokenizer = AutoTokenizer.from_pretrained(path)
        self.model = AutoModelForCausalLM.from_pretrained(path, torch_dtype=torch.bfloat16, device_map="auto")

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
            {"role": "system", "content": "Please reason step by step, and put your final answer within \\boxed{}. "
                                          "Then, give your confidence level in percentage regarding your answer."},
            {"role": "user", "content": question}
        ]

        tokenized_prompt = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_dict=True,
            return_tensors="pt"
        ).to("cuda")

        torch.manual_seed(random.randint(0, 2 ** 32 - 1))

        time_start = time.time()
        out = self.model.generate(
            **tokenized_prompt,
            max_new_tokens=max_new_tokens,
            temperature=1.0,
            do_sample=True,
            top_p=0.9,
            **parameters
        )
        time_end = time.time()

        response = self.tokenizer.decode(out[0])

        num_new_tokens = len(out[0]) - len(tokenized_prompt[0])

        speed = num_new_tokens / (time_end - time_start)

        return {
            "answer": response,
            "num_new_tokens": num_new_tokens,
            "speed": speed
        }
