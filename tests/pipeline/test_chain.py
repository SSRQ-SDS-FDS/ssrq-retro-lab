from ssrq_retro_lab.pipeline import chain
from ssrq_retro_lab.pipeline.components.text_extractor import (
    ExtractionInput,
    TextExtractor,
)


def test_chain_execute_succeeds_for_simple_pipeline():
    components = (TextExtractor(),)
    result = chain.executor(ExtractionInput(777, 518, 518), components)

    assert chain.is_ok(result)
