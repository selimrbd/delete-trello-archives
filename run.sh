#!/bin/sh
docker run --name trello -v logs:/app/logs delete-trello-archives
