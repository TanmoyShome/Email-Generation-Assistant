class Orchestrator:
    def __init__(self, model_client, evaluator, data_loader, prompt_engine):
        self.model_client = model_client
        self.evaluator = evaluator
        self.data_loader = data_loader
        self.prompt_engine = prompt_engine

    def run(self) -> List[Dict]:
        results = []
        for scenario in self.data_loader.get_all_scenarios():
            prompt = self.prompt_engine.build_prompt(...)
            generated = self.model_client.generate(prompt)
            scores = self.evaluator.evaluate(generated, scenario)
            results.append({...})
        return results