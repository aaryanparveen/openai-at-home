from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from typing import Any, Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
import tiktoken

from providers.chatgpt import AnonChatGPT
from providers.mercury import MercuryProvider
from providers.base import Provider

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("openai-at-home")

MODEL_REGISTRY: dict[str, dict[str, Any]] = {
    "mercury": {
        "id": "mercury",
        "backend_model": "mercury-2",
        "object": "model",
        "created": 1700000000,
        "owned_by": "openai-at-home",
        "permission": [],
        "root": "mercury",
        "parent": None,
        "provider": MercuryProvider,
    },
    "mercury-2": {
        "id": "mercury-2",
        "backend_model": "mercury-2",
        "object": "model",
        "created": 1700000000,
        "owned_by": "openai-at-home",
        "permission": [],
        "root": "mercury-2",
        "parent": None,
        "provider": MercuryProvider,
    },
    "openai/gpt-4o": {
        "id": "openai/gpt-4o",
        "backend_model": "gpt-4o",
        "object": "model",
        "created": 1700000000,
        "owned_by": "openai-at-home",
        "permission": [],
        "root": "openai/gpt-4o",
        "parent": None,
        "provider": AnonChatGPT,
    },
    "openai/gpt-4o-mini": {
        "id": "openai/gpt-4o-mini",
        "backend_model": "gpt-4o-mini",
        "object": "model",
        "created": 1700000000,
        "owned_by": "openai-at-home",
        "permission": [],
        "root": "openai/gpt-4o-mini",
        "parent": None,
        "provider": AnonChatGPT,
    },
    "openai/gpt5-mini": {
        "id": "openai/gpt5-mini",
        "backend_model": "auto",
        "object": "model",
        "created": 1700000000,
        "owned_by": "openai-at-home",
        "permission": [],
        "root": "openai/gpt5-mini",
        "parent": None,
        "provider": AnonChatGPT,
    },
    "openai/gpt-5.3": {
        "id": "openai/gpt-5.3",
        "backend_model": "gpt-4o",
        "object": "model",
        "created": 1700000000,
        "owned_by": "openai-at-home",
        "permission": [],
        "root": "openai/gpt-5.3",
        "parent": None,
        "provider": AnonChatGPT,
    },
}

class ChatMessage(BaseModel):
    role: str
    content: Any
    name: Optional[str] = None

class ChatCompletionRequest(BaseModel):
    model: str = "openai/gpt-5.3"
    messages: list[ChatMessage]
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    stream_options: Optional[dict] = None
    stop: Optional[Any] = None
    max_tokens: Optional[int] = None
    max_completion_tokens: Optional[int] = None
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0
    logit_bias: Optional[dict] = None
    logprobs: Optional[bool] = None
    top_logprobs: Optional[int] = None
    user: Optional[str] = None
    seed: Optional[int] = None
    tools: Optional[list] = None
    tool_choice: Optional[Any] = None
    response_format: Optional[dict] = None

def openai_error(message: str, error_type: str = "invalid_request_error",
                 param: Optional[str] = None, code: Optional[str] = None,
                 status: int = 400) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={
            "error": {
                "message": message,
                "type": error_type,
                "param": param,
                "code": code,
            }
        },
    )

import re

def count_tokens(text: str) -> int:
    try:
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:
        return 0

def _cid() -> str:
    return "chatcmpl-" + uuid.uuid4().hex[:29]

def _ts() -> int:
    return int(time.time())

def _fp() -> str:
    return "fp_" + uuid.uuid4().hex[:10]

def build_completion(cid: str, model: str, content: str, created: int, prompt_tokens: int = 0) -> dict:
    match = re.search(r"<tool_call>\s*({.*?})\s*</tool_call>", content, re.DOTALL)
    
    if match:
        try:
            tool_data = json.loads(match.group(1))
            tool_calls = [{
                "id": f"call_{uuid.uuid4().hex[:24]}",
                "type": "function",
                "function": {
                    "name": tool_data.get("name", "unknown_tool"),
                    "arguments": json.dumps(tool_data.get("arguments", {}))
                }
            }]
            message_obj = {
                "role": "assistant",
                "content": None,
                "tool_calls": tool_calls,
                "refusal": None,
            }
            completion_tokens = count_tokens(match.group(1))
        except Exception:
            message_obj = {
                "role": "assistant",
                "content": content,
                "refusal": None,
            }
            completion_tokens = count_tokens(content)
    else:
        message_obj = {
            "role": "assistant",
            "content": content,
            "refusal": None,
        }
        completion_tokens = count_tokens(content)

    return {
        "id": cid,
        "object": "chat.completion",
        "created": created,
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": message_obj,
                "logprobs": None,
                "finish_reason": "tool_calls" if match else "stop",
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
        "system_fingerprint": _fp(),
    }

def build_chunk(cid: str, model: str, created: int,
                delta: dict, finish_reason: Optional[str] = None) -> dict:
    return {
        "id": cid,
        "object": "chat.completion.chunk",
        "created": created,
        "model": model,
        "system_fingerprint": _fp(),
        "choices": [
            {
                "index": 0,
                "delta": delta,
                "logprobs": None,
                "finish_reason": finish_reason,
            }
        ],
    }

app = FastAPI(title="OpenAI-Compatible at-home", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

@app.get("/")
async def root():
    return {"status": "ok", "service": "openai-at-home"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": m["id"],
                "object": "model",
                "created": m["created"],
                "owned_by": m["owned_by"],
                "permission": m.get("permission", []),
                "root": m.get("root", m["id"]),
                "parent": m.get("parent"),
            }
            for m in MODEL_REGISTRY.values()
        ],
    }

@app.get("/v1/models/{model_id:path}")
async def get_model(model_id: str):
    if model_id not in MODEL_REGISTRY:
        return openai_error(f"The model `{model_id}` does not exist.",
                            code="model_not_found", status=404)
    m = MODEL_REGISTRY[model_id]
    return {
        "id": m["id"],
        "object": "model",
        "created": m["created"],
        "owned_by": m["owned_by"],
        "permission": m.get("permission", []),
        "root": m.get("root", m["id"]),
        "parent": m.get("parent"),
    }

@app.post("/v1/chat/completions")
async def chat_completions(req: ChatCompletionRequest, request: Request):
    if req.model not in MODEL_REGISTRY:
        return openai_error(
            f"The model `{req.model}` does not exist or you do not have access to it.",
            code="model_not_found",
            status=404,
        )

    if not req.messages:
        return openai_error("'messages' is a required property.", param="messages")

    backend_model = MODEL_REGISTRY[req.model]["backend_model"]
    oai_msgs = [{"role": m.role, "content": m.content} for m in req.messages]
    
    if req.tools:
        tools_str = json.dumps([t.get("function", t) for t in req.tools], indent=2)
        system_instruction = (
            "You have access to the following tools:\n"
            f"{tools_str}\n\n"
            "To use a tool, you MUST output a raw JSON block wrapped in EXACTLY these XML tags, and NOTHING else:\n"
            "<tool_call>\n"
            '{"name": "tool_name", "arguments": { "arg1": "value1" }}\n'
            "</tool_call>\n\n"
            "Do NOT wrap the JSON in Markdown or backticks. Only use the <tool_call> tags."
        )
        if oai_msgs and oai_msgs[0]["role"] == "system":
            oai_msgs[0]["content"] += f"\n\n{system_instruction}"
        else:
            oai_msgs.insert(0, {"role": "system", "content": system_instruction})
            
    prompt_text = "".join(m["content"] for m in oai_msgs if isinstance(m["content"], str))
    prompt_tokens = count_tokens(prompt_text)
    
    logger.info("Chat request: model=%s backend_model=%s stream=%s msgs=%d tokens=%d", req.model, backend_model, req.stream, len(req.messages), prompt_tokens)

    ProviderClass = MODEL_REGISTRY[req.model]["provider"]
    client: Provider = ProviderClass()

    if not req.stream:
        loop = asyncio.get_event_loop()
        try:
            reply = await loop.run_in_executor(
                None, lambda: client.send_message(oai_msgs, model=backend_model)
            )
        except Exception as e:
            logger.error("Backend error: %s", e, exc_info=True)
            return openai_error(
                f"Backend error: {e}",
                error_type="server_error",
                code="backend_error",
                status=502,
            )
        cid = _cid()
        created = _ts()
        return JSONResponse(build_completion(cid, req.model, reply, created, prompt_tokens))

    async def sse_generator():
        import queue as _queue

        cid = _cid()
        created = _ts()
        loop = asyncio.get_event_loop()
        generated_tokens = []

        role_chunk = build_chunk(cid, req.model, created, {"role": "assistant", "content": ""})
        yield f"data: {json.dumps(role_chunk)}\n\n"

        token_q: _queue.Queue = _queue.Queue()
        _SENTINEL = object()

        def _run_stream():
            try:
                for token in client.stream_message_live(oai_msgs, model=backend_model):
                    token_q.put(token)
            except Exception as e:
                token_q.put(e)
            finally:
                token_q.put(_SENTINEL)

        loop.run_in_executor(None, _run_stream)

        buffer = ""
        in_tool_call = False
        tool_json_buffer = ""
        tool_call_id = f"call_{uuid.uuid4().hex[:24]}"
        tool_fired_initial_chunk = False

        while True:
            try:
                item = await asyncio.wait_for(loop.run_in_executor(None, token_q.get), timeout=120)
            except asyncio.TimeoutError:
                break

            if item is _SENTINEL:
                break
            if isinstance(item, Exception):
                logger.error("Stream error: %s", item, exc_info=True)
                err_chunk = build_chunk(cid, req.model, created, {"content": f"[Error: {item}]"}, "stop")
                yield f"data: {json.dumps(err_chunk)}\n\n"
                yield "data: [DONE]\n\n"
                return

            generated_tokens.append(item)
            buffer += item
            
            if not in_tool_call:
                if "<tool_call>" in buffer:
                    in_tool_call = True
                    pre_tag = buffer.split("<tool_call>")[0]
                    if pre_tag:
                        content_chunk = build_chunk(cid, req.model, created, {"content": pre_tag})
                        yield f"data: {json.dumps(content_chunk)}\n\n"
                    
                    tool_json_buffer = buffer.split("<tool_call>")[1]
                    buffer = ""
                else:
                    if len(buffer) > 11 and not "<" in buffer[-11:]:
                        safe_content = buffer[:-11]
                        buffer = buffer[-11:]
                        if safe_content:
                            content_chunk = build_chunk(cid, req.model, created, {"content": safe_content})
                            yield f"data: {json.dumps(content_chunk)}\n\n"
            
            else:
                tool_json_buffer += item
                if "</tool_call>" in tool_json_buffer:
                    json_str = tool_json_buffer.split("</tool_call>")[0].strip()
                    try:
                        tool_data = json.loads(json_str)
                        delta = {
                            "tool_calls": [{
                                "index": 0,
                                "id": tool_call_id,
                                "type": "function",
                                "function": {
                                    "name": tool_data.get("name", "unknown_tool"),
                                    "arguments": json.dumps(tool_data.get("arguments", {}))
                                }
                            }]
                        }
                        tool_chunk = build_chunk(cid, req.model, created, delta)
                        yield f"data: {json.dumps(tool_chunk)}\n\n"
                    except Exception as e:
                        logger.error(f"Failed to parse intercepted tool call JSON: {e}")
                        
                    buffer = tool_json_buffer.split("</tool_call>")[1]
                    in_tool_call = False
                    tool_json_buffer = ""

        if not in_tool_call and buffer:
            content_chunk = build_chunk(cid, req.model, created, {"content": buffer})
            yield f"data: {json.dumps(content_chunk)}\n\n"

        stop_chunk = build_chunk(cid, req.model, created, {}, "stop")
        
        final_text = "".join(generated_tokens)
        completion_tokens = count_tokens(final_text)
        stop_chunk["usage"] = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens
        }
        
        yield f"data: {json.dumps(stop_chunk)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        sse_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

@app.exception_handler(422)
async def validation_exception_handler(request, exc):
    return openai_error(
        str(exc),
        error_type="invalid_request_error",
        code="invalid_request",
        status=422,
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=13373, log_level="info")
