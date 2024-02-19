from pathlib import Path

import openai


def upload_training_file_to_openai(training_file: Path) -> str:
    """Upload the training file to OpenAI
    and returns the file id.

    Args:
        path: The path to the training file.

    Returns:
        The file id.
    """
    file_upload = openai.files.create(
        file=training_file,
        purpose="fine-tune",
    )

    return file_upload.id


def create_openai_finetuning_job(
    training_file_id: str,
    name: str,
    model: str = "gpt-3.5-turbo-1106",
    epochs: int = 3,
    validation_file_id: str | None = None,
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
        validation_file=validation_file_id,
        model=model,
        suffix=name,
        hyperparameters={"n_epochs": epochs},
    )

    return response.id


def get_finetuned_model_id(job_id: str) -> str:
    """Gets the id of the finetuned model.

    Args:
        job_id: The id of the job.

    Returns:
        The id of the finetuned model.
    """
    job = openai.fine_tuning.jobs.retrieve(job_id)
    model_id = job.fine_tuned_model

    if model_id:
        return model_id

    raise ValueError("No model id found")
