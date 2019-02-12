import numpy as np
import matplotlib.pyplot as plt
import pysftp
import json
import time
import sys
import os
import datetime

class DynamicUpdatePlot(object):
    def __init__(self,sensorhub,query):
        self.min_x = 0
        self.max_x = 20
        self.json_name='/mnt/vdb/'+sensorhub+'/env_params/' #Parameterize this to change date and sensor hub
        self.json_time=1640 #periodically increase by 5 minutes
        self.date='2019-02-10'
        self.query=query
        self.dist=[] #may use append style
        self.dist.extend(-1*np.ones(30,))

    def get_json(self): #Sub min varies from 0 to 5 for 10ths of seconds in a minute
        cur_len=0
        if(-1 in self.dist==False):
            self.dist.extend(-1*np.ones(30,)) #About to be populated with 30 new data points for current json_time
        ##Gets the json file for all time instants within the specified minute
        '''
        with pysftp.Connection('192.168.0.202', username='root', password='antsle') as sftp: #parameterzie IP address
            with sftp.cd(self.json_name+self.date+'/'+repr(self.json_time)): #parameterize path
                etd_ftp_files = set()
                for etd_file in sftp.listdir():
                    if sftp.isfile(etd_file) and etd_file.lower().endswith('.json'):
                        etd_ftp_files.add(etd_file)
                        print(etd_ftp_files) #adds etd_ftp file for each env minute file in the directory
                etd_ftp_retrieve_files = etd_ftp_files
                for etd_file in etd_ftp_retrieve_files: #(etd_ftp_retrieve_files should have 5 files)
                    #Downloading each of the 5 files one by one
                    env_json_file=sftp.get(etd_file, localpath=os.path.join('C:/Users/Homagni/Desktop/json', etd_file))
                cur_len=len(etd_ftp_retrieve_files) #Based on number of json files currently created on antsle
        '''
        cur_len=2
        #Now open the downloaded data files locally (max 5 downloaded files per json_time)
        for i in range(self.json_time,self.json_time+cur_len): #5 is the number of files in the directory , #i iterates the hourminute extension of file
            with open('json/'+self.date+' '+repr(i)+'_env_params.json') as json_file: 
                data = json.load(json_file)
                #print("This is data file at time instant ",i)
                #Each of the downloaded files in turn have 6 data points
                for j in range(len(data)):
                    #print("data dist ... ",data[j]['dist_mm'])
                    self.dist[6*(i-self.json_time)+j]=data[j][self.query] # Encourages over write in case of lost data packets
                #sys.exit()
        print(self.dist)
            
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
        if(max_readings%20==0):
            self.ax.set_xlim(self.min_x+max_readings, self.max_x+max_readings)
        #We need to draw *and* flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
    def draw(self):
        max_readings=0
        self.on_launch()     
        xdata = []
        ydata = []
        while(True): #this is how many readings to plot 
            self.get_json()
            max_readings+=1 #time counter is incremented nonetheless
            for i in range(len(xdata),len(self.dist)):
                if(self.dist[i]==-1):
                    break #means new data has not been added
                if(self.dist[i]!=None):
                    xdata.append(max_readings+i)
                    ydata.append(self.dist[i])
            self.on_running(xdata, ydata, max_readings)
            time.sleep(1)
            now = datetime.datetime.now()
            #self.date=now.strftime("%Y-%m-%d") #uncomment to update dates
            if(max_readings%(5*60)==0):#5 mins over, new file should have been created
                #self.json_time+=5 #uncomment to update json times
                pass 
        return xdata, ydata
def main():
    plt.ion()
    d = DynamicUpdatePlot(sys.argv[1],sys.argv[2])
    #run as...
    #python diagnostics.py BS2 dist_mm
    d.draw()
if __name__ == '__main__':
    main()


