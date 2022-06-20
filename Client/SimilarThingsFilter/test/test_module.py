import pytest
from create_app import create_app
from things_module import ThingsModule
import os

ROOT_PATH = os.getcwd().split("things_server")[0].replace(os.sep, '/')


class TestBodyRest:
    paths = [
        os.path.join(ROOT_PATH, "resources/exampleImages/bike.jpg"),
        os.path.join(ROOT_PATH, "resources/exampleImages/lizard2.jpg"),
        os.path.join(ROOT_PATH, "resources/BodyPeople/Face.jpg")
    ]

    pattern_image = os.path.join(ROOT_PATH, "resources/exampleImages/lizard3.jpg")

    @pytest.fixture()
    def app(self):
        app = create_app()
        app.config.update({"TESTING": True})
        yield app

    @pytest.fixture()
    def client(self, app):
        return app.test_client()

    def test_predict_type(self):
        result = ThingsModule.get_images(self.pattern_image, self.paths)
        print(result)
        assert isinstance(result, list)


    def test_get_body_api(self, client):
        body = {"paths": self.paths, "options": {
            "imagePath": self.pattern_image}}

        response = client.post("/", json=body)
        print("Response", response.json)
        assert response.status_code == 200
        assert len(response.json["pictures"]) == 1
