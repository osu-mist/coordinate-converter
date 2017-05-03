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
Included is a [docker-compose file](docker-compose.yml) that starts containers for [CS2CS](http://proj4.org/apps/cs2cs.html) and [Golang](https://golang.org) to build the executable. A file called converted-coordinates.json will be created in $PWD when running this command:
```
export URL='www.example.com/arcgisjsonendpoint'
docker-compose up
```