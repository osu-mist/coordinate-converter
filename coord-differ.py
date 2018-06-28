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

            for differing_feature_id in old_coords_view ^ new_coords_view:
                print differing_feature_id
                if differing_feature_id not in new_coords_view:
                    print "New feature with id: {}".format(differing_feature_id)
                else:
                    print "Deprecated feature with old id: {}".format(differing_feature_id)

            #already in sorted order
            for common_feature_id in old_coords_view & new_coords_view:
                print "Processing id:{}".format(common_feature_id)

                if(old_mapped[common_feature_id] != new_mapped[common_feature_id]):
                    old = old_mapped[common_feature_id]
                    new = new_mapped[common_feature_id]
                    print "Start diffing\n"

                    try:
                        #TODO figure out how to handle missing keys for AIMS_Name
                        if(#old['properties']['AIMS_Name'] != new['properties']['AIMS_Name'] or
                        old['properties']['AiM_Desc'] != new['properties']['AiM_Desc'] or
                        old['properties']['Notes'] != new['properties']['Notes']):
                            print "!!! Feature id {}'s desc and notes have changed!".format(common_feature_id)
                            print "OLD {} - {}".format(#old['properties']['AIMS_Name'],
                                                            old['properties']['AiM_Desc'],
                                                            old['properties']['Notes'])

                            print "NEW {} - {}".format(#new['properties']['AIMS_Name'],
                                                            new['properties']['AiM_Desc'],
                                                            new['properties']['Notes'])
                    except KeyError as e:
                        print "Key Error caught"
                        pass
                    else:
                        print "Location id: {} - {} - {}".format(common_feature_id,
                                                        old['properties']['AiM_Desc'], old['properties']['Notes'])

                    print "\nDiffing fields"
                    #dictdiff geometry and properties dict

                    #diff returns an iterator...
                    geo_diff = list(diff(old['geometry'], new['geometry']))
                    properties_diff = list(diff(old['properties'], new['properties']))

                    print "Properties Differences"
                    print properties_diff
                    print "\nGeometry Differences"
                    print geo_diff

                    import pdb; pdb.set_trace()


