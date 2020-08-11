# Delete Trello Archived Cards

This routine allows **batch deletion of all trello archived cards**. This operation [isn't currently made available through Trello's Interface](https://community.atlassian.com/t5/Trello-questions/How-can-i-delete-all-archived-cards/qaq-p/649283)
**WARNING**: this will delete **all your archived cards without distinction** (starting from the most recently archived). Use at your own risk.

## Usage

### 0. Prerequisites

#### Install Docker

This procedure requires [docker](https://docs.docker.com/get-docker/) to be installed on your system

#### get a trello API key and token 

Following [these steps](https://developer.atlassian.com/cloud/trello/guides/rest-api/api-introduction/#:~:text=Authentication%20and%20Authorization,-Trello%20uses%20a&text=You%20can%20get%20your%20API,the%20top%20of%20that%20page.)

#### create credentials file

Add `.trello` file at the root of this repository, containing your credentials in the following format:
```
key=...
token=...
```

### 1. build the docker image

```
docker build . -t delete-trello-archives:latest
```

### 2. run the image

The following command will launch the batch deletion of your trello archived cards.
```
docker run --name trello delete-trello-archives
``

If you wish to get the logs of cards deleted, create a `logs` volume pointing to `/app/logs`:
```
docker run --name trello -v logs:/app/logs delete-trello-archives
docker volume inspect logs ## get absolute path to volume
sudo cat path/to/volume/logs.txt ## dsplay logs
```

### Note

100 requests are sent every 10 seconds to respect [Atlassian's API rate limits](https://developer.atlassian.com/cloud/trello/guides/rest-api/rate-limits/). Therefore this routine allows to delete ~ 600 cards / minute
