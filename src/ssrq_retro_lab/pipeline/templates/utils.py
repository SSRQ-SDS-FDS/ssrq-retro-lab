from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

__all__ = ["render_template"]

TEMPLATE_DIR: Path = Path(__file__).parent


def render_template(template_name: str, **kwargs) -> str:
    """Render a Jinja2 template with the given arguments.

    Args:
        template_name (str): The name of the template to render.
        **kwargs: The arguments to pass to the template.

    Returns:
        str: The rendered template.
    """
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), undefined=StrictUndefined)
    template = env.get_template(template_name)

    return template.render(**kwargs)
