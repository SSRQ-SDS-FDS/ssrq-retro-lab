from dataclasses import dataclass

from ssrq_retro_lab.train.messages import MESSAGE_REPLACEMENT_PATTERN


@dataclass
class OpenAIDataset:
    system: str
    user: str
    assistant: str

    def to_dict(self) -> dict[str, list[dict[str, str]]]:
        return {
            "messages": [
                {"role": "system", "content": self.system},
                {"role": "user", "content": self.user},
                {"role": "assistant", "content": self.assistant},
            ]
        }


def create_openai_dataset(
    system_role: str,
    user_template: str,
    user_text: str,
    assistant_template: str,
    assistant_text: str,
) -> OpenAIDataset:
    return OpenAIDataset(
        system=system_role,
        user=insert_text_into_template(user_template, user_text),
        assistant=insert_text_into_template(assistant_template, assistant_text),
    )


def insert_text_into_template(template: str, text: str, pattern: str = MESSAGE_REPLACEMENT_PATTERN) -> str:
    return template.replace(pattern, text)
