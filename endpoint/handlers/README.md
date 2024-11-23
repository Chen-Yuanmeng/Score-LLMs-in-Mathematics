# Custom Handlers for LLMs

Files in this folder are custom handlers for the respective models, enabling them to be able to be run on [Inference Endpoints](https://ui.endpoints.huggingface.co/) under `Custom` task mode.

### Aspects these custom handlers do instead of default action

- These handlers will record the time spent generating responses and calculate the speed (tokens/s)
- These handlers provide specially-designed prompts
    - Models are guided to reason step by step and finally give an answer
    - Models are asked to tell their "confidence level" regarding the answers
- These handlers add `temperature`, `top_p` and `do_sample` parameters in generation


### Requirements and dependencies

These handlers all require `torch`, `transformers`, `random` and `time` libraries in Python 3 (although some handlers do not directly rely on some of them). Because these dependencies are by default included in the endpoint environment, no extra `requirements.txt` is needed.

### More information and credit

For more information about "Inference Endpoints", you can refer to these docs:
- https://huggingface.co/docs/inference-endpoints/index
- https://huggingface.co/docs/inference-endpoints/guides/custom_handler

I would also like to pay tribute to these articles and repositories for helping me understand and deploy the endpoints:
- [`data-is-better-together/custom-sd3.5-handler` on Huggingface](https://huggingface.co/data-is-better-together/custom-sd3.5-handler)
- [Deploy LLMs with Hugging Face Inference Endpoints](https://huggingface.co/blog/inference-endpoints-llm)

