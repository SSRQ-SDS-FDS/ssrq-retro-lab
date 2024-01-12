from collections import defaultdict


def validate_openai_training_data(dataset: list) -> bool:
    """Validates the OpenAI training data.

    See: https://cookbook.openai.com/examples/chat_finetuning_data_prep

    Args:
        data: The data to validate.

    Returns:
        True if the data is valid, False otherwise.
    """
    # Format error checks
    format_errors = defaultdict(int)  # type: ignore

    for ex in dataset:
        if not isinstance(ex, dict):
            format_errors["data_type"] += 1
            continue

        messages = ex.get("messages", None)
        if not messages:
            format_errors["missing_messages_list"] += 1
            continue

        for message in messages:
            if "role" not in message or "content" not in message:
                format_errors["message_missing_key"] += 1

            if any(
                k not in ("role", "content", "name", "function_call") for k in message
            ):
                format_errors["message_unrecognized_key"] += 1

            if message.get("role", None) not in (
                "system",
                "user",
                "assistant",
                "function",
            ):
                format_errors["unrecognized_role"] += 1

            content = message.get("content", None)
            function_call = message.get("function_call", None)

            if (not content and not function_call) or not isinstance(content, str):
                format_errors["missing_content"] += 1

        if not any(message.get("role", None) == "assistant" for message in messages):
            format_errors["example_missing_assistant_message"] += 1

    if format_errors:
        print("Found errors:")  # noqa: T201
        for k, v in format_errors.items():
            print(f"{k}: {v}")  # noqa: T201
        return False

    print("No errors found")  # noqa: T201
    return True
