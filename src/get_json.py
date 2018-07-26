import requests
import logging
import json

#from datPython import Dat
#import datpy
import pandas as pd
import glob, os
import datetime
import re
import yaml

#%%
#dat = datpy.Dat()
#r = dat.download(BASE_URL, 'data')
#print(r)

#datetime.datetime.now().isoformat()
 
#%% IO
LOCAL_PROJECT_PATH = glob.glob(os.path.expanduser('~/git/gardenstate'))[0]
assert os.path.exists(LOCAL_PROJECT_PATH)
LOCAL_DATA_PATH = os.path.join(LOCAL_PROJECT_PATH,'DATA')
assert os.path.exists(LOCAL_DATA_PATH)
LOCAL_API_PATH = os.path.join(LOCAL_PROJECT_PATH,'API_PATH.yml')
assert os.path.exists(LOCAL_API_PATH)
#%% Get all links
with open(LOCAL_API_PATH) as f:
    api_paths = yaml.load(f)
r = requests.get(api_paths['BASE_URL'])
all_base_links = json.loads(r.text)

#%% Loop over each individually
all_data = list()
for l in all_base_links:
    
    if re.search('^ flower\d+',l['name']):
        file_url = requests.compat.urljoin(api_paths['BASE_URL'],l['path'])
        r = requests.get(file_url)
        this_data = json.loads(r.text)
        all_data.append(this_data['Flower'])
        print("Saved", l)
    else:
        print("Skip",l)
    #print(l)    
#%% Save data
# Create a DF
df = pd.DataFrame.from_records(all_data).set_index('id')
df['date'] = pd.to_datetime(df['timestamp'],unit='s')
df.sort_index(inplace=True)

# Save to disk
timestamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%SB")
path_csv = os.path.join(LOCAL_DATA_PATH,timestamp+".csv")
df.to_csv(path_csv)
print("Saved to {}".format(path_csv))

#%% Get all data at once
# This has a problem - no flower_id!!!
if 0:
    r = requests.get("https://flowertokens.hashbase.io/all_flowers.json")
    df = pd.DataFrame(all_data,index = '')


#%% 

# This has a problem - no flower ID!!!


