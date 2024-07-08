#!/bin/zsh

export PATH="$(pwd)/.venv/bin:$PATH"

app="python3 -m dclient "



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
        u)
            user=$OPTARG
            echo "user: $user"
            ;; 
        \?)
            echo "invalid option"
            exit 1
            ;;
    esac
done

eval "$app -r $repo --docker $dockerfile build" 
eval "$app -r $repo --docker $dockerfile push -u $user" 
