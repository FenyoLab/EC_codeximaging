# Description: Helper functions for project

def load_yaml_file(yaml_file):
    #load the config file
    import yaml
    with open(yaml_file, 'r') as f:
        yaml_dict = yaml.safe_load(f)
    return yaml_dict