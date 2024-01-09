import numpy as np
import tiktoken

ENCODING = tiktoken.get_encoding("cl100k_base")


# not exact!
# simplified from https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
def num_tokens_from_messages(messages: list[dict[str, str]], tokens_per_message=3, tokens_per_name=1) -> int:
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(ENCODING.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3
    return num_tokens


def num_assistant_tokens_from_messages(messages: list[dict[str, str]]) -> int:
    num_tokens = 0
    for message in messages:
        if message["role"] == "assistant":
            num_tokens += len(ENCODING.encode(message["content"]))
    return num_tokens


def print_distribution(values, name):
    print(f"\n#### Distribution of {name}:")  # noqa: T201
    print(f"min / max: {min(values)}, {max(values)}")  # noqa: T201
    print(f"mean / median: {np.mean(values)}, {np.median(values)}")  # noqa: T201
    print(f"p5 / p95: {np.quantile(values, 0.1)}, {np.quantile(values, 0.9)}")  # noqa: T201
