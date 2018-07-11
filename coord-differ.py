"""
    Usage:
    coord-differ.py <old_data_path> <new_data_path>
    coord-differ.py <old_data_path> <new_data_path> --coord_threshold=<threshold>

    Arguments:
        old_data_path: File path of old building json
        new_data_path: File path of new building json
    
    Options:
        --coord_threshold=<threshold>   Floating point difference threshold for reporting changed coordinate values
"""

import sys
import json
from dictdiffer import diff

from docopt import docopt
import pprint
#print(docopt(__doc__, version='1.0.0rc2'))

args = docopt(__doc__, version='1.0.0rc2')


def mapFeatToID(json):
    features = {}
    for f in json['features']:
        features[f['id']] = f
    return features


def reportNewOrRemovedIDs(old_coords_view, new_coords_view):
    new_ids = []
    removed_ids = []

    for differing_feature_id in old_coords_view ^ new_coords_view:
        if differing_feature_id not in new_coords_view:
            removed_ids.append(differing_feature_id)
        else:
            new_ids.append(differing_feature_id)

    print "====================================="
    print "New or missing id's"
    print "# of new features: {}".format(len(new_ids))
    print "# of removed features: {}".format(len(removed_ids))
    if(new_ids):
        print "-------------------------------------"
        print "New features ids:"
        print new_ids
        #pprint.pprint(new_ids)
    if(removed_ids):
        print "-------------------------------------"
        print "Deprecated feature ids:"
        print removed_ids
        #pprint.pprint(removed_ids)
    print "====================================="


def reportIndivDiffs(packed_diffs):
    for (common_feature_id, properties_diff, geo_diff, type_change) in packed_diffs:
        if(properties_diff or geo_diff):
            print "\nID:{}".format(common_feature_id)
            print "-------------------------------------"
            if(properties_diff):
                print "Properties Differences"
                reportDiff(properties_diff)
            if(geo_diff):
                if(properties_diff):
                    print ""
                print "Geometry Differences"
                if(args['--coord_threshold']):
                    reportGeoDiff(geo_diff, type_change, tolerance=float(
                        args['--coord_threshold']))
                else:
                    reportGeoDiff(geo_diff, type_change)
            print "-------------------------------------"


def reportGeoDiff(diff, type_change, tolerance=None):
    if(tolerance):
        print "These are the coordinates that have changed past the tolerance of {}".format(tolerance)
    else:
        print "These are ALL the changes in the coordinates"

    # print diff
    # for d in diff:
    #    print d
    if(type_change):
        print "!!! Geometry type has changed !!!"
    pprint.pprint(diff)


def reportDiff(diff):
    adds = {}
    removes = {}
    changes = {}

    # print diff
    for d in diff:
        if(d[0] == 'change'):
            changes[d[1]] = d[2]
        elif(d[0] == 'add'):
            adds[d[1]] = d[2]
        elif(d[0] == 'remove'):
            removes[d[1]] = d[2]

    if adds:
        print "Added Attributes:"
        # for key, value in adds.iteritems():
        #    print "{}: `{}`".format(key, value)

        pprint.pprint(adds)

    # TODO finish reporting layout
    if removes:
        print "\nRemoved Attributes:"
        # for key, value in removes.iteritems():
        #    print "{}: `{}`".format(key, value)
        pprint.pprint(removes)

    if changes:
        print "\nChanged Atrributes:"
        for key, value in changes.iteritems():
            print "{}: `{}` -> `{}`".format(key, value[0], value[1])
        # pprint.pprint(changes)


if __name__ == "__main__":
    if(args['<old_data_path>'] == args['<new_data_path>']):
        print "These are the same file..."
        sys.exit(1)
    else:
        with open(args['<old_data_path>'], "r") as old_json_file, open(args['<new_data_path>'], "r") as new_json_file:
            old_coords = json.loads(new_json_file.read())
            new_coords = json.loads(old_json_file.read())

        # if (old_coords_view ^ new_coords_view) != set([]):
        if (old_coords == new_coords):
            # print "There are no differences"
            sys.exit(0)
        else:
            # print "There are differences"
            if(old_coords['crs'] != new_coords['crs']):
                print "Spacial reference has changed from: {} to {}".format(old_coords['crs'], new_coords['crs'])

            old_mapped = mapFeatToID(old_coords)
            new_mapped = mapFeatToID(new_coords)

            old_coords_view = old_mapped.viewkeys()
            new_coords_view = new_mapped.viewkeys()

            reportNewOrRemovedIDs(old_coords_view, new_coords_view)

            packed_diffs = []  # idx, properties_diff, geo_diff
            type_change_count = 0
            for common_feature_id in old_coords_view & new_coords_view:  # already in sorted order

                if(old_mapped[common_feature_id] != new_mapped[common_feature_id]):
                    old = old_mapped[common_feature_id]
                    new = new_mapped[common_feature_id]

                    if(args['--coord_threshold']):
                        geo_diff = list(diff(old['geometry'], new['geometry'], tolerance=float(
                            args['--coord_threshold'])))
                    else:
                        geo_diff = list(diff(old['geometry'], new['geometry']))

                    try:
                        if(old['geometry']['type'] != new['geometry']['type']):
                            type_change = True;
                            type_change_count += 1
                        else:
                            type_change = False;
                    except TypeError:
                        #OCEANOGRAPHY SHOPS COMPLEX LOT was an example of a feature previously lacking the Geometry so this comparison on type would fail
                        if(old['geometry'] != new['geometry']):
                            type_change = True;
                        else:
                            type_change = False;


                    properties_diff = list(
                        diff(old['properties'], new['properties']))

                    packed_diffs.append(
                        (common_feature_id, properties_diff, geo_diff, type_change))

            if(type_change_count):
                print "{} id's have changed geometry types".format(type_change_count)

            print "====================================="
            print "Reporting common ids diffs"
            print "====================================="
            reportIndivDiffs(packed_diffs)