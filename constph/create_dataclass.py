from constph import load_config_yaml
from constph import create_dataclass_file

   
configuration = load_config_yaml(config='constph/bin/dataclass_structure.yaml',
                                   input_dir='.', output_dir='constph/bin/')

configuration = {'input_dataclass': configuration}

create_dataclass_file(configuration)