package main

import (
        "net/http"
        "io/ioutil"
        "os/exec"
        "encoding/json"
        "strconv"
        "bytes"
        "strings"
        "os"
        "fmt"
        "flag"
        "github.com/paulmach/go.geojson"
    )
/*
Represents a subset of fields from an ARCGIS API response.
*/
type Buildings struct {
    Features []struct {
        Attributes struct {
            BldID string `json:"BldID"`
            BldNam string `json:"BldNam"`
        } `json:"attributes"`
        Geometry struct {
            Rings [][][]float64 `json:"rings"`
        } `json:"geometry"`
    } `json:"features"`
}

/*
Make http request and unmarshals json respones into Buildings struct
*/
func getBuildings(url string) (*geojson.FeatureCollection, *geojson.FeatureCollection) {
    // Make http request to ARCGIS API
    res, err := http.Get(url)
    check(err)

    // Read body of API response
    body, err := ioutil.ReadAll(res.Body)
    res.Body.Close()
    check(err)

    // Unmarshal json into buildings struct
    buildings := geojson.NewFeatureCollection()
    err = json.Unmarshal(body, buildings)
    check(err)

    convertedBuildings := geojson.NewFeatureCollection()
    err = json.Unmarshal(body, convertedBuildings)
    check(err)

    return buildings, convertedBuildings
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

    cs2csCommand := "echo \"" + lonStr + " " + latStr + "\" | cs2cs -f %8.6f +proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=10.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs +to +proj=longlat +datum=WGS84 +no_defs"
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
func coordinateIterator(buildings *geojson.FeatureCollection, convertedBuildings *geojson.FeatureCollection) {
    // Iterate over each coordinate pair and convert coordinates using convertCoordinates()
    for featureIndex, building := range buildings.Features {
        fmt.Println("Converting building", building.Properties["BldNam"])
        if building.Geometry.Type == "Polygon" {
            for ringIndex, ring := range building.Geometry.Polygon {
                for coordPairIndex, coordpair := range ring {
                    convertedLon, convertedLat := convertCoordinates(coordpair[0], coordpair[1])

                    // Reassign coordinate values to the converted coordinates
                    convertedBuildings.Features[featureIndex].Geometry.Polygon[ringIndex][(len(ring) - 1) - coordPairIndex][0] = convertedLon
                    convertedBuildings.Features[featureIndex].Geometry.Polygon[ringIndex][(len(ring) - 1) - coordPairIndex][1] = convertedLat
                }
            }
        } else if building.Geometry.Type == "MultiPolygon" {
            fmt.Println("Todo: Handle MultiPolygon")
        }
    }
}

/*
Marshal buildings struct to json and write to file
*/
func writeBuildingstoJson(buildings *geojson.FeatureCollection, filePath string) {
    convertedJson, err := json.Marshal(buildings)
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

    buildings, convertedBuildings := getBuildings(*url)

    coordinateIterator(buildings, convertedBuildings)

    writeBuildingstoJson(convertedBuildings, *filePath)
}