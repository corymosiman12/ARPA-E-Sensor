import json
import socket
import sys
import os
from datetime import datetime, timedelta
import threading
import logging
import time
import influxdb
import pysftp
import paramiko
from queue import Queue

logging.basicConfig(filename = '/root/client_logfile.log', level = logging.INFO,
                    format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',)

class MyRetriever(threading.Thread):
    def __init__(self, my_root, pi_ip_address, pi_img_audio_root, listen_port, debug):
        threading.Thread.__init__(self)
        logging.info('Initializing MyRetriever')
        self.my_audio_root = os.path.join(my_root, 'audio')
        self.my_img_root = os.path.join(my_root, 'img')
        self.pi_ip_address = pi_ip_address
        self.pi_audio_root = os.path.join(pi_img_audio_root, 'audio')
        self.pi_img_root = os.path.join(pi_img_audio_root, 'img')
        self.listen_port = listen_port
        self.debug = debug
        self.to_retrieve = Queue(maxsize=0)
        self.num_threads = 5
        self.successfully_retrieved = []
        self.audio_seconds = [str(x).zfill(2) for x in range(0,60,20)]
        self.img_seconds = [str(x).zfill(2) for x in range(0,60)]
        self.bad_audio_transfers = 0
        self.bad_img_transfers = 0
        self.start()
    
    def to_retrieve_updater(self):
        while True:
            if datetime.now().second == 0:
                time.sleep(1)
                p = True
                if self.debug and p:
                    print("Retriever updater running")
                    p = False
                audio_date_dir = os.path.join(self.my_audio_root, datetime.now().strftime('%Y-%m-%d'))
                img_date_dir = os.path.join(self.my_img_root, datetime.now().strftime('%Y-%m-%d'))
                if not os.path.isdir(audio_date_dir):
                    os.makedirs(audio_date_dir)
                self.my_audio_root_date = audio_date_dir

                if not os.path.isdir(img_date_dir):
                    os.makedirs(img_date_dir)
                self.my_img_root_date = img_date_dir

                t = datetime.now() - timedelta(minutes = 1)
                prev_min_audio_dir = os.path.join(self.my_audio_root_date, t.strftime('%H%M'))
                prev_min_img_dir = os.path.join(self.my_img_root_date, t.strftime('%H%M'))

                if not os.path.isdir(prev_min_audio_dir):
                    os.makedirs(prev_min_audio_dir)
                    pi_audio_dir = os.path.join(self.pi_audio_root, t.strftime('%Y-%m-%d'), t.strftime('%H%M'))
                    # self.to_retrieve.append((pi_audio_dir, prev_min_audio_dir))
                    self.to_retrieve.put((pi_audio_dir, prev_min_audio_dir))

                if not os.path.isdir(prev_min_img_dir):
                    os.makedirs(prev_min_img_dir)
                    pi_img_dir = os.path.join(self.pi_img_root, t.strftime('%Y-%m-%d'), t.strftime('%H%M'))
                    # self.to_retrieve.append((pi_img_dir, prev_min_img_dir))
                    self.to_retrieve.put((pi_img_dir, prev_min_img_dir))
    
    def restart_dat_service(self):
        r = ['restart']
        # Instantiate IPV4 TCP socket class
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Create a socket connection to the server at the specified port
            s.connect((self.pi_ip_address, self.listen_port))

            # Send message over socket connection, requesting aforementioned data
            s.sendall(self.create_message(r))
            
            # Receive all data from server.
            self.restart_response = self.my_recv_all(s).split('\r\n')

            logging.warning('Telling pi to restart - not getting correct data. Pi response: {}'.format(self.restart_response))
            if self.debug:
                print('Telling pi to restart - not getting correct data. Pi response: {}'.format(self.restart_response))

            # Close socket
            s.close()

        except Exception as e:
            logging.warning('Exception occured when telling pi to restart.  Exception: {}'.format(e))
            if self.debug:
                print('Attempted to restart pi, appears unsuccessful')
            if s:
                try:
                    s.close()
                except:
                    pass
        if s:
            try:
                s.close()
            except:
                pass

    def restart_dat_img(self):
        r = ['restart_img']
        # Instantiate IPV4 TCP socket class
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Create a socket connection to the server at the specified port
            s.connect((self.pi_ip_address, self.listen_port))

            # Send message over socket connection, requesting aforementioned data
            s.sendall(self.create_message(r))
            
            # Receive all data from server.
            self.restart_response = self.my_recv_all(s).split('\r\n')

            logging.warning('Telling pi to restart UV4L - not getting correct data. Pi response: {}'.format(self.restart_response))
            if self.debug:
                print('Telling pi to restart UV4L - not getting correct data. Pi response: {}'.format(self.restart_response))

            # Close socket
            s.close()

        except Exception as e:
            logging.warning('Exception occured when telling pi to restart UV4L.  Exception: {}'.format(e))
            if self.debug:
                print('Attempted to restart UV4L, appears unsuccessful')
            if s:
                try:
                    s.close()
                except:
                    pass
        if s:
            try:
                s.close()
            except:
                pass

    def has_correct_files(self, item):
        missing = []
        local_dir = item[1]
        d, hr = local_dir.split('/')[-2:]
        if 'audio' in local_dir:
            should_have_files = [os.path.join(local_dir, '{} {}{}_audio.wav'.format(d, hr, s)) for s in self.audio_seconds]
            has_files = [os.path.join(local_dir, f) for f in os.listdir(local_dir) if f.endswith('.wav')]
            missing = list(set(should_have_files) - set(has_files))
            if self.debug:
                print('audio missing: {} files'.format(len(missing)))
                print('specifically these files: {}'.format(missing))
            if len(missing) >=1:
                self.bad_audio_transfers += 1
                logging.warning('audio missing: {} files'.format(len(missing)))
                logging.warning('specifically these files: {}'.format(missing))

        elif 'img' in local_dir:
            should_have_files = [os.path.join(local_dir, '{} {}{}_photo.png'.format(d, hr, s)) for s in self.img_seconds]
            has_files = [os.path.join(local_dir, f) for f in os.listdir(local_dir) if f.endswith('.png')]
            missing = list(set(should_have_files) - set(has_files))
            if self.debug:
                print('img missing: {} files'.format(len(missing)))
                print('specifically these files: {}'.format(missing))
            if len(missing) >=1:
                self.bad_img_transfers += 1
                logging.warning('img missing: {} files'.format(len(missing)))
                logging.warning('specifically these files: {}'.format(missing))
        
        if self.bad_audio_transfers >= 5 or self.bad_img_transfers >= 5:
            self.restart_dat_service()
            time.sleep(5)
            self.restart_dat_img()
            self.bad_audio_transfers = 0
            self.bad_img_transfers = 0

    def retrieve_this(self):
        item = self.to_retrieve.get()
        typ = 'audio' if 'audio' in item[0] else 'img'
        if self.debug:
            print('Thread started to get: {}'.format(item))
        try:
            with pysftp.Connection(self.pi_ip_address, username='pi', password='sensor') as sftp:
                try:
                    sftp.get_d(item[0], item[1], preserve_mtime=True)
                    # ind = self.to_retrieve.index(item)
                    self.successfully_retrieved.append(item)
                    logging.info('Successfully retrieved {}'.format(item[0]))
                    
                    self.to_retrieve.task_done()
                    self.has_correct_files(item)

                    if self.debug:
                        print('Successfully retrieved {}'.format(item[0]))

                except FileNotFoundError:
                    logging.critical('File not found on Server.  No way to retrieve past info.')
                    if self.debug:
                        print('File not found on Server.  No way to retrieve past info.')
                    self.to_retrieve.task_done()
                    self.restart_dat_img()

        except (ConnectionAbortedError, ConnectionError, ConnectionRefusedError, ConnectionResetError, paramiko.ssh_exception.SSHException) as conn_error:
            logging.warning('Network connection error: {}'.format(conn_error))
            if self.debug:
                print('Network connection error: {}'.format(conn_error))
            self.to_retrieve.task_done()
            self.to_retrieve.put(item)

    def create_message(self, to_send):
        """
        Configure the message to send to the server.
        Elements are separated by a carriage return and newline.
        The first line is always the datetime of client request.

        param: to_send <class 'list'>
                List of elements to send to server.

        return: <class 'bytes'> a byte string (b''), ready to 
                send over a socket connection
        """
        dt_str = [datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")]
        for item in to_send:
            dt_str.append(item)
        
        message = '\r\n'.join(dt_str)
        logging.info("Sending Message: \n{}".format(message))
        return message.encode()

    def my_recv_all(self, s, timeout=2):
        """
        Regardless of message size, ensure that entire message is received
        from server.  Timeout specifies time to wait for additional socket
        stream.

        param: s <class 'socket.socket'>
                A socket connection to server.
        return: <class 'str'>
                A string containing all info sent.
        """
        try:
        #make socket non blocking
            s.setblocking(0)
            
            #total data partwise in an array
            total_data=[]
            data=''
            
            #beginning time
            begin=time.time()
            while 1:
                #if you got some data, then break after timeout
                if total_data and time.time()-begin > timeout:
                    break
                
                #if you got no data at all, wait a little longer, twice the timeout
                elif time.time()-begin > timeout*2:
                    break
                
                #recv something
                try:
                    data = s.recv(8192).decode()
                    if data:
                        total_data.append(data)
                        #change the beginning time for measurement
                        begin = time.time()
                    else:
                        #sleep for sometime to indicate a gap
                        time.sleep(0.1)
                except Exception as e:
                    logging.warning('Exception occured in my_recv_all inner.  Exception: {}'.format(e))
                    try:
                        s.close()
                    except:
                        pass
            
            #join all parts to make final string
            return ''.join(total_data)
        except Exception as e:
            logging.warning('Exception occured in my_recv_all_outer.  Exception: {}'.format(e))
            try:
                s.close()
            except:
                pass

    def run(self):
        retriever_updater = threading.Thread(target = self.to_retrieve_updater)
        retriever_updater.start()

        while True:
            if not self.to_retrieve.empty():
                for i in range(self.num_threads):
                    worker = threading.Thread(target=self.retrieve_this)
                    worker.setDaemon(True)
                    worker.start()

class MyClient():
    def __init__(self, server_id, debug):
        self.debug = debug
        self.server_id = server_id
        self.conf = self.import_conf(self.server_id)
        self.pi_ip_address = self.conf['servers'][self.server_id]
        self.my_root = os.path.join(self.conf['img_audio_root'], self.server_id)
        self.image_dir = os.path.join(self.my_root, 'img')
        self.audio_dir = os.path.join(self.my_root, 'audio')
        self.listen_port = int(self.conf['listen_port'])
        self.collect_interval = int(self.conf['collect_interval_min'])
        self.influx_client = influxdb.InfluxDBClient(self.conf['influx_ip'], 8086, database='hpd_mobile')
        self.pi_img_audio_root = self.conf['pi_img_audio_root']
        self.server_delete_thread = threading.Thread(target = self.server_delete, daemon=True)
        self.server_delete_thread.start()
        self.create_img_dir()
        self.create_audio_dir()
        self.retriever = MyRetriever(self.my_root, self.pi_ip_address, self.pi_img_audio_root, self.listen_port, self.debug)

    def import_conf(self, server_id):
        """
        Import the client configuration file.

        param: server_id <class 'str'>
        return: <class 'dict'> of configuration parameters
        """
        with open('client_conf.json', 'r') as f:
            conf = json.loads(f.read())
            
        return conf
    
    def create_img_dir(self):
        """
        Check if main server directory for images exist.  If they exist, do nothing.
        If they don't exist yet, create.  This directory will be:
            /mnt/vdb/<server_id>/img/
        """
        if not os.path.isdir(self.image_dir):
            os.makedirs(self.image_dir)

    def create_audio_dir(self):
        """
        Check if server directories for images exist.  If they exist, do nothing.
        If they don't exist yet, create.  This directory will be:
            /mnt/vdb/<server_id>/audio
        """
        if not os.path.isdir(self.audio_dir):
            os.makedirs(self.audio_dir)

    def create_message(self, to_send):
        """
        Configure the message to send to the server.
        Elements are separated by a carriage return and newline.
        The first line is always the datetime of client request.

        param: to_send <class 'list'>
                List of elements to send to server.

        return: <class 'bytes'> a byte string (b''), ready to 
                send over a socket connection
        """
        dt_str = [datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")]
        for item in to_send:
            dt_str.append(item)
        
        message = '\r\n'.join(dt_str)
        logging.info("Sending Message: \n{}".format(message))
        return message.encode()

    def my_recv_all(self, s, timeout=2):
        """
        Regardless of message size, ensure that entire message is received
        from server.  Timeout specifies time to wait for additional socket
        stream.

        param: s <class 'socket.socket'>
                A socket connection to server.
        return: <class 'str'>
                A string containing all info sent.
        """
        try:
            #make socket non blocking
            s.setblocking(0)
            
            #total data partwise in an array
            total_data=[]
            data=''
            
            #beginning time
            begin=time.time()
            while 1:
                #if you got some data, then break after timeout
                if total_data and time.time()-begin > timeout:
                    break
                
                #if you got no data at all, wait a little longer, twice the timeout
                elif time.time()-begin > timeout*2:
                    break
                
                #recv something
                try:
                    data = s.recv(8192).decode()
                    if data:
                        total_data.append(data)
                        #change the beginning time for measurement
                        begin = time.time()
                    else:
                        #sleep for sometime to indicate a gap
                        time.sleep(0.1)
                except Exception as e:
                    logging.warning('Exception occured in my_recv_all inner.  Exception: {}'.format(e))
                    try:
                        s.close()
                    except:
                        pass
            
            #join all parts to make final string
            return ''.join(total_data)
        except Exception as e:
            logging.warning('Exception occured in my_recv_all_outer.  Exception: {}'.format(e))
            try:
                s.close()
            except:
                pass

    def influx_write(self):
        """
        Format all data received from server to be inserted into the
        InfluxDB.  This is currently specific to all data excluding
        microphone and camera data.

        return: <class 'bool'>
                When the influx write_points method is called to write
                all points of the json_body to the DB, the result of the
                write (True or False) indicates success or not.  This
                is returned for further processing.
        """
        json_body = []
        count_points = 0
        times= []
        for r in self.get_sensors_response["Readings"]:
            count_points += 1
            json_body.append({
                "measurement": "env_params",
                "tags": {
                    "server_id": self.server_id,
                    "pi_ip_address": self.pi_ip_address,
                    "client_request_time": self.get_sensors_response["Client_Request_Time"],
                    "server_response_time": self.get_sensors_response["Server_Response_Time"]
                },
                "time": r["time"],
                "fields": {
                    "light_lux": int(r["light_lux"]),
                    "temp_c": int(r["temp_c"]),
                    "rh_percent": int(r["rh_percent"]),
                    "dist_mm": int(r["dist_mm"]),
                    "co2eq_ppm": int(r["co2eq_ppm"]),
                    "tvoc_ppb": int(r["tvoc_ppb"]),
                    "co2eq_base": int(r["co2eq_base"]),
                    "tvoc_base": int(r["tvoc_base"])
                }
            })
            times.append(r["time"])
        if self.debug:
            print('{} points to insert into influxdb'.format(count_points))
            print('Times of sensor readings: {}'.format(times))
        if count_points != 12:
            logging.warning('Only {} points to insert into influxdb.'.format(count_points))
            logging.warning('Timestamps of sensor readings: {}'.format(times))
        else:
            logging.info('{} points inserted'.format(count_points))
        return(self.influx_client.write_points(json_body))

    def restart_dat_service(self):
        r = ['restart']
        # Instantiate IPV4 TCP socket class
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Create a socket connection to the server at the specified port
            s.connect((self.pi_ip_address, self.listen_port))

            # Send message over socket connection, requesting aforementioned data
            s.sendall(self.create_message(r))
            
            # Receive all data from server.
            self.restart_response = self.my_recv_all(s).split('\r\n')

            logging.warning('Telling pi to restart - not getting correct data. Pi response: {}'.format(self.restart_response))
            if self.debug:
                print('Telling pi to restart - not getting correct data. Pi response: {}'.format(self.restart_response))

            # Close socket
            s.close()

        except Exception as e:
            logging.warning('Exception occured when telling pi to restart.  Exception: {}'.format(e))
            if self.debug:
                print('Attempted to restart, appears unsuccessful')
            if s:
                try:
                    s.close()
                except:
                    pass
        if s:
            try:
                s.close()
            except:
                pass

    def get_sensors_data(self):
        """
        Connect to server and get data.  This is currently specific to
        all data excluding the microphone and camera.
        """
        # Instantiate IPV4 TCP socket class
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Create a socket connection to the server at the specified port
            s.connect((self.pi_ip_address, self.listen_port))

            # Send message over socket connection, requesting aforementioned data
            s.sendall(self.create_message(["env_params"]))

            try:
                # Receive all data from server.  Load as dictionary
                self.get_sensors_response = json.loads(self.my_recv_all(s))
            except json.decoder.JSONDecodeError as e:
                logging.warning('Unable to decode JSON from server.  Exception: {}'.format(e))
                
            # Attempt to write to InfluxDB.  Relay success/not to server
            # Upon success, server removes data from cache
            try:
                # influx_write() returns 'bool'
                successful_write = self.influx_write()
                if successful_write:
                    s.sendall(self.create_message(["SUCCESS"]))
                    logging.info('Successful write')
                    if self.debug:
                        print('Successful write to Influx')
                else:
                    s.sendall(self.create_message(["NOT SUCCESS"]))
                    logging.warning('Unsuccessful write to influxdb')
            except:
                s.sendall(self.create_message(["NOT SUCCESS"]))
                logging.warning('Unsuccessful write to influxdb')

            # Check that server received message correctly
            self.validation = self.my_recv_all(s)
            logging.info("Validation: {}".format(self.validation))

            # Close socket
            s.close()

        except (OSError, ConnectionAbortedError, ConnectionError, ConnectionRefusedError, ConnectionResetError, paramiko.ssh_exception.SSHException) as e:
            logging.info('Unable to connect and get_sensors_data. Error: {}'.format(e))
            if self.debug:
                print('Unable to connect and get_sensors_data. Error: {}'.format(e))
            
            try:
                if s:
                    s.close()
            except:
                pass
        if s:
            try:
                s.close()
            except:
                pass

        time.sleep(60)
    
    def server_delete(self):
        logging.info('Starting server_delete Thread')
        if self.debug:
            print('Starting server_delete Thread')
        while True:
            if datetime.now().minute % 5 == 0 and datetime.now().second == 30:
                logging.info('00:30 or 05:30')
                to_remove = ['to_remove']
                for item in self.retriever.successfully_retrieved:
                    to_remove.append(item[0])
                
                if len(to_remove) <= 1:
                    logging.info('Nothing to remove from self.retriever.successfully_retrieved...')
                    pass

                else:
                    # Instantiate IPV4 TCP socket class
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    try:
                        # Create a socket connection to the server at the specified port
                        s.connect((self.pi_ip_address, self.listen_port))

                        # Send message over socket connection, requesting aforementioned data
                        s.sendall(self.create_message(to_remove))

                        # Receive all data from server.
                        self.delete_response = self.my_recv_all(s).split('\r\n')
                        self.num_dirs_deleted = self.delete_response[0]
                        if self.debug:
                            print('{} dirs deleted'.format(self.num_dirs_deleted))

                        if len(self.delete_response) > 1:
                            self.dirs_deleted = self.delete_response[1:]
                            removed_from_queue = 0

                            for d in self.dirs_deleted:
                                for a in self.retriever.successfully_retrieved:
                                    if a[0] == d:
                                        ind = self.retriever.successfully_retrieved.index(a)
                                        self.retriever.successfully_retrieved.pop(ind)
                                        removed_from_queue += 1

                            logging.info('{} directories deleted from server'.format(self.num_dirs_deleted))
                            logging.info('{} directories removed from queue'.format(removed_from_queue))
                            logging.info('Dirs deleted: {}'.format(self.dirs_deleted))

                            if self.debug:
                                print('{} directories deleted from server'.format(self.num_dirs_deleted))
                                print('{} directories removed from queue'.format(removed_from_queue))

                        # Close socket
                        s.close()

                    except (OSError, ConnectionAbortedError, ConnectionError, ConnectionRefusedError, ConnectionResetError, paramiko.ssh_exception.SSHException) as e:
                        logging.info('Unable to connect and server_delete. Error: {}'.format(e))
                        if self.debug:
                            print('Unable to connect and server_delete. Error: {}'.format(e))
                        try:
                            if s:
                                s.close()
                        except:
                            pass
            
                time.sleep(30)

if __name__ == "__main__":
    """
    The client must be run by specifying a server id. Example:
        client$ python client.py B_S3
    Client is currently set to ping it's specified server
    every 2 minutes, get data, and write to InfluxDB.

    """
    server_id = sys.argv[1]
    debug = True

    # Instantiate client
    c = MyClient(server_id, debug)

    while True:
        # pass
        if datetime.now().minute % c.collect_interval == 0:

            # Wait two seconds before connecting to server
            time.sleep(2)

            # Get data from sensors and save to influxdb
            get_data = threading.Thread(target=c.get_sensors_data())
            get_data.start()
            get_data.join()



