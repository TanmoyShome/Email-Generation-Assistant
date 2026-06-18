import gradio as gr
from fastapi import FastAPI

from app.api.v1.api import api_router
from app.config.settings import settings
from frontend.frontend import build_ui


app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "name": settings.PROJECT_NAME,
        "docs": "/docs",
        "gradio": "/gradio",
    }


gradio_app = build_ui()
app = gr.mount_gradio_app(app, gradio_app, path="/gradio")
