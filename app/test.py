import yaml

def load_yaml_with_defaults(file_path):
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
        return config

document = 'config.yaml'
statsDict = {'targetSpeed' : 0, 'currentSpeed' : 0, 'rpm' : 0, 'dropsAmount' : 0, 'vaccinationsAmount' : 0}

with open(document, "r") as file:
    settingsDict = yaml.safe_load(file)



print (settingsDict)