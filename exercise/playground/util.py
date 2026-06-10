import os
import yaml

APP_ENV = os.getenv('APP_ENV', '.env')

def read_env():
    with open(APP_ENV, 'r') as fin:
        for line in fin.readlines():
            if (line.strip() or '#').startswith('#'):
                continue
            var, value = line.split('=')
            os.environ[var] = value.split('\n')[0]

def load_yaml(filename):
    with open(filename) as fin:
        data = yaml.safe_load(fin)
    return data