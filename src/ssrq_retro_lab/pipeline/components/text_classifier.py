import json
from typing import Literal

from loguru import logger
from pydantic import BaseModel
from result import Err, Ok
from spacy_llm.registry.reader import fewshot_reader
from textdistance import cosine
from typeguard import typechecked

from ssrq_retro_lab.config import ZG_DATA_ROOT
from ssrq_retro_lab.pipeline.components.html_wrangler import HTMLTextExtractionResult
from ssrq_retro_lab.pipeline.components.protocol import Component, ComponentError
from ssrq_retro_lab.pipeline.llm.chat import generate
from ssrq_retro_lab.pipeline.templates.utils import render_template

CLASSIFICATON_DEFAULT_TEMPLATE = "textline_classification_v1.jinja2"
FEWSHORT_EXAMPLE = ZG_DATA_ROOT / "examples" / "few-shot-article-lines.json"

TextLabels = Literal["LINENUMBER", "REFERENCE", "SUMMARY", "TITLE", "TEXT"]


class TextClass(BaseModel):
    text: str
    label: TextLabels
    reason: str


class ClassifiedText(BaseModel):
    classified_text: list[TextClass]


class StructuredArticle(BaseModel):
    article_number: int
    date: str
    references: list[str]
    summary: list[str]
    text: list[str]
    title: str


class TextClassifier(Component):
    _allowed_retries = 1
    _name = "TextClassifier"
    _repeat_previous = False

    @typechecked
    def invoke(self, text: HTMLTextExtractionResult):
        structured_article = StructuredArticle(
            article_number=text["entry"].no,
            date=text["entry"].date,
            references=[],
            summary=[],
            text=[],
            title=text["entry"].title,
        )

        examples = fewshot_reader(FEWSHORT_EXAMPLE)()
        schema = json.dumps(ClassifiedText.model_json_schema(), indent=2)
        labels = TextLabels.__args__  # type: ignore

        for i, p in enumerate(text["article"]):
            textline = p.get()

            if textline is None:
                logger.debug(f"Textline {i} is None. Skipping...")
                continue

            prompt = render_template(
                CLASSIFICATON_DEFAULT_TEMPLATE,
                paragraph=textline,
                schema=schema,
                labels=labels,
                prompt_examples=examples,
                article_number=f"{structured_article.article_number}.",
            )

            classification_result = generate(prompt, "gpt-3.5-turbo", True, "json")

            if classification_result.is_err():
                return Err(ComponentError(classification_result.unwrap_err().args[0]))

            try:
                validated_classification_result = ClassifiedText.model_validate_json(
                    self._extract_json_from_result(classification_result.unwrap())
                )
            except Exception as e:
                return Err(
                    ComponentError(f"Failed to validate classification result: {e}")
                )

            for c in validated_classification_result.classified_text:
                match c.label:
                    case "LINENUMBER":
                        logger.debug(f"Skipping line number {c.text}")
                        continue
                    case "REFERENCE":
                        structured_article.references.append(c.text)
                    case "SUMMARY":
                        structured_article.summary.append(c.text)
                    case "TITLE":
                        if TextClassifier._is_real_title(
                            structured_article.article_number,
                            textline,
                            text["entry"].title,
                            c.text,
                        ):
                            structured_article.title = c.text
                        else:
                            structured_article.summary.append(c.text)
                    case "TEXT":
                        structured_article.text.append(c.text)

        if len(structured_article.text) == 0 and len(structured_article.summary) == 0:
            Err(
                ComponentError(
                    f"No text or summary found in the article with number {structured_article.article_number}"
                )
            )

        return Ok(structured_article)

    def _extract_json_from_result(self, result: str) -> str:
        import re

        if "```json" not in result:
            return result

        match = re.search(r"```json(.*?)```", result, re.DOTALL)

        if match:
            return match.group(1).strip()
        return result

    @staticmethod
    def _is_real_title(
        article_number: int, paragraph: str, entry_title: str, parsed_title: str
    ) -> bool:
        """It seems, that the LLM has problems to classify summaries and titles correctly.
        This function tries to fix that by checking if the paragraph contains the article number or if the cosine
        similarity between the entry title and the parsed title is above 0.75. If one of the conditions is met, the
        paragraph is considered to be the title of the article.

        Args:
            article_number (int): The article number.
            paragraph (str): The paragraph to check.
            entry_title (str): The entry title.
            parsed_title (str): The parsed title.

        Returns:
            bool: True if the paragraph is considered to be the title, False otherwise."""
        if f"{article_number}." in paragraph:
            return True
        if cosine(entry_title, parsed_title) > 0.75:
            return True
        return False
