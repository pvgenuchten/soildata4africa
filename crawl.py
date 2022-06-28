import pandas as pd
import os, yaml 
import requests as req
from yaml.loader import SafeLoader


source = "."
target = "./portals"

myPortals = pd.read_csv(source+os.sep+'portals.csv')
for index, row in myPortals.iterrows():
    print(row['url'], row['label'])
    # get domain as identifier for the catalogue (if multiple catalogues live in a domain, they are merged)
    domain = row['url'].split('//')[1].split('/')[0]
    # check if domain-folder exists, else create it
    if os.path.isdir(target+os.sep+domain):
        # already exits; update metadata
        print(target+os.sep+domain+' already exits')
        try:
            with open(os.path.join(target+os.sep+domain+os.sep, 'index.yml')) as f:
                portalMD = yaml.load(f, Loader=SafeLoader)
        except Exception as e:
            print(e)
    else:
         os.makedirs(target+os.sep+domain)
    ## FETCH PORTAL METADATA
    try:
        resp = req.get(row['url'])
        content_type = resp.headers['content-type'].split(';')[0]
        print(content_type)
         # if website, check title/abstract, schema-org or similar
        if (content_type == 'text/html'):
            print('html')
        elif (content_type == 'application/json'):    # if API, identify the type of API, if it is OPENAPI, CSW, OAI-PMH, Dataverse, CKAN, WMS/WFS fetch metadata from conventions
            print('json')
        elif (content_type in ['text/xml','application/xml']):
            print('xml')
        else:
            print('other: '+ content_type)
        
        print(resp.text) # Printing response

        # see if the row includes a doi, if so fetch the doi metadata (datacite)

        ## Maybe the row has a dataset on an existing portal, always add a dataset folder, initially and next for second, third

    except Exception as e:
            print(e)
    
   
