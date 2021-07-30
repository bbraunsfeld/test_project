#packages
import os
import yaml
from dataclasses import dataclass
from dacite import from_dict

#stuff
def get_bin_dir():
    """Returns the bin directory of this package"""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), 'bin'))


def get_toppar_dir():
    """Returns the toppar directory of this package"""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), 'toppar'))

def load_config_yaml(config, input_dir, output_dir):

    with open(f"{config}", 'r') as stream:
        try:
            settingsMap = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    # set the bin, data and analysis dir
    settingsMap['bin_dir'] = get_bin_dir()
    print (settingsMap['bin_dir'])
    settingsMap['analysis_dir_base'] = os.path.abspath(f"{output_dir}")
    settingsMap['data_dir_base'] = os.path.abspath(f"{input_dir}")
    system_name = f"{settingsMap['system']['structure']['name']}"
    settingsMap['system_dir'] = f"{settingsMap['analysis_dir_base']}/{system_name}"
    settingsMap['cluster_dir'] = f"/data/local/{system_name}"

    settingsMap['system']['name'] = system_name

    return settingsMap

class CodeBlock():
    
    def __init__(self, head, block):
        self.head = head
        self.block = block
        
    def __str__(self, indent=""):
        result = indent + self.head + ':\n'
        indent += '    '
        for block in self.block:
            if isinstance(block, CodeBlock):
                result += block.__str__(indent)
            else:
                result += indent + block + '\n' 
        return result
    
    
def class_code(configuration, total_code, in_secondary_loop = False):
    if isinstance(configuration, dict):
        for key, value in configuration.items():
            head = '@dataclass' + '\n' + 'class ' + str(key)
            block = []
            if isinstance(value, dict):   
                for key1, value1 in value.items(): 
                    if isinstance(value1, dict): 
                        block.append(str(key1) + ':' + ' ' + str(key1))
                    elif not isinstance(value1, dict):
                        value_type = str(type(value1)).split("'")[1]
                        block.append(str(key1) + ':' + ' ' + value_type)        
                total_code = str(CodeBlock(head,block)) + total_code
                total_code = class_code(value,total_code='', in_secondary_loop = True) + total_code
                in_secondary_loop = False
            elif not isinstance(value, dict):
                pass
                #if in_secondary_loop == False:
                    #value_type = str(type(value)).split("'")[1]
                    #block.append(str(key) + ':' + ' ' + value_type)
                    #total_code = str(CodeBlock(head,block)) + total_code
                #else:
                    #pass
            else:
                print ('type error')
                #logger.info("Unsupported Type")
    return total_code


class create_dataclass_file(object):

    def __init__(self, configuration):
        self.configuration = configuration
        self.results = self.__structure__(self.configuration)
        self.__parser__(self.results)
       
    def __structure__(self, configuration):        
        self.total_code = ''
        self.code = str(class_code(self.configuration,self.total_code))
        self.setup = 'from dataclasses import dataclass' + '\n' + '\n' + '#dataclass' + '\n'
        self.results = self.setup + self.code
        return self.results

    def __parser__(self, results):
        file_path = os.getcwd()
        file_name = '/src/bin/dataclass.py'
        tmp_path = file_path + file_name
        
        try:
            with open(tmp_path, 'w') as f:
                f.write(self.results)
                f.close()
        except IOError:
            print(f"Data class could not be created: {file_name}")
            #logger.info(f"Data class could not be created: {file_name}")
            pass

def fill_dataclass(input_dataclass,configuration):
    filled_class = from_dict(data_class=input_dataclass, data=configuration)
    return filled_class