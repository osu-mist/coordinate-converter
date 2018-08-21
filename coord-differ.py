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
import functools

from docopt import docopt
import pprint
#print(docopt(__doc__, version='1.0.0rc2'))

args = docopt(__doc__, version='1.0.0rc2')

def mapFeatToID(json):
    features = {}
    for f in json['features']:
        features[f['id']] = f
    return features

"""
    Diffs two Dict viewkeys, an old dict and new dict, and returns the new keys and removed keys as a pair.
"""
def diff_viewkeys(old_view, new_view):
    new_keys = []
    removed_keys = []
    for differing_key in old_view ^ new_view:
        if differing_key not in new_view:
            removed_keys.append(differing_key)
        else:
            new_keys.append(differing_key)

    return (new_keys, removed_keys)


def reportNewOrRemovedIDs(old_coords_view, new_coords_view):
    new_ids, removed_ids = diff_viewkeys(old_coords_view, new_coords_view)

    print "====================================="
    print "\nNew or missing id's"
    print "# of new features: {}".format(len(new_ids))
    print "# of removed features: {}".format(len(removed_ids))
    if(new_ids):
        print "-------------------------------------"
        print "New features ids:"
        print new_ids
    if(removed_ids):
        print "-------------------------------------"
        print "Deprecated feature ids:"
        print removed_ids
    print "\n====================================="


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

    if(type_change):
        print "!!! Geometry type has changed !!!"
    pprint.pprint(diff)

def argparse_lambda_for_geo_differ():
    if(args['--coord_threshold']):
        thresh = float(args['--coord_threshold'])
        geo_differ = lambda old_geo, new_geo: list(diff(old_geo, new_geo, tolerance=thresh))
    else:
        geo_differ = lambda old_geo, new_geo: list(diff(old_geo, new_geo))
    return geo_differ

"""
    Splits the dictdiffer diff by category: adds, removes, changes
"""
def splitDiffByCategory(diff):
    adds = {}
    removes = {}
    changes = {}
    #repr usage is to handle nested object diffs from throwing TypeError: unhashable type 'list'
    for d in diff:
        if(d[0] == 'change'):
            changes[d[1].__repr__()] = d[2]
        elif(d[0] == 'add'):
            adds[d[1].__repr__()] = d[2]
        elif(d[0] == 'remove'):
            removes[d[1].__repr__()] = d[2]
    return adds, removes, changes

def reportDiff(diff):
    adds, removes, changes = splitDiffByCategory(diff)

    if adds:
        print "Added Attributes:"
        pprint.pprint(adds)

    if removes:
        print "\nRemoved Attributes:"
        pprint.pprint(removes)

    if changes:
        print "\nChanged Atrributes:"
        for key, value in changes.iteritems():
            print "{}: `{}` -> `{}`".format(key, value[0], value[1])

if __name__ == "__main__":
    if(args['<old_data_path>'] == args['<new_data_path>']):
        print >> sys.stderr, "These are the same file..."
        sys.exit(1)
    else:
        with open(args['<old_data_path>'], "r") as old_json_file, open(args['<new_data_path>'], "r") as new_json_file:
            old_coords = json.loads(old_json_file.read())
            new_coords = json.loads(new_json_file.read())

        try:
            geo_differ = argparse_lambda_for_geo_differ()
        except ValueError:
            print >> sys.stderr, "Invalid threshhold value"
            exit(1)

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

            packed_diffs = []  # idx, properties_diff, geo_diff, type_change
            type_change_count = 0
            for common_feature_id in old_coords_view & new_coords_view:  # already in sorted order

                if(old_mapped[common_feature_id] != new_mapped[common_feature_id]):
                    old = old_mapped[common_feature_id]
                    new = new_mapped[common_feature_id]

                    geo_diff = geo_differ(old['geometry'], new['geometry'])

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

            print "Reporting common ids diffs"
            print "{} ids have differences.".format(len(old_coords_view & new_coords_view))
            print "====================================="
            reportIndivDiffs(packed_diffs)