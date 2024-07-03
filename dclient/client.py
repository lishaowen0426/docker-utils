import docker


class DockerClient(docker.DockerClient):
    def __init__(self, host=None, port=None, sock=None, dockerfile=None, compose=None):

        if sock is not None:
            connection_str = f"unix://{sock}"
        elif (host is not None) and (port is not None):
            connection_str = f"tcp://{host}:{port}"
        else:
            raise Exception("Either socket or host and port needs to be specified")

        docker.DockerClient.__init__(self, base_url=connection_str)
        self.dockerfile = dockerfile
        self.compose = compose

    @classmethod
    def unix_sock(cls, sock):
        return cls(sock=sock)

    @classmethod
    def tcp(cls, host, port):
        return cls(host=host, port=port)
