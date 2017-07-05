# Coordinate Converter
Coordinate Converter is used to convert coordinates from a JSON http response. Specfically, this program is used at OSU with ARCGIS to convert coordinates to latitude and longitude.

### Coordinate System
This program is meant to convert coordinates for locations at Oregon State University.
As such, the coordinate projections we are accepting are either:

NAD_1983_HARN_StatePlane_Oregon_North_FIPS_3601_Feet_Intl
WKID: 2913 Authority: EPSG

or

WGS_1984_Web_Mercator_Auxiliary_Sphere
WKID: 3857 Authority: EPSG

Accepting both coordinate types is a temporary feature that will soon be deprecated after all coordinates given from ARCGIS are NAD_1983 (WKID 2913).

All coordinates are converted to the WGS84 projection.

### Dependencies

* [github.com/paulmach/go.geojson](https://github.com/paulmach/go.geojson)

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