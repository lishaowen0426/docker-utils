from flask import Flask, make_response, request
from flask_restful import Api, Resource

from dclient.client import DockerClient

# HOST = "localhost"
# PORT = 34592

app = Flask(__name__)
api = Api(app)

client = DockerClient.unix_sock("/var/run/docker.sock")


class Compose(Resource):
    def post(self):
        data = request.json
        repo = data["repo"]
        compose_file = data["compose"]
        print(repo)
        print(compose_file)
        # resp = client.pull(f"${HOST}:${PORT}/repo:latest", stream=True, decode=True)
        # for line in resp:
        #    print(line)
        return make_response({}, 200)


api.add_resource(Compose, "/docker-compose")


if __name__ == "__main__":
    app.run(debug=True)
