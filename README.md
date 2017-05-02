# Coordinate Converter
Coordinate Converter is used to convert coordinates from a JSON http response. Specfically, this program is used at OSU with ARCGIS to convert coordinates to latitude and longitude.

## Usage

### Run It Locally
This program requires [CS2CS](http://proj4.org/apps/cs2cs.html) and [Golang](https://golang.org) to run locally.
```
go install
URL="www.example.com/arcgisjsonendpoint"
FILEPATH="/path/to/desired/output.json"
coordinate-converter "$URL" "$FILEPATH"
```

### Run It in Docker
Included is a [Dockerfile](Dockerfile) that contains a runtime environment for [CS2CS](http://proj4.org/apps/cs2cs.html) and [Golang](https://golang.org).
```
docker build -t coordinate-converter .
URL="www.example.com/arcgisjsonendpoint"
FILEPATH="/path/to/desired/output.json"
docker run --rm \
    -v "$FILEPATH":"$FILEPATH" \
    -e "FILEPATH=$FILEPATH" \
    -e "URL=$URL" \
    coordinate-converter
```