import pytest
from create_app import create_app
from animal_module import AnimalModule
import os
ROOT_PATH = os.getcwd().split("animal_server")[0].replace(os.sep, '/')


class TestAnimalRest:
    paths = [
        os.path.join(ROOT_PATH, "resources/Animals/tiger.jpg"),
        os.path.join(ROOT_PATH, "resources/Animals/elephant.jpg"),
        os.path.join(ROOT_PATH, "resources/Animals/panda.jpg")
    ]

    animal = 'tiger'

    @pytest.fixture()
    def app(self):
        app = create_app()
        app.config.update({"TESTING": True})
        yield app

    @pytest.fixture()
    def client(self, app):
        return app.test_client()

    def test_detect_tiger(self):
        self.animal = 'tiger'
        result = AnimalModule().detect_animal(self.paths[0])
        assert max(result, key=result.get) == self.animal

    def test_detect_elephant(self):
        self.animal = 'elephant'
        result = AnimalModule().detect_animal(self.paths[1])
        assert max(result, key=result.get) == self.animal

    def test_detect_panda(self):
        self.animal = 'panda'
        result = AnimalModule().detect_animal(self.paths[2])
        assert max(result, key=result.get) == self.animal

    def test_get_animal_api(self, client):
        body = {"paths": self.paths, "options": {
            "animalSpecies": self.animal}}
        response = client.post("/", json=body)
        print("Response", response.json)
        assert response.status_code == 200
        assert len(response.json["pictures"]) == 1
        assert response.json["pictures"][0] == self.paths[0]
