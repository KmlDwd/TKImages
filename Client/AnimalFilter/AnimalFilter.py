import json
from detecto import core, utils
from pathlib import Path

class AnimalModule():
    animals = [
        'tiger',
        'elephant',
        'panda'
    ]

    def __init__(self) -> None:
        super().__init__()
        module_path = Path()
        self.model_path = module_path / "model_weights.pth"

    def detect_animals(self, animalSpecies, confidence, paths):
        filtered_paths = []
        for file in paths:
            evaluated_animals = self.detect_animal(file)
            maxVal = max(evaluated_animals.values())
            if max(evaluated_animals, key=evaluated_animals.get) == animalSpecies and maxVal >= confidence:
                filtered_paths.append(file)

        return filtered_paths

    def detect_animal(self, file_path: str):
        print(self.model_path)
        model = core.Model.load(self.model_path, self.animals)
        image = utils.read_image(file_path)

        labels, _, scores = model.predict(image)

        animal_scores = {label: [score for i, score in enumerate(scores)
                                 if labels[i] == label] for label in set(labels)}

        return {label: round(float(max(animal_scores[label])) * 100) for label in animal_scores}


def process_request(body):
    body = json.loads(body)
    params = body["params"]

    result = AnimalModule().detect_animals(paths=body["paths"],
                           animalSpecies=params["species"], confidence=params["confidence"])
    return result
