from pathlib import Path


class PromptEngine:
    def __init__(self, templates_dir: str):
        self.templates_dir = self._resolve_templates_dir(templates_dir)

    @staticmethod
    def _resolve_templates_dir(templates_dir: str) -> Path:
        path = Path(templates_dir).expanduser()
        if path.is_absolute() and path.exists():
            return path

        project_root = Path(__file__).resolve().parents[2]
        app_root = Path(__file__).resolve().parents[1]
        candidates = [
            path,
            project_root / path,
            app_root / path,
        ]

        if path.parts and path.parts[0] == "data":
            candidates.append(app_root / path)

        for candidate in candidates:
            if candidate.exists():
                return candidate

        return project_root / path

    def _load_template(self, filename: str) -> str:
        template_path = self.templates_dir / filename
        if not template_path.exists():
            raise FileNotFoundError(
                f"Prompt template not found: {template_path}. "
                "Check PROMPT_TEMPLATES_DIR or use app/data/prompt_templates."
            )
        return template_path.read_text(encoding="utf-8").strip()

    def build_prompt(self, intent: str, facts: list[str], tone: str) -> str:
        system = self._load_template("system.txt")
        few_shot = self._load_template("few_shot.txt")
        facts_block = "\n".join(f"- {fact}" for fact in facts)
        user = f"""Intent:
{intent}

Key facts that must be included:
{facts_block}

Tone:
{tone}

Write one complete professional email. Include a concise subject line, greeting,
email body, clear next step when appropriate, and sign-off. Do not mention the
prompt, the technique, or any hidden reasoning."""
        return f"{system}\n\n{few_shot}\n\n{user}"

    @staticmethod
    def technique_summary() -> str:
        return (
            "Role-playing + few-shot prompting: the model is assigned the role "
            "of a senior business communication assistant, shown successful "
            "examples, and given a structured contract for subject, greeting, "
            "body, next step, and sign-off."
        )
