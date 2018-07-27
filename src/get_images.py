import requests
import logging
import json

#from datPython import Dat
#import datpy
import pandas as pd
import glob, os
#import datetime
#import re
import yaml
#import posixpath
import sys
import zipfile


#%% LOGGING for Spyder! Disable for production. 
logger = logging.getLogger()
logger.handlers = []

# Set level
logger.setLevel(logging.DEBUG)

# Create formatter
#FORMAT = "%(asctime)s - %(levelno)s - %(module)-15s - %(funcName)-15s - %(message)s"
#FORMAT = "%(asctime)s L%(levelno)s: %(message)s"
FORMAT = "%(asctime)s - %(funcName)-20s: %(message)s"
DATE_FMT = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(FORMAT, DATE_FMT)

# Create handler and assign
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(formatter)
logger.handlers = [handler]
logger.critical("Logging started")

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


#%% IO
LOCAL_PROJECT_PATH = glob.glob(os.path.expanduser('~/git/gardenstate'))[0]
assert os.path.exists(LOCAL_PROJECT_PATH)
LOCAL_DATA_PATH = os.path.join(LOCAL_PROJECT_PATH,'IMAGES')
assert os.path.exists(LOCAL_DATA_PATH)
LOCAL_API_PATH = os.path.join(LOCAL_PROJECT_PATH,'API_PATH.yml')
assert os.path.exists(LOCAL_API_PATH)

#%%
with open(LOCAL_API_PATH) as f:
    api_paths = yaml.load(f)

#%%

r = requests.get(api_paths['TIMESTAMPS'])
response_data = json.loads(r.text)

time_stamps = response_data['timestamps']
logging.debug("Found {} timestamps".format(len(time_stamps)))

[ts['key'] for ts in time_stamps]

ts_series = pd.Series([ts['key'] for ts in time_stamps])

ts_dt_series = pd.to_datetime(ts_series,unit='s')

ts_df = pd.concat([ts_dt_series,ts_series], axis=1)

ts_df.columns = ['datetime','mtime']

ts_df['delta'] = (ts_df['datetime']-ts_df['datetime'].shift()).fillna(0)
mean_timestep = ts_df['delta'].iloc[1::].mean()
total_time_elapsed = ts_df['datetime'].iloc[-1] - ts_df['datetime'][0]

logging.debug("mean timestep: {}".format(mean_timestep))
logging.debug("Total time elapsed:{}".format(total_time_elapsed))


#%% Get wall images

#requests.compat.urljoin(api_paths['BASE_API_URL'],record['mtime']+'.jpg')

#requests.compat.urljoin(api_paths['BASE_API_URL'],'wall/'+record['mtime']+'.jpg')


#%% 
def download_save_image(t_url,out_path):
    # GET the wall image     
    #TODO Check that os.path.join is cross-platform for URLs!
    r = requests.get(t_url)
    image = r.content
    #logging.debug("Downloaded image with size {}".format(len(image)))

    with open(out_path, 'wb') as f:
        f.write(image)
        
    #logging.debug("Saved image {}".format(out_path))
    
    logging.debug("Downloaded {:7} bytes to {}".format(len(image),out_path))
    
    
#%%
ts_df = ts_df[0:3]
for i,record in ts_df.iterrows():
    wall_url_name = record['mtime']+'.jpg'
    image_dt = record['datetime']
    image_dt_str = image_dt.strftime('%Y%m%dT%H%M%S')
    logging.debug("Processing timestep {}".format(image_dt))

    # Path handling, new directory for this timestamp
    path_folder_timestep = os.path.join(LOCAL_DATA_PATH,image_dt_str)
    path_this_wall = os.path.join(path_folder_timestep,image_dt_str+' wall'+'.jpg')
    path_flower_zip = os.path.join(path_folder_timestep+ ' flowers'+'.zip')
    
    
    if os.path.exists(path_flower_zip):
        logging.debug("Skipping {}, already exsists".format(image_dt))
        continue
    
    if not os.path.exists(path_folder_timestep):
        os.mkdir(path_folder_timestep)
    #elif os.path.exists(path_this_wall) and os.path.exists(path_flower_zip):
    #    # Skip this if this timestep has already been downloaded!
    #    logging.debug("SKIP".format())
    #    continue
    
    wall_url = os.path.join(api_paths['BASE_API_URL'],'wall',wall_url_name)
    download_save_image(wall_url,path_this_wall)

    # Iterate over flowers
    for flnum in range(1,4):
        flower_fname = "flower{}.jpg".format(flnum)
        url_this_flwr = os.path.join(api_paths['BASE_API_URL'],'flowers',record['mtime'],flower_fname)
        #r = requests.get(url_this_flwr)
        #flwr_image = r.content
        #logging.debug("{} - {} {} bytes".format(flower_fname,r.status_code,len(flwr_image)))
        path_flwr = os.path.join(path_folder_timestep,image_dt_str + " "+ flower_fname)
        
        download_save_image(url_this_flwr,path_flwr)
        
#%%
path_folder = path_folder_timestep
path_zip_out = path_flower_zip
def zip_flowers(path_folder,path_zip_out):
    # Collect the flower files
    all_image_files = glob.glob(os.path.join(path_folder, '*.jpg'))
    
    with zipfile.ZipFile(path_zip_out, 'w') as zip_this:        
        for file in all_image_files:
            zip_this.write(file, compress_type=zipfile.ZIP_DEFLATED)    
        
        
#        with open(path_flwr, 'wb') as f:
#            f.write(flwr_image)
#        logging.debug("Saved flower image {}".format(path_flwr))

        #print(flower_fname)


zip_flowers(path_folder_timestep,path_flower_zip)
#https://flowertokens.app/flowers/1logger.critical(532415250/flower1.jpg
#https://flowertokens.app/flowers/1532415250/flower100.jpg

#%%





























