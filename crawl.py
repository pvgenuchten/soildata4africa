import pandas as pd
import os, yaml, json, re 
import requests as req
from yaml.loader import SafeLoader
from lxml import html


source = "."
target = "./portals"

def create_initial(path,id,label,desc,url):
    cnf = {
        "identifier": id,
        "url": url,
        "name": label,
        "abstract": desc,
        "contact": {
            "name": "",
            "organisation": "",
            "email": ""},
        "license": ""
    }
    try:
        with open(path, 'w') as f:
            yaml.dump(cnf, f)
    except Exception as e:
        print('file '+ path +' can not be written, check it; '+ e)
   

myPortals = pd.read_csv(source+os.sep+'portals.csv')
for index, row in myPortals.iterrows():
    print(row['url'], row['label'])
    
    # we should check the url, maybe the url is forwarded (from doi, or no longer existing location)
    try:
        resp = req.get(row['url'])
    except Exception as e:
        print('request to ' + row['url'] + ' failed');
        continue
    
    # then check resp.url
    # get domain as identifier for the catalogue (if multiple catalogues live in a domain, they are merged)
    domain = resp.url.split('//')[1].split('/')[0]
    print(domain)

    # check if domain-folder exists, else create it
    if os.path.isdir(target+os.sep+domain):
        # already exits; update metadata
        print(target+os.sep+domain+' already exits')
        try:
            with open(os.path.join(target+os.sep+domain+os.sep, 'index.yml')) as f:
                portalMD = yaml.load(f, Loader=SafeLoader)
        except FileNotFoundError:  # filenotfound, create it
            create_initial(os.path.join(target+os.sep+domain+os.sep, 'index.yml'),domain,row.get('label'),row.get('desc'),resp.url)
        except Exception as e:
            print('file '+ os.path.join(target+os.sep+domain+os.sep, 'index.yml') +' can not be read, check it; '+ e)
    else:
         os.makedirs(target+os.sep+domain)
         create_initial(os.path.join(target+os.sep+domain+os.sep, 'index.yml'),domain,row.get('label'),row.get('desc'),resp.url)

    ## FETCH PORTAL METADATA
    #try:
    abs = ""
    content_type = resp.headers['content-type'].split(';')[0]
    print(content_type)
        # if website, check title/abstract, schema-org or similar
    if (content_type == 'text/html'):
        print('html')
        tree = html.fromstring(resp.content)
        ttl = tree.xpath('//title[0]/text()')
        abs = tree.xpath('//meta[@name="description"]/@content/text()')
        if len(abs) == 0:
            abs = tree.xpath('//meta[@name="og:description"]/@content/text()')
        if len(abs) > 0:
            abs=abs[0]
        else:
            abs=""
        schemaorg = tree.xpath('//script[@type="application/ld+json"]/text()')
        if len(schemaorg) > 0:
            schemaorg = json.loads(schemaorg[0])
            ttl = schemaorg.get('name',ttl)
            abs = schemaorg.get('description',abs)
        print(abs) 
    elif (content_type == 'application/json'):    # if API, identify the type of API, if it is OPENAPI, CSW, OAI-PMH, Dataverse, CKAN, WMS/WFS fetch metadata from conventions
        print('json')
        # see if it is openapi, json-ld, odata, ...
        ttl=resp.url.split('/')[-1].split('?')[0].split('#')[0]
        if not ttl:
            ttl = domain
    elif (content_type in ['text/xml','application/xml']):
        print('xml')
        # see if it is wms/wfs/iso/wcs/csw etc
        ttl=resp.url.split('/')[-1].split('?')[0].split('#')[0]
        if not ttl:
            ttl = domain
    else:
        ttl=resp.url.split('/')[-1].split('?')[0].split('#')[0]
        if not ttl:
            ttl = domain
        print('other: '+ content_type)
    
    # create safe folder name (or use identifier, if we know it)

    fldrnm = "".join([c for c in ttl if re.match(r'\w', c)])
    fldr = target+os.sep+domain+os.sep+'datasets'+os.sep+fldrnm

    if os.path.isdir(fldr):
        print('folder '+ fldr +' exists')
    else:
        os.makedirs(fldr)
        if (schemaorg):
            with open(os.path.join(fldr+os.sep, 'index.yml'), 'w') as f:
                yaml.dump(schemaorg, f)
        else:
            create_initial(os.path.join(fldr+os.sep, 'index.yml'),fldrnm,ttl,abs,resp.url)



        # print(resp.text) # Printing response

        # see if the row includes a doi, if so fetch the doi metadata (datacite)

        ## Maybe the row has a dataset on an existing portal, always add a dataset folder, initially and next for second, third

    #except Exception as e:
    #        print(e)
    
