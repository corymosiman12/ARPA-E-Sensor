import os
import pandas as pd
from datetime import datetime
import json
import ast

class AudioChecker():
    def __init__(self, path_to_import_conf, write_file, display_output, server_id):
        self.conf_file_path = path_to_import_conf
        self.import_conf(self.conf_file_path)
        self.write_file = write_file
        self.display_output = display_output
        self.audio_tape_length = self.conf_dict['audio_tape_length']
        self.all_seconds = pd.date_range(self.b_dt, self.e_dt, freq = self.audio_tape_length).tolist()
        self.expect_num_wavs = len(self.all_seconds)
        self.expect_num_directories = len(pd.date_range(self.b_dt, self.e_dt, freq = self.conf_dict["dir_create_freq"]).tolist())
        self.root_dir = os.path.join(self.conf_dict['root'], server_id, 'audio')
        self.date_dirs = self.conf_dict['date_dirs']
        self.hrs_to_pass = self.conf_dict['hr_dirs_to_skip']
        self.correct_files_per_dir = self.conf_dict['audio_files_per_dir']
        self.count_correct = {}
        self.count_other = {}
        self.total_wavs = 0
        self.duplicates = 0
        self.counter_min = 50
        self.duplicates_ts = []
        self.wavs = []

    def import_conf(self, path):
        with open(path, 'r') as f:
            self.conf_dict = json.loads(f.read())
        self.b_dt = self.conf_dict['begin_dt']
        self.e_dt = self.conf_dict['end_dt']
        self.b_dt_as_dt = datetime.strptime(self.b_dt, '%Y-%m-%d %H:%M:%S')
        self.e_dt_as_dt = datetime.strptime(self.e_dt, '%Y-%m-%d %H:%M:%S')

    def finder(self):
        for pic in self.wavs:
            dt = datetime.strptime(pic.split('_')[0], '%Y-%m-%d %H%M%S')
            try:
                ind = self.all_seconds.index(dt)
                self.all_seconds.pop(ind)
            except:
                self.duplicates += 1
                self.duplicates_ts.append(dt.strftime('%Y-%m-%d %H:%M:%S'))
                # print('Total duplicates: {}\tdt: {}'.format(self.duplicates, dt))
                pass

    def writer(self, output_dict):
        if self.write_file:

            b = 'test_output.json'
            write_file = os.path.join(self.root_dir, b)
            print('Writing file to: {}'.format(write_file))
            with open(write_file, 'w+') as f:
                f.write(json.dumps(output_dict))
    
    def displayer(self, output_dict):
        if self.display_output:
            print(output_dict)

    def configure_output(self):
        if self.write_file or self.display_output:
            missed_seconds = []

            for ts in self.all_seconds:
                missed_seconds.append(ts.strftime('%Y-%m-%d %H:%M:%S'))

            output_dict = {
                'Configuration dict': self.conf_dict,
                'Expected number of wavs': self.expect_num_wavs,
                'Number of wavs counted (including duplicates)': self.total_wavs,
                'Total number of duplicates': self.duplicates,
                'Number of not captured wavs': len(self.all_seconds),
                'Expected number of directories': self.expect_num_directories,
                'Number of directories w/correct num wavs': len(self.count_correct),
                'Number of directories w/incorrect num wavs': len(self.count_other),
                'Non-correct wavs directories': self.count_other,
                'Timestamps of not captured wavs': missed_seconds,
                'Duplicates': self.duplicates_ts
            }
        else:
            output_dict = []
        return output_dict

    def main(self):
        for d in self.date_dirs:
            hr_min_dirs = os.listdir(os.path.join(self.root_dir, d))
            for hr_min in hr_min_dirs:
                if hr_min in self.hrs_to_pass:
                    print('Not looking in : {}'.format(os.path.join(self.root_dir, d, hr_min)))
                    continue
                else:
                    a = datetime.strptime((d + ' ' + hr_min), '%Y-%m-%d %H%M')
                    if a < self.b_dt_as_dt or a > self.e_dt_as_dt:
                        continue
                    else:
                        temp = os.path.join(self.root_dir, d, hr_min)
                        if os.path.isdir(temp):
                            self.wavs = os.listdir(os.path.join(self.root_dir, d, hr_min))
                            self.wavs = [x for x in self.wavs if x.endswith('.wav')]
                            self.finder()
                            self.total_wavs += len(self.wavs)
                            if self.total_wavs > self.counter_min:
                                print('Counting wav: {}'.format(self.total_wavs))
                                self.counter_min += 50

                            if len(self.wavs) == self.correct_files_per_dir:
                                self.count_correct[os.path.join(d,hr_min)] = self.correct_files_per_dir

                            elif len(self.wavs) != 3:
                                self.count_other[os.path.join(d,hr_min)] = len(self.wavs)

                        else:
                            print('{} is not a dir'.format(temp))
        
        output_dict = self.configure_output()
        self.writer(output_dict)
        self.displayer(output_dict)
        print('All done!')

if __name__ == '__main__':
    """
    Example of full path to configuration files:
        /Users/corymosiman/Github/ARPA-E-Sensor/tests/audio/conf/cnt_audio_1_final_conf.json
        /Users/corymosiman/Github/ARPA-E-Sensor/tests/audio/conf/cnt_audio_2_final_conf.json
    """
    path = input('Input full path to configuration file: ')
    server_id = input('Enter the server id.  For example, `BS1`: ')
    write_file = input('Do you want to write output file (True or False): ')
    while not write_file == 'True' and not write_file == 'False':
        write_file = input('Enter True or False: ')


    display_output = input('Do you want to display output (True or False): ')
    while not display_output == 'True' and not display_output == 'False':
        display_output = input('Enter True or False: ')

    a = AudioChecker(path, write_file, display_output, server_id)
    a.main()