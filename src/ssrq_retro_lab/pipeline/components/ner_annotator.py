import sys
from typing import cast

from diskcache import Cache
from result import Err, Ok, Result, is_err
from spacy.tokens import Doc, DocBin
from spacy_llm.util import assemble
from spacy_llm import logger as spacy_logger
from typeguard import typechecked

from ssrq_retro_lab.config import CACHE_DIR, PROJECT_ROOT, ZG_DATA_ROOT
from ssrq_retro_lab.pipeline.components.ocr_corrector import StructuredCorrectedArticle
from ssrq_retro_lab.pipeline.components.protocol import Component, ComponentError
from ssrq_retro_lab.pipeline.components.text_classifier import TextClassifier
from logging import StreamHandler
from loguru import logger


class NERAnnotator(Component):
    _allowed_retries = 0
    _name = "NERAnnotator"
    _repeat_previous = False

    @typechecked
    def invoke(
        self,
        corrected_article: StructuredCorrectedArticle,
    ) -> Result[tuple[StructuredCorrectedArticle, Doc], ComponentError]:
        with Cache(CACHE_DIR / self._name) as cache:
            annotated_text = self._annotate(corrected_article, cache)

            if is_err(annotated_text):
                return annotated_text

            annotations = annotated_text.unwrap()

            self._log_annotations(annotations)

            return Ok(
                (
                    corrected_article,
                    annotations,
                )
            )

    def _annotate(
        self,
        corrected_article: StructuredCorrectedArticle,
        cache: Cache,
    ) -> Result[Doc, ComponentError]:
        cache_key = TextClassifier.create_cache_key(
            "ner_annotated".join(corrected_article.corrected_text.text)
        )
        nlp = assemble(
            (PROJECT_ROOT / "spacy_config.cfg"),
            overrides={
                "paths.examples": str((ZG_DATA_ROOT / "examples" / "few-shot-ner.json"))
            },
        )
        if cache_key in cache:
            logger.debug(
                f"Annotated text with key {cache_key} / article number {corrected_article.article_number} found in cache."
            )
            return Ok(
                cast(
                    Doc,
                    list(
                        DocBin()
                        .from_bytes(cast(bytes, cache[cache_key]))
                        .get_docs(nlp.vocab)
                    )[0],
                )
            )

        try:
            doc = nlp("\n".join(corrected_article.corrected_text.text))
            doc_bin = DocBin()
            doc_bin.add(doc)
            cache[cache_key] = doc_bin.to_bytes()
        except Exception as e:
            return Err(ComponentError(f"Failed to annotate text: {e}"))

        return Ok(doc)

    def _log_annotations(self, doc: Doc):
        for ent in doc.ents:
            logger.debug(f"Entity: {ent.text}, Label: {ent.label_}")
