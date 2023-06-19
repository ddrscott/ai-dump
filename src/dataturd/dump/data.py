import os
import json

es_url = os.environ.get('ELASTIC_URL', 'localhost')
es_user = os.environ.get('ELASTIC_USER', 'not_set')
es_pass = os.environ.get('ELASTIC_PASS', 'not_set')

from elasticsearch import Elasticsearch

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set up Elasticsearch client
es = Elasticsearch([es_url], basic_auth=(es_user, es_pass), verify_certs=False)

chat_index = 'chats-v3'

def log_chat(doc:dict):
    es.index(index=chat_index, body=doc)

def recent_chats(limit:int=20):
    res = es.search(index=chat_index,
                    query={"match_all": {}},
                    size=limit,
                    sort=[{"timestamp": {"order": "desc"}}])
    return res['hits']['hits']


def row_to_markdown(row):
    content = [
            f"\n> {h['content']} \n" if h['role'] == 'human' else f"{h['content']}"
            for h in json.loads(row['history'])
    ] + ['\n' + row['answer']]

    return ''.join(content)
