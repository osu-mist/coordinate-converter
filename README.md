# Coordinate Converter
Coordinate Converter is used to convert coordinates from a JSON http response. Specfically, this program is used at OSU with ARCGIS to convert coordinates to latitude and longitude.

### Dependencies

* github.com/paulmach/go.geojson

## Usage

### Run It Locally
This program requires [CS2CS](http://proj4.org/apps/cs2cs.html) and [Golang](https://golang.org) to run locally. 
```
go install
# URL of ARCGIS Json endpoint. Required
URL="www.example.com/arcgisjsonendpoint"

# Path to json output file. If no file path is provided, path will be $PWD/converted-coordinates.json
FILEPATH="/path/to/desired/output.json"
coordinate-converter -u "$URL" [-f "$FILEPATH"]
```

### Run It in Docker
Included is a [docker-compose file](docker-compose.yml) that starts containers for [CS2CS](http://proj4.org/apps/cs2cs.html) and [Golang](https://golang.org) to build the executable. A file called converted-coordinates.json will be created in $PWD when running this command:
```
export URL='www.example.com/arcgisjsonendpoint'
docker-compose up --build
```