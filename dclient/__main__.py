import argparse
import paramiko
import os
from tag import TagManager
from sys import platform
from pathlib import Path

import paramiko.client
from client import DockerClient


parser = argparse.ArgumentParser(prog="client", description="docker utils client")

parser.add_argument("-H", "--host", nargs="?", default=argparse.SUPPRESS)
parser.add_argument("-p", "--port", nargs="?", default=argparse.SUPPRESS)
parser.add_argument("-s", "--sock", nargs="?", default=argparse.SUPPRESS)
parser.add_argument(
    "-r",
    "--repo",
    nargs="?",
    default=argparse.SUPPRESS,
    help="repository",
)
parser.add_argument(
    "--docker",
    nargs="?",
    default=argparse.SUPPRESS,
    help="directory contains Dockerfile and/or docker-compose.yml",
)

subparsers = parser.add_subparsers(help="subcommands help", dest="action")


parser_build = subparsers.add_parser("build", help="build and tag an image")

parser_push = subparsers.add_parser("push", help="push compose file")
parser_push.add_argument("-f", "--file", nargs="?", default="docker-compose.yml")
parser_push.add_argument(
    "-d",
    "--dest",
    nargs="?",
    default=argparse.SUPPRESS,
    help="destination host",
)
parser_push.add_argument(
    "-p",
    "--port",
    nargs="?",
    default=argparse.SUPPRESS,
    help="registry port",
)
parser_push.add_argument(
    "-u",
    "--user",
    nargs="?",
    default=argparse.SUPPRESS,
    help="user name",
)

args = parser.parse_args()

default_tag = "latest"

if "repo" not in args:
    raise Exception("require the repo")

if "docker" not in args:
    raise Exception("require the docker directory")

project_dir = Path(args.docker)


if "sock" in args:
    client = DockerClient.unix_sock(args.sock)
elif "host" in args and "port" in args:
    client = DockerClient.tcp(host=args.host, port=args.port)
else:
    if platform == "linux" or platform == "darwin":
        client = DockerClient.unix_sock("/var/run/docker.sock")
    elif platform == "win32":
        client = DockerClient.tcp(host="127.0.0.1", port="2375")
    else:
        raise Exception("either sock or host and port are required")

if args.action == "build":

    tag = f"{args.repo}:{default_tag}"

    resp = client.build(
        path=str(project_dir), quiet=False, rm=True, tag=tag, decode=True
    )
    for line in resp:
        if "stream" in line:
            print(line["stream"])

elif args.action == "push":
    if "dest" not in args:
        raise Exception("destination is required")
    if "port" not in args:
        raise Exception("port is required")

    """
    """

    # save last tag
    tag_mgr = TagManager("http://192.168.0.213:34592/v2/")
    tag_mgr.valid()
    tag_mgr.delete_image("loto7", "latest")
    tag_mgr.delete_image("loto7", "second")
    exit(0)
    tag_mgr.retag("loto7", "latest", "second")

    # retag
    remote_repo = f"{args.dest}:{args.port}/{args.repo}"
    client.tag(args.repo, remote_repo, default_tag)
    resp = client.push(remote_repo, default_tag, stream=True, decode=True)
    for line in resp:
        print(line)

    compose_file = project_dir / "docker-compose.yml"
    if compose_file.is_file():
        print("push docker-compose.yml")
        if "user" not in args:
            raise Exception("user is required")

        sshClient = paramiko.client.SSHClient()
        sshClient.set_missing_host_key_policy(paramiko.RejectPolicy())
        pkey = Path.home() / ".ssh" / "id_ed25519.pub"

        sshClient.connect(
            hostname=args.dest, username=args.user, key_filename=str(pkey)
        )
        ftp = sshClient.open_sftp()
        ftp.put(str(compose_file), f"/home/{args.user}/{args.repo}/docker-compose.yml")
