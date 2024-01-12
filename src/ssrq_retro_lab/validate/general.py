from sklearn.metrics import accuracy_score, f1_score
from collections import namedtuple

MLMetrics = namedtuple("MLMetrics", ["accuracy", "f1_score"])


def calc_ml_metrics(y_true: list, y_pred: list) -> MLMetrics:
    """Calculate the ML metrics.

    Args:
        y_true (list): The true labels.
        y_pred (list): The predicted labels.

    Returns:
        MLMetrics: The ML metrics.
    """
    return MLMetrics(
        accuracy_score(y_true, y_pred), f1_score(y_true, y_pred, average="weighted")
    )
