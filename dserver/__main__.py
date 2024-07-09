from flask import Flask, make_response, request
from flask_restful import Api, Resource
from pathlib import Path
from docker.errors import APIError

from dclient.client import DockerClient
import subprocess


app = Flask(__name__)
api = Api(app)

client = DockerClient.unix_sock("/var/run/docker.sock")


class Compose(Resource):
    def post(self):
        data = request.json
        repo = data["repo"]
        compose = data["compose"]

        try:
            resp = client.pull(
                f"localhost:34592/{repo}", tag="latest", stream=True, decode=True
            )
            for line in resp:
                print(line)
        except APIError as e:
            print(f"Error: {e}")

        if compose != "":
            print(f"Compose: ready to up compose: {compose}/docker-compose-yml")
            self.run_compose(compose)
        return make_response({}, 200)

    def run_compose(self, compose):
        try:
            result = subprocess.run(
                "docker compose up -d",
                cwd=Path.home() / compose,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                shell=True,
            )
            result.check_returncode()
            print(result)
        except subprocess.CalledProcessError as e:
            print(f"Error: {e.stdout}")


api.add_resource(Compose, "/docker-compose")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=34594)
