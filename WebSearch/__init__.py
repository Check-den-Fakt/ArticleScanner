import logging
import requests
import json
import azure.functions as func
from urllib.parse import urlsplit
import re


sub_key_search = 'enter_key'
sub_key_trusted = "enter_key"


search_url = 'https://westeurope.api.cognitive.microsoft.com/bing/v7.0/search?'

mkt = 'de-DE'
count = '10'
offset = '0'
safesearch = "None"


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
    except ValueError:
        pass
    
    search_term = req_body.get('text')

    if search_term is not None:

        params = {
            "q": search_term, "count": count,"offset": offset, "mkt": mkt#, "safesearch" : safesearch
            }
    
        search_results = get_resp(search_url,get_header(sub_key_search),params)

        links = process_search_results(search_results,get_header(sub_key_trusted))
        
        resp = {
            "Query" : search_term,
            "Links" : links
        }

        return func.HttpResponse( 
            json.dumps(resp),
            mimetype="application/json"
            )
    else:
        return func.HttpResponse(
             "Please pass a name on the query string or in the request body",
             status_code=400
        )




def get_resp(url,header,params):
    response = requests.get(url, headers=header, params=params)
    response.raise_for_status()
    results = response.json()
    return results

def post_resp(url,header,body):
    response = requests.post(url, headers=header, json=body)
    response.raise_for_status()
    results = response.json()
    return results



def process_url(url):
    domain = "{0.scheme}://{0.netloc}".format(urlsplit(url))
    return(domain)

def get_trusted_score(url,header):
    trusted_url = "enter_url"
    body = {
        "url":url
    }
    try:
        score = post_resp(trusted_url,header,body)["trustScore"]
    except:
        score = "not found"
    return score

def process_search_results(search_results,header):
    links = []
    for element in search_results["webPages"]["value"]:
        url = process_url(element["url"])
        score = get_trusted_score(url,get_header(sub_key_trusted))

        body = {
                "domain" : url,
                "trustScore" : score,
                "url" : element["url"],
                "snippet" : element["snippet"]
                }
        if body not in links:
            links.append(body)

    return links


def get_header(key):
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        'content-type': 'application/json'
    }
    return headers 

