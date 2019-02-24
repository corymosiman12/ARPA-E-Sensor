import numpy as np
import matplotlib.pyplot as plt
import pysftp
import json
import time
import sys
import os
import datetime
import csv
import copy

class DynamicUpdatePlot(object):
    def __init__(self,sensorhub,query):
        self.min_x = 0
        self.max_x = 20
        #Change parameters here
        self.json_name='/mnt/disk2/'+sensorhub+'/env_params/' #Parameterize this to change date and sensor hub
        self.json_time=2040 #periodically increase by 5 minutes, adjust the starting time once before starting
        self.date='2019-02-22' #adjust the starting date
        self.local_save_path='C:/Users/maggie/Desktop/json'
        #Connection parameters
        self.ip='192.168.0.202'
        self.ip_name='root'
        self.ip_pass='antsle'
        self.local_test=True

        self.start_json_time=copy.copy(self.json_time)
        self.query=query
        self.sensorhub=sensorhub
        self.array_pointer=0
        self.file_names=[]
        #self.load_file_names()
        self.half_min_len=0
        self.dist=[] #may use append style
        self.dist.extend(-1*np.ones(30,))
    def write_to_csv(self):
        fname = self.sensorhub+self.query+'.csv'
        file1 = open(fname, 'a')
        writer = csv.writer(file1)
        for i in range(self.array_pointer,len(self.dist)):
            if(self.dist[i]==-1):
                continue
            fields1=[self.date,self.json_time,self.dist[i]]
            writer.writerow(fields1)
        self.array_pointer+=len(self.dist)
        file1.close()
    def catch_file_names(self,file_list):
        fname = self.sensorhub+self.query+'files_already_downloaded.obj'
        for i in file_list:
            self.file_names.append(repr(i))
        file1 = open(fname, 'w')
        pickle.dump(self.file_names,file1)
        file1.close()
    def load_file_names(self):
        try:
            file=open(self.sensorhub+self.query+'files_already_downloaded.obj','r')
            self.file_names=pickle.load(file)
            file.close()
        except:
            print("Pickle file has not been created yet")
    def get_json(self): #Sub min varies from 0 to 5 for 10ths of seconds in a minute
        cur_len=0
        if(not -1.0 in self.dist):
            self.dist.extend(-1*np.ones(30,)) #About to be populated with 30 new data points for current json_time
            self.json_time+=5
            self.half_min_len+=30
            print("Creating new positions in data holder")
        ##Gets the json file for all time instants within the specified minute
        if(self.local_test==False):
            with pysftp.Connection(self.ip, username=self.ip_name, password=self.ip_pass) as sftp: #parameterzie IP address
                with sftp.cd(self.json_name+self.date+'/'+repr(self.json_time)): #parameterize path
                    etd_ftp_files = set()
                    for etd_file in sftp.listdir():
                        if sftp.isfile(etd_file) and etd_file.lower().endswith('.json'):
                            etd_ftp_files.add(etd_file)
                            print(etd_ftp_files) #adds etd_ftp file for each env minute file in the directory
                    etd_ftp_retrieve_files = etd_ftp_files
                    self.catch_file_names(etd_ftp_retrieve_files)
                    for etd_file in etd_ftp_retrieve_files: #(etd_ftp_retrieve_files should have 5 files)
                        #Downloading each of the 5 files one by one
                        #if(repr(etd_file) in self.file_names==False):
                        env_json_file=sftp.get(etd_file, localpath=os.path.join(self.local_save_path, etd_file)) #Chose your own local save path
                    cur_len=len(etd_ftp_retrieve_files) #Based on number of json files currently created on antsle
            #except:
                #print("File is not being saved on the antsle or connection is not estabished")
        
        if(self.local_test==True):
            cur_len=5 #Comment this later 
        #Now open the downloaded data files locally (max 5 downloaded files per json_time)
    #try:
        for i in range(self.json_time,self.json_time+cur_len): #5 is the number of files in the directory , #i iterates the hourminute extension of file
            vm_path = os.path.join(self.json_name, self.date, repr(i))
            print(vm_path)
            with open(vm_path+'/'+self.date+' ' +repr(i)+'_env_params.json') as json_file: 
                #print(vm_path+repr(i)+'_env_params.json')
                data = json.load(json_file)
                #print("This is data file at time instant ",i)
                #Each of the downloaded files in turn have 6 data points
                for j in range(len(data)):
                    #print("data dist ... ",data[j]['dist_mm'])
                    self.dist[30*int((self.json_time-self.start_json_time)/5)+6*(i-self.json_time)+j]=data[j][self.query] # Encourages over write in case of lost data packets
   # except:
        # print("Files were not downloaded from antsle to local machine ")
        # print("Current json_time ",self.json_time)   
        # print(self.dist)
        # print(len(self.dist))
        # #sys.exit()
            
    def on_launch(self):
        #Set up plot
        self.figure, self.ax = plt.subplots()
        self.lines, = self.ax.plot([],[], 'o')
        #Autoscale on unknown axis and known lims on the other
        self.ax.set_autoscaley_on(True)
        self.ax.set_xlim(self.min_x, self.max_x)
        #Other stuff
        self.ax.grid()

    def on_running(self, xdata, ydata, max_readings):
        #Update data (with the new _and_ the old points)
        self.lines.set_xdata(xdata)
        self.lines.set_ydata(ydata)
        #Need both of these in order to rescale
        self.ax.relim()
        self.ax.autoscale_view()
        if(max_readings%30==0): #adjust this to control how fast the graph slides rightwards
            self.ax.set_xlim(self.min_x+30, self.max_x+30)
        #We need to draw *and* flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
    def draw(self):
        self.on_launch()     
        xdata = []
        ydata = []
        half_min_len=0
        inc_readings=0
        while(True): #this is how many readings to plot 
            self.get_json()
            max_readings=self.half_min_len
            for i in range(self.half_min_len,len(self.dist)):
                max_readings+=1 #time counter is incremented nonetheless
                inc_readings+=1
                if(self.dist[i]==-1):
                    print("break")
                    break #means new data has not been added
                if(self.dist[i]!=None):
                    #if(max_readings in xdata==False):
                    xdata.append(max_readings)
                    ydata.append(self.dist[i])
            self.on_running(xdata, ydata, inc_readings)
            time.sleep(1)
            #print("xdata ",xdata)
            #print("ydata ",ydata)
            if(len(xdata)>30): #Chop off the unnecessary data to prevent blow up
                xdata=xdata[30:]
                ydata=ydata[30:]
            self.write_to_csv()
            now = datetime.datetime.now()
            if(self.local_test==False):
                self.date=now.strftime("%Y-%m-%d") #uncomment to update dates
        return xdata, ydata
def main():
    plt.ion()
    d = DynamicUpdatePlot(sys.argv[1],sys.argv[2])
    #run as...
    #python diagnostics.py BS2 dist_mm
    d.draw()
if __name__ == '__main__':
    main()


