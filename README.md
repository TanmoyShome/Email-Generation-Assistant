# Email Generation Assistant

FastAPI + Gradio prototype that generates professional emails from three inputs:
intent, key facts, and tone.

## Prompt Engineering Technique

The app uses role-playing plus few-shot prompting. The system prompt assigns the
model the role of a senior business communication assistant, `few_shot.txt`
shows high-quality examples, and the final prompt gives a structured output
contract: subject line, greeting, body, next step, and sign-off.

## Custom Evaluation Metrics

- `fact_coverage`: checks whether each requested key fact is represented in the email.
- `tone_alignment`: scores simple tone markers for formal, casual, urgent, and empathetic styles.
- `professional_structure`: checks subject, greeting, polite language, sign-off, and concise length.
- `overall`: average of the custom metric scores.

## Run

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="your_api_key"
uvicorn app.main:app --reload
```

Open:

- Gradio UI: `http://127.0.0.1:8000/gradio`
- API docs: `http://127.0.0.1:8000/docs`

## API

Generate:

```http
POST /api/v1/emails/generate
```

```json
{
  "intent": "Follow up after meeting",
  "key_facts": ["Met on Tuesday", "Discussed proposal timeline", "Send pricing by Friday"],
  "tone": "formal and courteous"
}
```

Evaluate:

```http
POST /api/v1/emails/evaluate
```
