from collections import namedtuple

import textdistance
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ErrorRate = namedtuple("ErrorRate", ["cer", "similarity"])


def calc_error_rate(master: str, page: str) -> ErrorRate:
    """Calculate the error rate between the master and the page.

    Args:
        master (str): The master text.
        page (str): The page text.

    Returns:
        ErrorRate: The error rate between the master and the page.
    """
    cer = textdistance.levenshtein.normalized_distance(master, page) * 100
    vectorizer = CountVectorizer()

    bag_of_words = vectorizer.fit_transform([master, page])

    similarity = cosine_similarity(bag_of_words[0:1], bag_of_words[1:2])  # type: ignore

    return ErrorRate(cer, similarity[0][0])
