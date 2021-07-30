from utils import load_config_yaml
from utils import create_dataclass_file

   
configuration = load_config_yaml(config='src/bin/dataclass_structure.yaml',
                                   input_dir='.', output_dir='src/bin/')

configuration = {'input_dataclass': configuration}

create_dataclass_file(configuration)