from config import cfg
import openai
from typing import List, Dict, Optional
from fastapi import WebSocket
from langchain.adapters import openai as lc_openai
from colorama import Fore, Style

import logging

async def create_chat_completion(
        messages: list,  # type: ignore
        model: Optional[str] = None,
        temperature: float = 1.0,
        max_tokens: Optional[int] = None,
        llm_provider: Optional[str] = None,
        stream: Optional[bool] = False,
        websocket: WebSocket | None = None,
) -> str:
    """Create a chat completion using the OpenAI API
    Args:
        messages (list[dict[str, str]]): The messages to send to the chat completion
        model (str, optional): The model to use. Defaults to None.
        temperature (float, optional): The temperature to use. Defaults to 0.9.
        max_tokens (int, optional): The max tokens to use. Defaults to None.
        stream (bool, optional): Whether to stream the response. Defaults to False.
        llm_provider (str, optional): The LLM Provider to use.
        webocket (WebSocket): The websocket used in the currect request
    Returns:
        str: The response from the chat completion
    """

    # validate input
    if model is None:
        raise ValueError("Model cannot be None")
    if max_tokens is not None and max_tokens > 8001:
        raise ValueError(f"Max tokens cannot be more than 8001, but got {max_tokens}")

    # create response
    for attempt in range(10):  # maximum of 10 attempts
        response = await send_chat_completion_request(
            messages, model, temperature, max_tokens, stream, llm_provider, websocket
        )
        return response

    logging.error("Failed to get response from OpenAI API")
    raise RuntimeError("Failed to get response from OpenAI API")


async def send_chat_completion_request(
        messages, model, temperature, max_tokens, stream, llm_provider, websocket
):
    if not stream:
        result = lc_openai.ChatCompletion.create(
            model=model,  # Change model here to use different models
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            provider=llm_provider,  # Change provider here to use a different API
        )
        return result["choices"][0]["message"]["content"]
    else:
        return await stream_response(model, messages, temperature, max_tokens, llm_provider, websocket)


async def stream_response(model, messages, temperature, max_tokens, llm_provider, websocket=None):
    paragraph = ""
    response = ""

    for chunk in lc_openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            provider=llm_provider,
            stream=True,
    ):
        content = chunk["choices"][0].get("delta", {}).get("content")
        if content is not None:
            response += content
            paragraph += content
            if "\n" in paragraph:
                if websocket is not None:
                    await websocket.send_json({"type": "report", "output": paragraph})
                else:
                    print(f"{Fore.GREEN}{paragraph}{Style.RESET_ALL}")
                paragraph = ""
    return response


# ===============================================================

def create_chat_message(role, content):
    """
    Create a chat message with the given role and content.

    Args:
    role (str): The role of the message sender, e.g., "system", "user", or "assistant".
    content (str): The content of the message.

    Returns:
    dict: A dictionary containing the role and content of the message.
    """
    return {"role": role, "content": content}


# TODO - add token cost
def generate_context(prompt: str, full_msg_history: List[Dict], role: str) -> List[Dict]:
    full_msg_history.append(create_chat_message(role, prompt))
    return full_msg_history


def chat_completion(messages: List[Dict], model=cfg.fast_llm_model, temperature=cfg.temperature,
                    max_tokens=None) -> str:
    """
    :param messages:
    :param model:
    :param temperature:
    :param max_tokens:
    :return:
    """
    try:
        response = openai.ChatCompletion.create(
            # api_base='https://api.qqslyx.com/v1',
            # response = chat_completion_with_backoff(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            messages=messages
        )
    except Exception as e:
        print(e)
        raise

    if response is None:
        raise RuntimeError("Failed to get response after 5 retries")

    return response.choices[0].message["content"]
