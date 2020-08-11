#!/bin/sh
docker rm $(docker ps -aq)
docker build . -t delete-trello-archives:latest
