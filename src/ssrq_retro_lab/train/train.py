import os
from pathlib import Path
from ssrq_retro_lab.repository.reader import BufferBinaryReader

import openai

openai.api_key = os.environ.get("OPEN_AI_API_KEY")


def upload_training_file_to_openai(training_file: Path) -> str:
    """Upload the training file to OpenAI
    and returns the file id.

    Args:
        path: The path to the training file.

    Returns:
        The file id.
    """
    file_upload = openai.files.create(
        file=BufferBinaryReader(training_file).read(),
        purpose="fine-tune",
    )

    return file_upload.id


def create_openai_finetuning_job(
    training_file_id: str, name: str, model: str = "gpt-3.5-turbo-16k", epochs: int = 3
) -> str:
    """Creates a new OpenAI fine-tuning job.

    Args:
        training_file_id: The id of the training file.
        name: The name of the job.
        model: The model to use.
        epochs: The number of epochs to train.

    Returns:
        The id of the created job.
    """
    response = openai.fine_tuning.jobs.create(
        training_file=training_file_id,
        model=model,
        suffix=name,
        hyperparameters={"n_epochs": epochs},
    )

    return response.id
