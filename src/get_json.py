import requests
import logging
import json

#from datPython import Dat
#import datpy
import pandas as pd
import glob, os
import datetime
import re
#%%
#dat = datpy.Dat()
#r = dat.download(BASE_URL, 'data')
#print(r)

#datetime.datetime.now().isoformat()
 
#%% IO
LOCAL_DATA_PATH = glob.glob(os.path.expanduser('~/git/gardenstate/DATA'))[0]

#%% Get all links
BASE_URL = r"https://flowertokens.hashbase.io"
r = requests.get(BASE_URL)
all_base_links = json.loads(r.text)

#%% Loop over each individually
all_data = list()

for l in all_base_links:
    print(l)
    if re.search('^ flower\d+',l['name']):
        file_url = requests.compat.urljoin(BASE_URL,l['path'])
        r = requests.get(file_url)
        this_data = json.loads(r.text)
        all_data.append(this_data['Flower'])
        print("Saved", file_url)
    else:
        print("Skip",file_url)
        
#%% Save data
# Create a DF
df = pd.DataFrame.from_records(all_data).set_index('id')

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


