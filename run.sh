#!/bin/zsh
set -e

export PATH="$(pwd)/.venv/bin:$PATH"
export PYTHONPATH="$(pwd):$PYTHONPATH"

HOST=192.168.0.213
PORT=34592
TAG=latest

while getopts "hr:d:u:" flag; do
    case $flag in
        h)
            echo "-d dockerfile/compose directory"
            echo "-r repository"
            echo "-u remote user"
            exit 0
            ;;
        r)
            repo=$OPTARG
            echo "repo: $repo"
            ;;
        d)
            dockerfile=$OPTARG
            echo "Dockerfile projectory: $dockerfile"
            ;;
        \?)
            echo "invalid option"
            exit 1
            ;;
    esac
done


cd "${dockerfile}"

docker build --platform linux/amd64 -t "${repo}:${TAG}" -f $dockerfile/Dockerfile . 
docker image tag "${repo}:${TAG}" "$HOST:$PORT/${repo}:${TAG}" 
echo "retag image from ${repo}:${TAG} to ${repo}:second..."
python3 -m dclient -r ${repo} retag
docker push  "$HOST:$PORT/${repo}:latest" 

DOCKER_COMPOSE=""
if [ -f "${dockerfile}/docker-compose.yml" ]; then
    echo "push docker-compose.yml"
    scp ${dockerfile}/docker-compose.yml hpe:${repo}/docker-compose.yml
    DOCKER_COMPOSE="${repo}/docker-compose.yml"
fi


curl -d "{\"repo\":\"${repo}\", \"compose\":\"${DOCKER_COMPOSE}\"}" -H "Content-Type: application/json" -X POST http://localhost:5000/docker-compose
