import os
import sys
import pandas as pd
from datetime import datetime
from PIL import Image
import pickle
import gzip
import json
#from collections import namedtuple
import collections
from memory_profiler import profile

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
            self.write_location = os.path.join(conf['img_audio_root'], self.sensor, 'pickled_images')
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

    def load_image(self, png):
        im = Image.open(png)
        im = im.resize((112,112), Image.BILINEAR)
        return list(im.getdata())

    # def make_date_range(self, day):
    #     self.range_start = str(day + ' 00:00:00')
    #     self.range_end = str(day + ' 23:59:59')
    #     date_range = pd.date_range(start=self.range_start, end=self.range_end, freq='1s')
    #     return date_range   

    # @profile
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
            #new_range = self.make_date_range(day)
            day_entry = []
            hours = [str(x).zfill(2) + str(y) + '0' for x in range(0,24) for y in range(0,6)]
            all_mins = sorted(self.mylistdir(os.path.join(self.path, day)))

            for hr in hours:
                this_hr = [x for x in all_mins if x[0:3] == hr[0:3]]
                # if len(this_hr) > 0:
                #     print(len(this_hr))
                #     print(hr, this_hr)
                # else:
                #     print('{} is empty'.format(hr))
                for minute in sorted(this_hr):
                    for img_file in sorted(self.mylistdir(os.path.join(self.path, day, minute))):
                        day_time = self.get_time(img_file).split(' ')
                        str_day, str_time = day_time[0], day_time[1]
                        img_list = self.load_image(os.path.join(self.path, day, minute, img_file))
                        str_time = NewImage(day=str_day, time=str_time, data=img_list)
                        day_entry.append(str_time)
                        
                fname = day + '_' + hr + '_' + self.sensor + '.pklz'

                # print('time is: {}'.format(datetime.now().strftime('%H:%M:%S')))
                # fname = day + '_' + hr + '_' + self.sensor + '.pklz'
                # f = gzip.open(os.path.join(self.write_location,fname), 'wb')
                # pickle.dump(entry, f)
                # f.close() 
                # print('File written: {}'.format(fname))

                try:
                    self.pickle_object(day_entry, fname)
                except Exception as e:
                    print('Error: {}'.format(e))
                

# class MyPerformanceMonitor(threading.Thread):
#     """
#     Used to monitor the disk space, CPU, and memory of the pi.
#     """

#     def __init__(self):
#         threading.Thread.__init__(self)
#         self.disk_threshold = 75
#         self.mem_threshold = 25
#         self.calc_cpu_range()
#         self.start()

#     def calc_cpu_range(self):
#         cpu = psutil.cpu_freq()
#         self.cpu_range = cpu.max - cpu.min

#     def run(self):
#         logging.info('MyPerformanceMonitor run')
#         while True:
#             # michaelJordan time
#             if datetime.now().second == 23:
#                 try:
#                     # logging.info('MyPerformanceMonitor time to check!')
#                     cpu_perc = psutil.cpu_percent()
#                     if cpu_perc > 80:
#                         m = 'High CPU usage: {}'.format(cpu_perc)
#                         logging.warning(m)
#                         # print(m)

#                     virt_mem = psutil.virtual_memory()
#                     if virt_mem.percent <= self.mem_threshold:
#                         m = 'High virtual mem usage. Mem available: {}'.format(
#                             virt_mem.percent)
#                         logging.warning(m)
#                         # print(m)

#                     swap_mem = psutil.swap_memory()
#                     if swap_mem.percent >= self.mem_threshold:
#                         m = 'High swap mem usage: {}'.format(swap_mem.percent)
#                         logging.warning(m)
#                         # print(m)

#                     disk_usage = psutil.disk_usage('/')
#                     if disk_usage.percent >= self.disk_threshold:
#                         m = 'High disk usage: % User disk utilization: {}'.format(
#                             disk_usage.percent)
#                         # print(m)
#                         logging.warning(m)

#                     if datetime.now().minute % 5 == 0:
#                         logging.info('CPU Perc Usage: {}\tVirt Mem Perc Usage: {}\tSwap Mem Perc Usage: {}\tDisk Perc Usage: {}'.format(
#                             cpu_perc, virt_mem.percent, swap_mem.percent, disk_usage.percent))
#                 except Exception as e:
#                     logging.warning(
#                         'MyPerformanceMonitor excepted: {}'.format(e))
#                 time.sleep(1)




if __name__ == '__main__':
    on_line = True if len(sys.argv) > 1 else False
    sensor = sys.argv[1] if len(sys.argv) == 2 else 'BS1'
    I = ImageFile(on_line, sensor)
    I.main()
