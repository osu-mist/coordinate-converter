package main

import (
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"os/exec"
	"strconv"
	"strings"

	"github.com/paulmach/go.geojson"
)

/*
Make http request and unmarshals json respones into Features struct
*/
func getFeatures(url string) (*geojson.FeatureCollection, *geojson.FeatureCollection) {
	// Make http request to ARCGIS API
	res, err := http.Get(url)
	check(err)

	// Read body of API response
	body, err := ioutil.ReadAll(res.Body)
	res.Body.Close()
	check(err)

	// Unmarshal json into Features struct
	features := geojson.NewFeatureCollection()
	err = json.Unmarshal(body, features)
	check(err)

	convertedFeatures := geojson.NewFeatureCollection()
	err = json.Unmarshal(body, convertedFeatures)
	check(err)

	return features, convertedFeatures
}

/*
Simple error checking function.
*/
func check(e error) {
	if e != nil {
		panic(e)
	}
}

/*
Converts a set of coordinates using cs2cs. http://proj4.org/apps/cs2cs.html
*/
func convertCoordinates(lon, lat float64) (float64, float64) {
	// The coordinates are floats, so we must convert them into strings to include them in the cs2cs command
	lonStr := strconv.FormatFloat(lon, 'f', -1, 64)
	latStr := strconv.FormatFloat(lat, 'f', -1, 64)

	var cs2csProjection string

	cs2csProjection = "+proj=lcc +lat_1=46 +lat_2=44.33333333333334 +lat_0=43.66666666666666 +lon_0=-120.5 +x_0=2500000.0001424 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=ft +no_defs"

	cs2csCommand := "echo \"" + lonStr + " " + latStr + "\" | cs2cs -f %8.6f " + cs2csProjection + " +to +proj=longlat +datum=WGS84 +no_defs"
	cmd := exec.Command("sh", "-c", cs2csCommand)
	stdoutStderr, err := cmd.CombinedOutput()
	check(err)

	// Cs2cs outputs coordinates separated by random amounts of whitespace, with a 0 value at the end.
	// strings.Fields parses the 3 numbers so we can use them individually (and ignore the unneeded 0).
	parsedOutput := strings.Fields(string(stdoutStderr[:]))

	convertedLon, err := strconv.ParseFloat(parsedOutput[0], 64)
	check(err)
	convertedLat, err := strconv.ParseFloat(parsedOutput[1], 64)
	check(err)

	return convertedLon, convertedLat
}

/*
Iterate over each coordinate and reassign coordinates to converted values
*/
func coordinateIterator(features *geojson.FeatureCollection, convertedFeatures *geojson.FeatureCollection) {
	// Iterate over each coordinate pair and convert coordinates using convertCoordinates()
	for featureIndex, feature := range features.Features {
		fmt.Println("Converting feature coordinates", feature.Properties["OBJECTID"])

		if feature.Properties["Cent_Lon"] != nil && feature.Properties["Cent_Lat"] != nil {
			convertedCentroidLon, convertedCentroidLat := convertCoordinates(feature.Properties["Cent_Lon"].(float64), feature.Properties["Cent_Lat"].(float64))

			convertedFeatures.Features[featureIndex].Properties["Cent_Lon"] = convertedCentroidLon
			convertedFeatures.Features[featureIndex].Properties["Cent_Lat"] = convertedCentroidLat

		}

		if feature.Geometry.Type == "Polygon" {
			for ringIndex, ring := range feature.Geometry.Polygon {
				for coordPairIndex, coordpair := range ring {
					convertedLon, convertedLat := convertCoordinates(coordpair[0], coordpair[1])

					// Reassign coordinate values to the converted coordinates
					convertedFeatures.Features[featureIndex].Geometry.Polygon[ringIndex][(len(ring)-1)-coordPairIndex][0] = convertedLon
					convertedFeatures.Features[featureIndex].Geometry.Polygon[ringIndex][(len(ring)-1)-coordPairIndex][1] = convertedLat
				}
			}
		} else if feature.Geometry.Type == "MultiPolygon" {
			for polygonIndex, polygon := range feature.Geometry.MultiPolygon {
				for ringIndex, ring := range polygon {
					for coordPairIndex, coordpair := range ring {
						convertedLon, convertedLat := convertCoordinates(coordpair[0], coordpair[1])

						// Reassign coordinate values to the converted coordinates
						convertedFeatures.Features[featureIndex].Geometry.MultiPolygon[polygonIndex][ringIndex][(len(ring)-1)-coordPairIndex][0] = convertedLon
						convertedFeatures.Features[featureIndex].Geometry.MultiPolygon[polygonIndex][ringIndex][(len(ring)-1)-coordPairIndex][1] = convertedLat
					}
				}
			}
		} else if feature.Geometry.Type == "Point" {
			convertedLon, convertedLat := convertCoordinates(feature.Geometry.Point[0], feature.Geometry.Point[1])

			convertedFeatures.Features[featureIndex].Geometry.Point[0] = convertedLon
			convertedFeatures.Features[featureIndex].Geometry.Point[1] = convertedLat
		}
	}
}

/*
Marshal features struct to json and write to file
*/
func writeFeaturestoJson(features *geojson.FeatureCollection, filePath string) {
	convertedJson, err := json.Marshal(features)
	check(err)

	var prettyJson bytes.Buffer

	// Pretty print it into prettyJson
	err = json.Indent(&prettyJson, convertedJson, "", "\t")
	check(err)

	// Write pretty json to file
	err = ioutil.WriteFile(filePath, prettyJson.Bytes(), 0644)
	check(err)
}

func main() {
	url := flag.String("u", "", "URL of ARCGIS json endpoint")
	filePath := flag.String("f", "converted-coordinates.json", "Filepath of json output file. Example: \"/directory/file.json\"")
	flag.Parse()

	if *url == "" {
		fmt.Println("No url specified. Use the \"-u\" flag to specify an ARCGIS Json url")
		os.Exit(1)
	}

	features, convertedFeatures := getFeatures(*url)

	coordinateIterator(features, convertedFeatures)

	writeFeaturestoJson(convertedFeatures, *filePath)
}
