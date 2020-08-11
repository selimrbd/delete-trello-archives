from pathlib import Path
import json
import time
from datetime import datetime
import grequests
import requests

path_trello_creds = Path('.trello')
path_logs = Path(f"./logs/delete-trello-archives_{datetime.now().strftime('%Y%m%d%H%M%S_')}.log")

## get trello credentials.
## should be in ~/.trello, with the following format:
#key=...
#token=...
with open(path_trello_creds, 'r') as f:
    c = f.read()
creds_key = c.split('\n')[0].split('=')[1]
creds_token = c.split('\n')[1].split('=')[1]

### utility function
def get_archived_cards(key, token, query='is:archived', cards_limit=1000, verbose=1):
    if verbose > 0:
        print('getting list of archived cards...')
    params = {'key':creds_key, 'token':creds_token, 'query':query, 'cards_limit':cards_limit}
    url_search = 'https://api.trello.com/1/search'
    r = requests.get(url_search, params=params)
    if verbose > 0:
        print(r)
    out = json.loads(r.text)
    return(out['cards'])


if __name__ == '__main__':
    total_cards_processed = 0
    nb_batch = 100
    sleep_sec = 10
    params = {'key':creds_key, 'token':creds_token}
    logs = list()

    try:
        cards = get_archived_cards(creds_key, creds_token)
        while len(cards) > 0:
            print(f'found {len(cards)} cards archived (maximum of 1000 cards / request)')
            cards_id = [c['id'] for c in cards]
            cards_name = [c['name'] for c in cards]
            nb_batchs = (len(cards) // nb_batch) + 1*(len(cards)%nb_batch > 0)
            print(f'nb of batches: {nb_batchs}')

            for i in range(nb_batchs):
                tmp_ids = cards_id[i*nb_batch:min((i+1)*nb_batch, len(cards))]
                tmp_names = cards_name[i*nb_batch:min((i+1)*nb_batch, len(cards))]
                urls = [f'https://api.trello.com/1/cards/{cid}' for cid in tmp_ids]
                async_list = [grequests.request('DELETE', u, params=params) for u in urls]
                print(f'running {len(async_list)} requests asynchronously')
                outputs = grequests.map(async_list)
                total_cards_processed += len(async_list)
                for (cid, name, r) in zip(tmp_ids, tmp_names, outputs):
                    logs.append({'id': cid, 'name': name, 'response':r})
                print(f'sleeping for {sleep_sec} seconds...')
                time.sleep(sleep_sec)

            print(f'updating list of archived cards...')
            cards = get_archived_cards(creds_key, creds_token)
            time.sleep(sleep_sec)
    except Exception as e:
        print(f'Exception ({type(e)}): {e}')
    finally:
        # assert len(logs) == total_cards_processed
        nb_success = len([l for l in logs if l['response'].status_code == 200])
        errors = [l for l in logs if l['response'].status_code != 200]
        print(f'total nb of cards processed: {total_cards_processed}')
        print(f'successful processing: {nb_success}/{total_cards_processed}')
        strs = [f"{l['id']},{l['name']},{l['response'].status_code}" for l in logs]
        log_str = '\n'.join(strs)
        print('***********')
        print(f'saving logs to {path_logs}')
        print('***********')
        with open(path_logs, 'w') as f:
            f.write(log_str)
