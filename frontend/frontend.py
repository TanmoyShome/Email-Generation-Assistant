import json
from pathlib import Path

import gradio as gr
import httpx

from app.config.settings import settings

BASE_URL = settings.FRONTEND_BASE_URL
OUTPUT_DIR = Path(settings.FRONTEND_OUTPUT_DIR)


def upload_file_to_endpoint(endpoint: str, file_path: Path) -> dict:
    """Upload a file to a given endpoint and return the JSON response."""
    with file_path.open("rb") as fh:
        files = {"file": (file_path.name, fh, "application/json")}
        response = httpx.post(f"{BASE_URL}/{endpoint}", files=files, timeout=30)
        response.raise_for_status()
    return response.json()


def generate_from_file(uploaded_file):
    """Generate email(s) by uploading a JSON file to the /generates endpoint."""
    if not uploaded_file:
        return "Please upload a JSON file.", None, ""

    file_path = Path(uploaded_file)
    try:
        data = upload_file_to_endpoint("generates", file_path)
    except Exception as exc:
        return f"Generation failed: {exc}", None, ""

    # Extract emails from the response
    if "results" in data and data["results"]:
        emails = "\n\n---\n\n".join(
            res.get("email", "") for res in data["results"] if res.get("email")
        )
        return emails, data, ""
    else:
        return "No emails were generated.", data, ""


def evaluate_from_file(uploaded_file):
    """Evaluate emails by uploading a JSON file to the /evaluations endpoint."""
    if not uploaded_file:
        return "Please upload a JSON file.", None, ""

    file_path = Path(uploaded_file)
    try:
        data = upload_file_to_endpoint("evaluations", file_path)
    except Exception as exc:
        return f"Evaluation failed: {exc}", None, ""

    # Extract prompt technique (if any) from response
    prompt_text = json.dumps(data.get("metric_definitions", {}), indent=2) if data.get("metric_definitions") else ""
    return "", data, prompt_text


def report_from_file(uploaded_file):
    """Generate a report by uploading a JSON file to the /evaluates-report endpoint."""
    if not uploaded_file:
        return "Please upload a JSON evaluation file.", None

    file_path = Path(uploaded_file)
    try:
        data = upload_file_to_endpoint("evaluates-report", file_path)
    except Exception as exc:
        return f"Report generation failed: {exc}", None

    # Save the report locally (optional)
    report_path = OUTPUT_DIR / "evalReport" / f"{file_path.stem}_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    return "Report generated successfully.", data


def build_ui():
    with gr.Blocks(title="Email Generation + Evaluation") as demo:
        gr.Markdown("# Email Generation + Evaluation")

        with gr.Tab("Generate Email"):
            generate_file = gr.File(
                label="Upload JSON File (as accepted by /generates)",
                file_count="single",
                type="filepath",
            )
            generate_btn = gr.Button("Generate Email")
            generated_email = gr.Textbox(label="Generated Email", lines=12)
            generated_json = gr.JSON(label="Generation Response")
            generate_status = gr.Textbox(label="Status", visible=True)

            generate_btn.click(
                fn=generate_from_file,
                inputs=[generate_file],
                outputs=[generated_email, generated_json, generate_status],
            )

        with gr.Tab("Evaluate Email"):
            evaluate_file = gr.File(
                label="Upload JSON File (as accepted by /evaluations)",
                file_count="single",
                type="filepath",
            )
            evaluate_btn = gr.Button("Evaluate Email")
            evaluation_output = gr.JSON(label="Evaluation Result")
            evaluation_prompt = gr.Textbox(label="Prompt Technique", lines=3)
            evaluation_status = gr.Textbox(label="Status", visible=True)

            evaluate_btn.click(
                fn=evaluate_from_file,
                inputs=[evaluate_file],
                outputs=[evaluation_status, evaluation_output, evaluation_prompt],
            )

        with gr.Tab("Generate Report"):
            upload_file = gr.File(
                label="Upload JSON File (as accepted by /evaluates-report)",
                file_count="single",
                type="filepath",
            )
            report_btn = gr.Button("Generate Report")
            report_status = gr.Textbox(label="Status", lines=1)
            report_output = gr.JSON(label="Report Output")

            report_btn.click(
                fn=report_from_file,
                inputs=[upload_file],
                outputs=[report_status, report_output],
            )

    return demo


def main():
    return build_ui()


if __name__ == "__main__":
    build_ui().launch()