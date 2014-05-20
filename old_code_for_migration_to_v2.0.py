from pymongo import MongoClient
from eve import Eve

app = Eve()

# Setup the client (but this is already in Eve?)
# Using the main db:
# mongourl = 'mongodb://' + os.getenv('MONGO_USERNAME') + ':' + \
#     os.getenv('MONGO_PASSWORD') + '@' + os.getenv('MONGO_HOST') + \
#     ':' + os.getenv('MONGO_PORT') + '/' + os.getenv('MONGO_DBNAME')

# Using the migration db:
mongourl = 'mongodb://' + 'development:UYp6WKK824TkF@' + \
    'candidate.0.mongolayer.com:10498/pulsepod'

msg = "ALERT: DO MIGRATION?"
DO_IT = True if raw_input("%s (y/N) " % msg).lower() == 'y' else False

if not DO_IT:
    print "RUNNING TRIAL MIGRATION"

print mongourl
log = open('migration.log', 'w')

client = MongoClient(mongourl)

# Assign the databases we need for migration:
db = client.pulsepod

for pod in db.pods.find():
    print "MIGRATING POD: " + pod['name'] + "\t\t[DO IT: " + str(DO_IT) + "]"
    log.write("MIGRATING POD: " + pod['name'] +
              "\t\t[DO IT: " + str(DO_IT) + "]\n")
    # Does this pod already have a notebook?
    if '_notebook' not in pod.keys():
        log.write("Need to add a notebook for this pod.\n")
        log.write("\tAdding pod's _id to notebook's _id_pod...\n")
        if DO_IT:
            db.pods_notebooks.insert(
                {'_id_pod': pod['_id']})
        log.write("\tUpdating the pod _notebook to 1...\n")
        if DO_IT:
            db.pods.update(
                {'_id': pod['_id']},
                {'$set': {'_notebook': 0}})
    # First, extract schema to conform to new version:
    for item in app.config['DOMAIN']['pods']['schema']:
        item_schema = app.config['DOMAIN']['pods']['schema'][item]
        if item in pod.keys():
            log.write("Pod already has " + item + "\n")
        else:
            log.write("Updating pod/notebook to include " + item + "\n")
            if 'default' in item_schema.keys():
                if not item_schema['versioned']:
                    log.write("\tSetting " + item + " to " +
                              str(item_schema['default']) + " in pod\n")
                    if DO_IT:
                        db.pods.update(
                            {'_id': pod['_id']},
                            {'$set': {item: str(item_schema['default'])}})
                if item_schema['versioned']:
                    log.write("Need to set value in pods_notebooks\n")
                    log.write("\tSetting " + item + " to " +
                              str(item_schema['default']) +
                              " in pod's notebook\n")
                    # check for pods_notebooks:
                    if DO_IT:
                        db.pods.update(
                            {'_id': pod['_id']},
                            {'$set': {item: str(item_schema['default'])}})
            elif item_schema['type'] is 'dict':
                for sub_item in item_schema['schema']:
                    sub_item_schema = item_schema['schema'][sub_item]
                    if 'default' in sub_item_schema.keys():
                        log.write("\tSetting " + sub_item + " to " +
                                  str(sub_item_schema['default']) +
                                  " in pod\n")
                        if DO_IT:
                            db.pods.update(
                                {'_id': pod['_id']},
                                {'$set':
                                    {item + '.' + sub_item:
                                        str(sub_item_schema['default'])}})
            else:
                log.write("\t" + item + " does not have a default value...\n")

for pod in db.pods.find():
    if 'notebook' in pod.keys():
        log.write("Migrating data from notebooks to pods_notebooks\n")
        old_notebook = db.notebooks.find_one({'_id': pod['notebook']})
        # print old_notebook
        this_name = old_notebook['name']
        this_lat = old_notebook['latlon']['lat']
        this_lon = old_notebook['latlon']['lon']
        log.write("\tUpdating _notebook nbk_name to " + this_name + "\n")
        log.write("\tUpdating _notebook lat to " + str(this_lat) + "\n")
        log.write("\tUpdating _notebook lon to " + str(this_lon) + "\n")
        if DO_IT:
            db.pods.update(
                {'_id': pod['_id']},
                {'$set': {
                    'nbk_name': this_name,
                    'location.lng': this_lon,
                    'location.lat': this_lat
                }})
    else:
        log.write("Pod " + pod['name'] +
                  " does not have an entry in notebooks\n")

for pod in db.pods.find():
    # Do Data stuff:
    coordinates = [pod['location']['lng'], pod['location']['lat']]
    log.write("\tSetting all data for this notebook to " +
              str(coordinates) + "\n")
    data_loc = {"type": "Point", "coordinates": coordinates}
    this_pod = {'_id': pod['_id'], '_notebook': 0}
    if DO_IT:
        db.data.update(
            {'p': pod['name']},
            {'$set': {'loc': data_loc}},
            multi=True)
    log.write("\tRemoving notebook entries from this pod's data\n")
    if DO_IT:
        db.data.update(
            {'p': pod['name']},
            {'$unset': {'notebook': ""}})
    # Update all data records for this pod:
        log.write("Setting all data pod entries to " + str(this_pod) + "\n")
        if DO_IT:
            db.data.update(
                {'p': pod['name']},
                {'$set': {'pod': this_pod}},
                multi=True)
    else:
        log.write("WARNING: COULD NOT FIND pods_notebooks with _pod_id: "
                  + str(pod['_id']) + "\n")

# Remove any non-meta fields from the pod:
for pod in db.pods.find():
    for item in pod.keys():
        if item not in ['_updated', '_notebook', '_id', '_created']:
            if item not in app.config['DOMAIN']['pods']['schema'].keys():
                log.write(item + " is not supposed to be in pods.\n")
                log.write("\tremoving " + item + " from pod\n")
                if DO_IT:
                    db.pods.update(
                        {'_id': pod['_id']},
                        {'$unset': {item: ""}})
