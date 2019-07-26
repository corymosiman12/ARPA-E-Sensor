import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime
from PIL import Image
import pickle
import gzip
import json
import collections

"""
This class takes the raw images that are saved on a server (antsle)
or in similar folder structure on a computer, and turns the images 
into arrays, reduces the size (from 336 x 336 to 112 x 112) and
pickles and compresses the result by hour. 

This file is meant to be used in conjunction with 'img_extract.py"
"""


NewImage = collections.namedtuple('NewImage', 'day time data')

class ImageFile():
    def __init__(self, on_line, sensor, dir):
        self.on_line = on_line
        self.sensor = sensor
        self.path = dir
        self.get_params()     
        self.black_imgs = []
        self.write_path = None
        self.stored_path = None

    def get_params(self):
        if not self.on_line:
            self.write_location = '/Users/maggie/Desktop/HPD_mobile_data/HPD_mobile-H1/pickled_images'
        else:
            stored = self.path.slpit('/')
            #self.write_location = os.path.join(stored[1], stored[2], self.sensor, 'pickled_images')
            self.write_location = self.write_path
            if not os.path.isdir(self.write_location):
                os.mkdir(self.write_location)
       
    def import_conf(self):
        with open('/root/client/client_conf.json', 'r') as f:
            conf = json.loads(f.read())
        return conf

    def mylistdir(self, directory):
        filelist = os.listdir(directory)
        return [x for x in filelist if not (x.startswith('.') or 'Icon' in x)]

    def get_time(self, file_name):
        day_time = datetime.strptime(file_name.strip('_photo.png'), '%Y-%m-%d %H%M%S')
        return day_time.strftime('%Y-%m-%d %H%M%S')

    def load_image(self, png, time):
        im = Image.open(png)
        im = im.resize((112,112), Image.BILINEAR)
        new_im = np.array(list(im.getdata()))
        ave_pxl = np.mean(new_im)
        return new_im if ave_pxl > 10 else 0

    """
    The following method creates a pandas dataframe for all images that 
    are supposed to be present. It is not active now
    """
    # def make_date_range(self, day):
    #     self.range_start = str(day + ' 00:00:00')
    #     self.range_end = str(day + ' 23:59:59')
    #     date_range = pd.date_range(start=self.range_start, end=self.range_end, freq='1s')
    #     return date_range   

    def pickle_object(self, entry, fname):
        print('time is: {}'.format(datetime.now().strftime('%H:%M:%S')))
        # fname = day + '_' + self.sensor + '.pklz'
        f = gzip.open(os.path.join(self.write_location,fname), 'wb')
        pickle.dump(entry, f)
        f.close() 
        print('File written: {}'.format(fname))

    def main(self):
        for day in sorted(self.mylistdir(self.path)):
            print(day)
            hours = [str(x).zfill(2) + '00' for x in range(0,24)]
            all_mins = sorted(self.mylistdir(os.path.join(self.path, day)))

            for hr in hours:
                hr_entry = []
                self.img_means = []
                this_hr = [x for x in all_mins if x[0:2] == hr[0:2]]
                for minute in sorted(this_hr):
                    for img_file in sorted(self.mylistdir(os.path.join(self.path, day, minute))):
                        day_time = self.get_time(img_file).split(' ')
                        str_day, str_time = day_time[0], day_time[1]
                        try:
                            img_list = self.load_image(os.path.join(self.path, day, minute, img_file), str_time)
                            str_time = NewImage(day=str_day, time=str_time, data=img_list)
                            hr_entry.append(str_time)
                        except Exception as e:
                            print('Pillow error: {}'.format(e))
                
                fname = day + '_' + hr + '_' + self.sensor + '.pklz'

                try:
                    self.pickle_object(hr_entry, fname)
                except Exception as e:
                    print('Pickle error: {}'.format(e))


if __name__ == '__main__':
    on_line = True if len(sys.argv) > 1 else False
    sensor = sys.argv[1] if len(sys.argv) == 2 else 'BS1'
    stored_loc = sys.argv[2] if len(sys.argv) == 3 else '/Users/maggie/Desktop/HPD_mobile_data/HPD_mobile-H1/BS1/img'
    I = ImageFile(on_line, sensor, stored_loc)
    I.main()
