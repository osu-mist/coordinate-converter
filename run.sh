#!/bin/sh
# This is a wrapper script for coordinate-converter to make sure it exists before running it.
while [ ! -f /tmp/coordinate-converter ]
do
  sleep 2
done

/tmp/coordinate-converter -u "$URL"