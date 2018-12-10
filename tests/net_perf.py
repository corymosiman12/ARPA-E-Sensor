    
class MyNetworkChecker()
    def __init__(self, path_to_import_conf, write_file, display_output, server_id):
        self.conf_file_path = path_to_import_conf
        self.import_conf(self.conf_file_path)
        
    def import_conf(self, path):
        with open(path, 'r') as f:
            self.conf_dict = json.loads(f.read())