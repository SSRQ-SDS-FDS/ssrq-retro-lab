from typing import cast

import gradio as gr
from loguru import logger
from result import is_err
from spacy.tokens import Doc

from ssrq_retro_lab.pipeline import chain
from ssrq_retro_lab.pipeline.components.ocr_corrector import StructuredCorrectedArticle
from ssrq_retro_lab.pipeline.components.text_extractor import ExtractionInput

ARTICLE_NUMBERS = range(1, 1881 + 1)


# Handler hinzufügen
logger.add("output.log")


def run_chain(
    article_input: list | int,
) -> tuple[list[tuple[str, str]], str, str] | tuple[str, ...]:
    if isinstance(article_input, list) and len(article_input) == 0:
        logger.error("Please select a article at first...")
        return tuple(["No article selected" for _ in range(3)])

    article_number: int = cast(int, article_input)
    logger.debug(f"Starting chain for article number {article_number}...")
    result = chain.executor(
        initial_input=ExtractionInput(article_number=int(article_number)),
        components=chain.DEFAULT_COMPONENTS,
    )

    if is_err(result):
        raise ValueError(result.unwrap_err().message)

    chain_result: tuple[StructuredCorrectedArticle, Doc, str] = result.unwrap()

    return (
        [
            (ent.text, ent.label_)
            for ent in chain_result[1].ents
            if ent.label_ in ["PERSON", "PERSON", "==NONE=="]
        ],
        f"{chain_result[0].title}\n{'\n'.join(chain_result[0].corrected_text.text)}",
        chain_result[2],
    )


def read_logs():
    with open("output.log", "r") as f:
        return f.read()


def main():
    with gr.Blocks(css=".textspan::after{ content: '\a'; white-space: pre;}") as demo:
        gr.Markdown("# 🧪 SSRQ Retro Lab")
        with gr.Row():
            article = gr.Dropdown(
                list(ARTICLE_NUMBERS), label="Select an article to process"
            )

        with gr.Row():
            # use the output here
            with gr.Column():
                ner_viz = gr.HighlightedText(label="Named Entities found")
                textbox = gr.Textbox(
                    value="Corrected OCR Text", label="Corrected OCR Text"
                )
            codebox = gr.Code(label="TEI XML", language="html")

        btn = gr.Button("Start LLM chain")
        btn.click(run_chain, article, outputs=[ner_viz, textbox, codebox])

        logs = gr.Textbox(label="Logs", value="No logs yet")

        demo.load(read_logs, None, logs, every=1)

    demo.launch()


if __name__ == "__main__":
    main()
