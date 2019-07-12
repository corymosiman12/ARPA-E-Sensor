import os
import sys
import pandas as pd
from datetime import datetime
from PIL import Image
import pickle
import gzip
#from collections import namedtuple
import collections

NewImage = collections.namedtuple('NewImage', 'day time data')

class ImageFile():
    def __init__(self, on_line, sensor):
        self.on_line = on_line
        self.sensor = sensor
        self.get_params()     

    def get_params(self):
        if not self.on_line:
            self.path = '/Users/maggie/Desktop/HPD_mobile_data/HPD_mobile-H1/BS1/img'
            self.write_location = '/Users/maggie/Desktop/HPD_mobile_data/HPD_mobile-H1/pickled_images'
        else:
            conf = self.import_conf()
            self.path = os.path.join(conf['img_audio_root'], self.sensor, 'img')
            self.write_location = os.path.join(self.path, 'pickled_images')
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
        return day_time

    def load_image(self, png):
        im = Image.open(png)
        return list(im.getdata())

    # def make_date_range(self, day):
    #     self.range_start = str(day + ' 00:00:00')
    #     self.range_end = str(day + ' 23:59:59')
    #     date_range = pd.date_range(start=self.range_start, end=self.range_end, freq='1s')
    #     return date_range   

    def pickle_object(self, entry, day):
        fname = day + '_' + self.sensor + '.pklz'
        f = gzip.open(os.path.join(self.write_location,fname), 'wb')
        pickle.dump(entry, f)
        print('File written: {}'.format(fname))
        f.close() 
    
    def main(self):
        for day in sorted(self.mylistdir(self.path)):
            print(day)
            #new_range = self.make_date_range(day)
            day_entry = []
            for hour in sorted(self.mylistdir(os.path.join(self.path, day))):
                for img_file in sorted(self.mylistdir(os.path.join(self.path, day, hour))):
                    day_time = self.get_time(img_file).strftime('%Y-%m-%d %H%M%S')
                    str_day = day_time.split(' ')[0]
                    str_time = day_time.split(' ')[1]
                    img_list = self.load_image(os.path.join(self.path, day, hour, img_file))
                    str_time = NewImage(day=str_day, time=str_time, data=img_list)
                    day_entry.append(str_time)
                    
            self.pickle_object(day_entry, str_day)


if __name__ == '__main__':
    on_line = True if len(sys.argv) > 1 else False
    sensor = sys.argv[1] if len(sys.argv) == 2 else 'BS1'
    I = ImageFile(on_line, sensor)
    I.main()
