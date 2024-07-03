import argparse
import paramiko
import os
from sys import platform

import paramiko.client
from client import DockerClient


parser = argparse.ArgumentParser(prog="client", description="docker utils client")

parser.add_argument("-H", "--host", nargs="?", default=argparse.SUPPRESS)
parser.add_argument("-p", "--port", nargs="?", default=argparse.SUPPRESS)
parser.add_argument("-s", "--sock", nargs="?", default=argparse.SUPPRESS)

subparsers = parser.add_subparsers(help="subcommands help", dest="action")


parser_build = subparsers.add_parser("build", help="build and tag an image")
parser_build.add_argument("-f", "--file", nargs="?", default="Dockerfile")
parser_build.add_argument("-t", "--tag", nargs="?", default="latest")
parser_build.add_argument(
    "-r",
    "--repo",
    nargs="?",
    default=argparse.SUPPRESS,
    help="repo in the form host:port/repository or repository",
)

parser_push = subparsers.add_parser("push", help="push compose file")
parser_push.add_argument("-f", "--file", nargs="?", default="compose.yaml")
parser_push.add_argument(
    "-d",
    "--dest",
    nargs="?",
    default=argparse.SUPPRESS,
    help="destination location is the form user@host:path, note that the file name should be included",
)


args = parser.parse_args()

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
    if "repo" not in args:
        raise Exception("build requires the repo")

    tag = f"{args.repo}:{args.tag}"

    image, _ = client.images.build(path=args.file, quiet=False, rm=True, tag=tag)

    client.images.push(repository=args.repo, tag={args.tag})
elif args.action == "push":
    if "dest" not in args:
        raise Exception("destination is required")

    sshClient = paramiko.client.SSHClient()
    sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sshClient.connect(hostname="192.168.0.213", username="ty001", password="Info2022.")
    ftp = sshClient.open_sftp()
    ftp.put(args.file, args.dest)
