from dataclasses import asdict
from typing import Any, Callable, Optional

from openai import OpenAI as _OpenAI
from openai.resources.chat import Completions
from openai.types.chat import ChatCompletion
from wrapt import wrap_function_wrapper

from genai_impact.compute_impacts import MODEL_SIZES, compute_llm_impact


def chat_wrapper(
    wrapped: Callable, instance: Completions, args: Any, kwargs: Any  # noqa: ARG001
) -> ChatCompletion:
    response = wrapped(*args, **kwargs)
    model_size = MODEL_SIZES.get(response.model)
    output_tokens = response.usage.completion_tokens
    impacts = compute_llm_impact(
        model_parameter_count=model_size, output_token_count=output_tokens
    )
    response.impacts = asdict(impacts)
    return response


class OpenAI(_OpenAI):
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, **kwargs: Any) -> None:
        super().__init__(api_key=api_key, base_url=base_url)

    wrap_function_wrapper(
        "openai.resources.chat.completions", "Completions.create", chat_wrapper
    )
