from collections.abc import Sequence
from typing import Any

from loguru import logger
from result import Ok, Result, is_err, is_ok

from ssrq_retro_lab.pipeline.components.html_wrangler import HTMLWrangler
from ssrq_retro_lab.pipeline.components.ner_annotator import NERAnnotator
from ssrq_retro_lab.pipeline.components.ocr_corrector import OCRCorrector
from ssrq_retro_lab.pipeline.components.protocol import Component, ComponentError
from ssrq_retro_lab.pipeline.components.tei_converter import TEIConverter
from ssrq_retro_lab.pipeline.components.text_classifier import TextClassifier
from ssrq_retro_lab.pipeline.components.text_extractor import TextExtractor

DEFAULT_COMPONENTS = (
    TextExtractor(),
    HTMLWrangler(),
    TextClassifier(),
    OCRCorrector(),
    NERAnnotator(),
    TEIConverter(),
)


def executor(
    initial_input: Any, components: Sequence[Component]
) -> Result[Any, ComponentError]:
    """Executes a sequence of components with the given input.

    This function allows to execute a sequence of components – e.g. a pipeline, which
    integrates calls to different services (like LLMs) – with the given input. The
    components are executed in the order they are provided. If a component fails, the
    executor will retry the component up to the maximum number of retries allowed for
    the component. If a component fails, the executor will log the error and continue
    with the next component. If the maximum number of retries is reached, the executor
    will log an error and return the error.

    The intermediate results of the components are passed to the next component as input.
    The output of every component is logged by default.

    Args:
        initial_input: The initial input for the first component.
        components: The components to execute.
        allowed_retries: The maximum number of retries for each component.

    Returns:
        The result of the last component or an error if any component failed.
    """
    index = 0
    retries = 0
    result = initial_input

    while index < len(components):
        component = components[index]
        component_result = component.invoke(result)

        if is_err(component_result):
            logger.error(component_result.unwrap_err().message)

            if retries == component._allowed_retries:
                if component._allowed_retries == 0:
                    logger.error(f"{component._name} failed with input {result}.")
                else:
                    logger.error(
                        f"Maximum retries of {component._allowed_retries} reached for {component._name}. Failed with input {result}."
                    )
                return component_result

            if component._repeat_previous and retries == 0:
                logger.warning(
                    f"Component {component._name} allows previous component execution..."
                )
                retries += 1
                index -= 1
                continue

            logger.warning(f"Retrying {component._name}...")
            retries += 1
            continue

        if is_ok(component_result):
            retries = 0
            result = component_result.unwrap()
            logger.success(f"{component._name} succeeded with result:\n{result}")

            index += 1

    return Ok(result)
