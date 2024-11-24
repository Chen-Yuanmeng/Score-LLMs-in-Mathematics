import torch
import time
import random
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig, LlamaForCausalLM

class EndpointHandler:
    """
    Custom handler for `deepseek-ai/deepseek-math-7b-instruct`.
    """
    def __init__(self, path=""):
        """
        Initialize model and tokenizer.
        :param path: Path to model and tokenizer
        """
        self.tokenizer = AutoTokenizer.from_pretrained(path)
        self.model: LlamaForCausalLM = AutoModelForCausalLM.from_pretrained(path, torch_dtype=torch.bfloat16, device_map="auto")
        self.model.generation_config = GenerationConfig.from_pretrained(path)
        self.model.generation_config.pad_token_id = self.model.generation_config.eos_token_id

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
            {
                "role": "user",
                "content": f"{question}\nPlease reason step by step, and put your final answer "
                           "within \\boxed{}. Then, give your confidence level regarding your answer."
            }
        ]

        input_tensor = self.tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt")

        torch.manual_seed(random.randint(0, 2 ** 32 - 1))

        time_start = time.time()
        outputs = self.model.generate(
            input_tensor.to(self.model.device),
            max_new_tokens=max_new_tokens,
            temperature=1.0,
            do_sample=True,
            top_p=0.9,
            **parameters
        )
        time_end = time.time()

        num_new_tokens = len(outputs[0]) - len(input_tensor[0])
        speed = num_new_tokens / (time_end - time_start)

        answer = self.tokenizer.decode(outputs[0][input_tensor.shape[1]:], skip_special_tokens=True)

        return {
            "answer": answer,
            "num_new_tokens": num_new_tokens,
            "speed": speed
        }
