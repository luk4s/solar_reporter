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
| `DESS_SECRET`     | secret  of `dessmonitor`  |
| `DESS_TOKEN`      | api token of `dessmonitor`|
| `DESS_PN`         | get from dessmonitor      |
| `DESS_SN`         | get from dessmonitor      |
| `DESS_DEVCODE`    | unique code of monitored dev |
| `DESS_DEVADDR`    | code of address of device |

## Usage

You can install python dependencies by pip:

```shell
pip install -r requirements.txt
```

and then run `main.py` with *dates for downloaded report from http://www.dessmonitor.com:

```shell
python main.py report YYYY-mm-dd YYYY-mm-dd
```

OR use docker

```shell
docker run --rm -v `pwd`:/files --env-file .env solar_reporter:latest report YYYY-mm-dd YYYY-mm-dd
```
note: make sure you have correctly filled env variables

### use API of DESS
First you need obtaion `secret` and `token` from https://dessmonitor.com.

```javascript
const secret = sessionStorage.getItem("secret")
const token = sessionStorage.getItem("token")
alert(`DESS_SECRET="${secret}"\nDESS_TOKEN="${token}"\n`)
```

Then put it into `.env` file. Tokens expires in 7.days => then need obtain again manually from browser after loggin.

@see http://api.dessmonitor.com/chapter1/QuickStart.htmlg
## Tests

```shell
docker run --rm -w /app  --entrypoint pytest solar_reporter:latest
```