import argparse
import os
from pathlib import Path
from sys import platform

import paramiko
import paramiko.client

from dclient.client import DockerClient
from dclient.tag import TagManager

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
parser_build.add_argument("--platform", nargs="?", default="linux/amd64")

parser_push = subparsers.add_parser("push", help="push compose file")
parser_push.add_argument("-f", "--file", nargs="?", default="docker-compose.yml")
parser_push.add_argument(
    "-d",
    "--dest",
    nargs="?",
    default="192.168.0.213",
    help="destination host",
)
parser_push.add_argument(
    "-p",
    "--port",
    nargs="?",
    default=34592,
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


def find_pub_key():
    p = Path.home() / ".ssh"
    for d in os.listdir(p):
        if d.endswith(".pub"):
            return d

    raise Exception("cannot find public key")


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
        sock_fd = Path("/var/run/docker.sock")
        if not sock_fd.exists():
            raise Exception("/var/run/docker.sock does not exist")
        client = DockerClient.unix_sock("/var/run/docker.sock")
    elif platform == "win32":
        raise Exception("Windows is unsupported")
    else:
        raise Exception("either sock or host and port are required")

if args.action == "build":

    tag = f"{args.repo}:{default_tag}"

    resp = client.build(
        path=str(project_dir),
        quiet=False,
        rm=True,
        tag=tag,
        decode=True,
        platform=args.platform,
    )
    for line in resp:
        if "stream" in line:
            print(line["stream"])

elif args.action == "push":
    if "dest" not in args:
        raise Exception("destination is required")
    if "port" not in args:
        raise Exception("port is required")

    # save last tag
    tag_mgr = TagManager("http://192.168.0.213:34592/v2/")
    tag_mgr.valid()

    tag_mgr.retag("loto7", "latest", "second")

    # retag
    remote_repo = f"{args.dest}:{args.port}/{args.repo}"
    client.tag(args.repo, remote_repo, default_tag)
    resp = client.push(remote_repo, default_tag, stream=True, decode=True)
    for line in resp:
        print(line)

    compose_file = project_dir / "docker-compose.yml"
    if compose_file.is_file():
        print(f"push docker-compose.yml: {compose_file}")
        if "user" not in args:
            raise Exception("user is required")

        sshClient = paramiko.client.SSHClient()
        sshClient.load_system_host_keys()
        sshClient.set_missing_host_key_policy(paramiko.RejectPolicy())

        pkey = Path.home() / ".ssh" / find_pub_key()

        sshClient.connect(
            hostname=args.dest, username=args.user, key_filename=str(pkey)
        )
        ftp = sshClient.open_sftp()
        ftp.put(str(compose_file), f"{args.repo}/docker-compose.yml")
