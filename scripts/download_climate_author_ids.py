#from delab.corpus.download_author_information import update_is_climate_author
import yaml
from yaml.loader import SafeLoader


def run():
    #update_is_climate_author(read_yaml('en'))
    print(read_yaml('en'))

def read_yaml(lang):
    if lang == 'ger':
        with open('twitter/strategic_communication/climate_change.yaml') as file:
            data = yaml.load(file, Loader=SafeLoader)
            accounts = []
    else:
        with open('twitter/strategic_communication/climate_change_en.yaml') as file:
            data = yaml.load(file, Loader=SafeLoader)
            accounts = []
    for key in data:
        data2 = data[key]
        for key2 in data2:
            for key3 in key2:
                values = list(key2[key3].values())
                account_name = (values[1])
                if account_name is not None and len(account_name) > 0:
                    accounts.append(account_name)
    return accounts

