import re

import openai
from loguru import logger
from result import Err, Ok, Result

__all__ = ["generate"]

USED_OPENAI_MODEL = ["gpt-3.5-turbo", "gpt-4-0125-preview"]


def generate(
    prompt: str, model_name: str, extract_language: bool, language: str
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


def _chat_with_open_ai(prompt: str, model_name: str) -> Result[str, str]:
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
        model=model_name, messages=[{"role": "user", "content": prompt}], temperature=0
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
