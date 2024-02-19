import json
from typing import cast

from diskcache import Cache
from loguru import logger
from pydantic import BaseModel
from result import Err, Ok, Result, is_err, is_ok
from typeguard import typechecked

from ssrq_retro_lab.config import CACHE_DIR
from ssrq_retro_lab.pipeline.components.protocol import Component, ComponentError
from ssrq_retro_lab.pipeline.components.text_classifier import (
    StructuredArticle,
    TextClassifier,
)
from ssrq_retro_lab.pipeline.llm.chat import (
    create_chat_completion_param,
    generate,
)
from ssrq_retro_lab.pipeline.templates.utils import render_template
from ssrq_retro_lab.train.messages import SYSTEM_ROLE_V2


class CorrectedOCRText(BaseModel):
    text: list[str]


class StructuredCorrectedArticle(StructuredArticle):
    corrected_references: CorrectedOCRText
    corrected_summary: CorrectedOCRText
    corrected_text: CorrectedOCRText


class OCRCorrector(Component):
    _allowed_retries = 0
    _name = "OCRCorrector"
    _repeat_previous = False
    TOKEN_LIMIT = 16385

    @typechecked
    def invoke(
        self, article: StructuredArticle
    ) -> Result[StructuredCorrectedArticle, ComponentError]:
        # ToDo: Implement correction of references and summary
        corrected_article = StructuredCorrectedArticle(
            article_number=article.article_number,
            date=article.date,
            corrected_references=CorrectedOCRText(text=article.references),
            references=article.references,
            corrected_summary=CorrectedOCRText(text=article.summary),
            summary=article.summary,
            corrected_text=CorrectedOCRText(text=[]),
            text=article.text,
            title=article.title,
        )
        with Cache(CACHE_DIR / self._name) as cache:
            text_correction_prompt = render_template(
                template_name="openai_ocr_training_user_v2.jinja2",
                schema=json.dumps(CorrectedOCRText.model_json_schema(), indent=2),
                text_input=json.dumps(
                    corrected_article.text, indent=2, ensure_ascii=False
                ),
            )

            corrected_text = self._correct(text_correction_prompt, cache)

            if is_err(corrected_text):
                return Err(corrected_text.unwrap_err())

            corrected_article.corrected_text = corrected_text.unwrap()

        return Ok(corrected_article)

    def _correct(
        self, user_prompt: str, cache: Cache
    ) -> Result[CorrectedOCRText, ComponentError]:
        # ToDo: Check if user prompt exceeds token limit
        cache_key = TextClassifier.create_cache_key(user_prompt)

        if cache_key in cache:
            logger.debug(f"Correction result for '{user_prompt}' found in cache")
            logger.debug(f"Correction result from cache:\n {cache[cache_key]}")
            return self._validate_correction_result(cast(str, cache[cache_key]))

        messages = create_chat_completion_param(
            system=SYSTEM_ROLE_V2, user=user_prompt, assistant=None
        )

        result = generate(
            prompt=messages,
            model_name="ft:gpt-3.5-turbo-1106:personal:ssrq-ocr-cor:8tgnqalq",
            extract_language=True,
            language="json",
        )

        if result.is_err():
            return Err(ComponentError(result.unwrap_err().args[0]))

        validated_result = self._validate_correction_result(result.unwrap())

        if is_ok(validated_result):
            cache[cache_key] = validated_result.unwrap().model_dump_json()

        return validated_result

    def _validate_correction_result(
        self, result: str
    ) -> Result[CorrectedOCRText, ComponentError]:
        try:
            return Ok(CorrectedOCRText.model_validate_json(result))
        except Exception as e:
            return Err(ComponentError(f"Failed to validate correction result: {e}"))
