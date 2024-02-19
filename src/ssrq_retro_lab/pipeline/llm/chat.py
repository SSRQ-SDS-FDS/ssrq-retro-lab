import re
from typing import Iterable

import openai
from loguru import logger
from openai.types.chat import ChatCompletionMessageParam
from result import Err, Ok, Result

__all__ = ["create_chat_completion_param", "generate"]

USED_OPENAI_MODEL = [
    "ft:gpt-3.5-turbo-1106:personal:ssrq-ocr-cor:8tgnqalq",
    "gpt-3.5-turbo",
    "gpt-4-0125-preview",
]


def generate(
    prompt: str | Iterable[ChatCompletionMessageParam],
    model_name: str,
    extract_language: bool,
    language: str,
) -> Result[str, ValueError]:
    """Generate text completion for a given prompt using a specified model.

    Args:
        prompt (str): The prompt to generate text completion for.
        model_name (str): The name of the model to use for text completion.

    Returns:
        Result[str, ValueError]: The generated text completion or an error if the model name is not supported.
    """
    if model_name not in USED_OPENAI_MODEL:
        return Err(ValueError(f"Model name {model_name} is not supported"))

    result = _chat_with_open_ai(prompt, model_name)
    if result.is_err():
        return Err(ValueError(result.unwrap_err()))

    if extract_language:
        return Ok(_extract_language_block_from_chat_result(result.unwrap(), language))

    return Ok(result.unwrap())


def create_chat_completion_param(
    system: str, user: str, assistant: str | None
) -> Iterable[ChatCompletionMessageParam]:
    """Create a chat completion parameter for OpenAI's chat API.

    Args:
        system (str): The system message.
        user (str): The user message.
        assistant (str | None): The assistant message (if available).

    Returns:
        Iterable[ChatCompletionMessageParam]: The chat completion parameter.
    """
    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

    if assistant:
        messages.append({"role": "assistant", "content": assistant})

    return messages


def _chat_with_open_ai(
    prompt: str | Iterable[ChatCompletionMessageParam], model_name: str
) -> Result[str, str]:
    """Return chat completion for a given prompt using OpenAI's chat API.

    Args:
        prompt (str): The prompt to generate text completion for.
        model_name (str): The name of the model to use for text completion.

    Returns:
        Result[str, str]: The generated text completion or an error if the model name is not supported.
    """
    logger.debug(
        f"Requestion chat completion with model {model_name} for prompt:\n {prompt}"
    )

    resp = openai.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}]
        if isinstance(prompt, str)
        else prompt,
        temperature=0,
    )

    result = resp.choices[0].message.content

    if result is None:
        return Err(f"OpenAI model {model_name} returned None for prompt:\n {prompt}")

    logger.debug(f"Result returned by {model_name}:\n {result}")

    return Ok(result)


def _extract_language_block_from_chat_result(result: str, language: str) -> str:
    if f"```{language}" not in result:
        return result

    match = re.search("```" + re.escape(language) + r"(.*?)```", result, re.DOTALL)

    if match:
        return match.group(1).strip()
    return result
