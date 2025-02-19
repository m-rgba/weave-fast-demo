import os
import weave
from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
from typing import List, Literal
from openai import AsyncOpenAI

app = FastAPI(
    title="My FastAPI",
    description="This is a sample app.",
    version="1.0.0",
)

openai_client = AsyncOpenAI()
google_client = AsyncOpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

weave.init(f"{os.getenv('WEAVE_TEAM')}/{os.getenv('WEAVE_PROJECT_ID')}")


class CompletionRequest(BaseModel):
    prompt: str


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatCompletionRequest(BaseModel):
    model: Literal["openai", "google"]
    messages: List[ChatMessage]


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def read_index():
    html_content = Path("templates/index.html").read_text()
    modified_html = html_content.replace(
        "weave-team-id/weave-project-id",
        f"{os.getenv('WEAVE_TEAM')}/{os.getenv('WEAVE_PROJECT_ID')}",
    )
    return StreamingResponse(iter([modified_html]), media_type="text/html")


@weave.op()
@app.post("/google/completion")
async def completion(request: ChatCompletionRequest):
    async def generate_response():
        system_message = {
            "role": "system",
            "content": "You are a helpful virtual assistant for a weightlifting store. Your goal is to help customers find the right equipment, answer questions about weightlifting, and provide excellent customer service. Be knowledgeable but friendly and approachable. If a user requests to speak with a human, advise them to sign into their account and select the help and support option. This is a demo app created by Weights & Biases, powered by Weave.",
        }
        messages = [system_message] + [
            {"role": msg.role, "content": msg.content} for msg in request.messages
        ]

        stream = await google_client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=messages,
            stream=True,
        )
        async for chunk in stream:
            if content := chunk.choices[0].delta.content:
                yield content

    return StreamingResponse(generate_response(), media_type="text/event-stream")


@weave.op()
@app.post("/openai/completion")
async def completion(request: ChatCompletionRequest):
    async def generate_response():
        system_message = {
            "role": "system",
            "content": "You are a helpful virtual assistant for a weightlifting store. Your goal is to help customers find the right equipment, answer questions about weightlifting, and provide excellent customer service. Be knowledgeable but friendly and approachable. If a user requests to speak with a human, advise them to sign into their account and select the help and support option. This is a demo app created by Weights & Biases, powered by Weave.",
        }
        messages = [system_message] + [
            {"role": msg.role, "content": msg.content} for msg in request.messages
        ]

        stream = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            stream=True,
        )
        async for chunk in stream:
            if content := chunk.choices[0].delta.content:
                yield content

    return StreamingResponse(generate_response(), media_type="text/event-stream")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
