# Solar Reporter script
For detail reporting of http://www.dessmonitor.com

Parse details daily data and push them into influx DB
## Install
```shell
docker build -t solar_reporter:latest .
```
## ENV variables
 
| variable          | description               |
|-------------------|---------------------------|
| `INFLUXDB_HOST`   | your influx DB (https...) |
| `INFLUXDB_TOKEN`  | secret token              |
| `INFLUXDB_BUCKET` | name of bucket            |
| `INFLUXDB_ORG`    | org name                  |

## Usage

You can install python dependencies by pip:

```shell
pip install -r requirements.txt
```

and then run `main.py` with all files downloaded from http://www.dessmonitor.com as arguments:

```shell
python main.py *.xlsx
```

OR use docker

```shell
docker run --rm -v `pwd`:/files --env-file .env solar_reporter:latest *.xlsx
```
note: make sure you have correctly filled env variables

## Tests

```shell
docker run --rm -w /app  --entrypoint pytest solar_reporter:latest
```