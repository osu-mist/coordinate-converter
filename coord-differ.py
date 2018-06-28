"""
    Usage:
    coord-differ.py <old_data_path> <new_data_path>

    Arguments:
        old_data_path: File path of old building json
        new_data_path: File path of new building json
"""

import sys
import json
from dictdiffer import diff

from docopt import docopt
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
    print "-------------------------------------"
    for f in new_ids:
        print "New feature with id: {}".format(differing_feature_id)
    print "-------------------------------------"
    for f in removed_ids:
        print "Deprecated feature with old id: {}".format(differing_feature_id)
    print "=====================================\n"

def reportDiff(diff):
    adds = {}
    removes = {}
    changes = {}

    print diff
    for d in diff:
        if(d[0] == 'change'):
            adds[d[1]] = d[2]
        elif(d[0] == 'add'):
            removes[d[1]] = d[2]
        elif(d[0] == 'remove'):
            changes[d[1]] = d[2]

    print "$$$ adds"
    for key, value in adds.iteritems():
        print "{}: {} -> {}".format(key, value[0], value[1])
    
    import pdb; pdb.set_trace()
    print "Removes"
    for key, value in removes.iteritems():
        print "{}: {} -> {}".format(key, value[0], value[1])

    print "Changes"
    for key, value in changes.iteritems():
        print "{}: {} -> {}".format(key, value[0], value[1])

if __name__ == "__main__":
    if(args['<old_data_path>'] == args['<new_data_path>']):
        print "These are the same file..."
        sys.exit(1)
    else:
        with open(args['<old_data_path>'], "r") as old_json_file, open(args['<new_data_path>'], "r") as new_json_file:
            old_coords = json.loads(new_json_file.read())
            new_coords  = json.loads(old_json_file.read())

        #if (old_coords_view ^ new_coords_view) != set([]):
        if (old_coords == new_coords):
            #print "There are no differences"
            sys.exit(0)
        else:
            #print "There are differences"
            if(old_coords['crs'] != new_coords['crs']):
                print "Spacial reference has changed from: {} to {}".format(old_coords['crs'], new_coords['crs'])

            old_mapped = mapFeatToID(old_coords)
            new_mapped = mapFeatToID(new_coords)

            old_coords_view = old_mapped.viewkeys()
            new_coords_view = new_mapped.viewkeys()

            reportNewOrRemovedIDs(old_coords_view, new_coords_view)

            print "Processing common ids"
            print "\n====================================="
            for common_feature_id in old_coords_view & new_coords_view: #already in sorted order
                print "Processing id:{}".format(common_feature_id)
                print "-------------------------------------"

                if(old_mapped[common_feature_id] != new_mapped[common_feature_id]):
                    old = old_mapped[common_feature_id]
                    new = new_mapped[common_feature_id]
                    #print "Start diffing\n"

                    try:
                        #TODO figure out how to handle missing keys for AIMS_Name
                        if(old['properties']['AIMS_Name'] != new['properties']['AIMS_Name'] or
                            old['properties']['AiM_Desc'] != new['properties']['AiM_Desc'] or
                            old['properties']['Notes'] != new['properties']['Notes']):

                            print "Feature id {}'s name, desc and notes have changed!".format(common_feature_id)
                            print "OLD: `{}` - `{}` - `{}`".format(old['properties']['AIMS_Name'],
                                                            old['properties']['AiM_Desc'],
                                                            old['properties']['Notes'])

                            print "NEW: `{}` - `{}` - `{}`".format(new['properties']['AIMS_Name'],
                                                            new['properties']['AiM_Desc'],
                                                            new['properties']['Notes'])
                    except KeyError as e:
                        print "Key Error caught"
                        pass

                    print "Location id: {} - {} - {}".format(common_feature_id,
                                                    old['properties']['AiM_Desc'], old['properties']['Notes'])

                    print "\nDiffing fields"
                    #dictdiff geometry and properties dict

                    #diff returns an iterator...
                    #TODO order by add, remove, changes
                    #TODO coordinate floating point threshold cmd option
                    #TODO add ignore type in geometry diff
                    geo_diff = list(diff(old['geometry'], new['geometry']))
                    properties_diff = list(diff(old['properties'], new['properties']))

                    print "Properties Differences"
                    print reportDiff(properties_diff)
                    print "\nGeometry Differences"
                    print reportDiff(geo_diff)
                    print "-------------------------------------"


