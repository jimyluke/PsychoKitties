import datetime
import operator
import traceback
from json import JSONDecodeError

import requests

from multiprocessing.pool import ThreadPool

from requests.exceptions import ProxyError, SSLError, ChunkedEncodingError
from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql.dml import Insert
from sqlalchemy.orm import sessionmaker
from urllib3.exceptions import ProtocolError

from application.models import Kitty, History

proxies = {
    'http': 'http://copyken:03b68e-470858-4b873c-b043e8-e9a870@mixed.rotating.proxyrack.net:9000',
    'https': 'http://copyken:03b68e-470858-4b873c-b043e8-e9a870@mixed.rotating.proxyrack.net:9000',
}


class HistoryScheduler:
    def __init__(self, collection):
        self.engine = create_engine(
            'mysql+pymysql://root:4ykcB7qaKdMthnk6@185.202.238.48:3306/psychokitties',
            echo=False)
        Session = sessionmaker(bind=self.engine)

        session = Session()
        self.collection = collection
        self.session = session
        self.saving_arr = []
        self.editions = self.session.query(Kitty).with_entities(Kitty.defaultEditionId) \
            .filter(Kitty.collection == collection).all()

    def save_to_db(self, parsed_events):
        already_there = self.session.query(History).with_entities(History.id).all()
        self.session.commit()
        txs = []
        for x in already_there:
            txs.append(x[0])

        adx = []
        dels = []
        adxa = []
        for event in parsed_events:
            if event['id'] not in adxa:
                history = History(event, self.collection)
                adx.append(history)
                adxa.append(event['id'])
        #stmt = Insert(History).values(adx)
        #stmt = stmt.on_duplicate_key_update(held_until=stmt.inserted.held_until)
        #self.session.execute(stmt)
        for h in adx:
            dels.append(h.id)
        for h in txs:
            dels.append(h)
        self.session.query(History).filter(History.collection==self.collection).delete()
        self.session.commit()
#        self.session.query(History).filter(History.collection==self.collection).delete()
#        self.session.commit()
        self.session.add_all(adx)
        self.session.commit()
        print(f"{self.collection} finished saving at {datetime.datetime.now()}, {len(adx)} new transactions added")

    def parse_events_from_history(self, assetsx, editionId):
        obj = {'editionId': editionId}
        assetsx.sort(key=operator.itemgetter('createdAt'), reverse=True)
        last = datetime.datetime.now().isoformat()
        temp = []
        x = 1
        for holder in assetsx:
            try:
                copy = obj.copy()
                try:
                    copy['username'] = holder['toUser']['id']
                    copy['twitter'] = holder['toUser']['twitterUsername']
                    copy['croWallet'] = holder['toUser']['croWalletAddress']
                except:
                    pass
                copy['bought'] = holder['createdAt']
                copy['held_until'] = last
                try:
                    copy['price'] = holder['listing']['priceDecimal']
                except:
                    pass
                copy['num'] = x
                x = x + 1
                last = holder['createdAt']
                copy['txType'] = holder['nature']
                copy['id'] = holder['id']
                temp.append(copy)
            except Exception as e:
                traceback.print_exc()
            # print(copy)
        added = []
        tampa = []
        for i in range(0, len(temp)):
            tx = temp[i]
            if tx['txType'] == 'withdrawn':
                try:
                    txA = temp[i - 1]
                    txB = temp[i + 1]
                    if txA['username'] == txB['username']:
                        txB['held_until'] = txA['held_until']
                        if txB['num'] not in added:
                            added.append(txB['num'])
                            tampa.append(txB)
                    else:
                        if txB['num'] not in added:
                            added.append(txB['num'])
                            tampa.append(txB)
                        if txA['num'] not in added:
                            added.append(txA['num'])
                            tampa.append(txA)
                except KeyError:
                    if temp[i + 1]['txType'] != 'withdrawn':
                        if temp[i + 1]['num'] not in added:
                            added.append(temp[i + 1]['num'])
                            tampa.append(temp[i + 1])
                    if temp[i - 1]['txType'] != 'withdrawn':
                        if temp[i + 1]['num'] not in added:
                            added.append(temp[i - 1]['num'])
                            tampa.append(temp[i - 1])
                except:
                    traceback.print_exc()
                    print(temp[i - 1])
                    print(temp[i + 1])
                    print(temp[i])
            if tx['txType'] == 'transferred':
                if tx['num'] not in added:
                    tampa.append(tx)
            if tx['txType'] not in ['transferred','withdrawn']:
                if tx['num'] not in added:
                    tampa.append(tx)
        sorted_data = sorted(tampa, key=lambda i: i['num'], reverse=False)
        for x in sorted_data:
            self.saving_arr.append(x)
        return sorted_data

    def get_asset_history(self, edition_id, retry=True):
        try:
            edition_id = str(edition_id).replace("(", "").replace("'", "").replace(",", "").replace(")", "")
            if edition_id is None or str(edition_id) == 'None':
                return []
            # print(edition_id)
            url = "https://crypto.com/nft-api/graphql"

            payload = "{\n\t\"operationName\": \"getAssetEvents\",\n\t\"variables\": {\n\t\t\"editionId\": \"" + edition_id + "\",\n\t\t\"natures\": [\"transferred\", \"airdropped\", \"withdrawn\", \"deposit\"]\n\t},\n\t\"query\": \"fragment UserData on User {\\n  uuid\\n  id\\n  username\\n  displayName\\n  twitterUsername\\n  croWalletAddress\\n  isCreator\\n  avatar {\\n    url\\n    __typename\\n  }\\n  __typename\\n}\\n\\nquery getAssetEvents($editionId: ID, $cacheId: ID, $natures: [String!]) {\\n  public(cacheId: $cacheId) {\\n    assetEvents(natures: $natures, editionId: $editionId) {\\n      id\\n      createdAt\\n      nature\\n      transactionHash\\n      chainEventHash\\n      edition {\\n        id\\n        __typename\\n      }\\n      listing {\\n        priceDecimal\\n        __typename\\n      }\\n      user {\\n        ...UserData\\n        __typename\\n      }\\n      toUser {\\n        ...UserData\\n        __typename\\n      }\\n      nftWithdrawal {\\n        status\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\"\n}"
            headers = {'content-type': 'application/json'}

            response = requests.request("POST", url, headers=headers, data=payload, proxies=proxies)
            assets = response.json()['data']['public']['assetEvents']
            return self.parse_events_from_history(assets, edition_id)
        except TypeError as e:
            print(f"Didn't Find asset events for {edition_id},trying again")
            self.get_asset_history(edition_id, False)
        except ProxyError as e:
            self.get_asset_history(edition_id, True)
        except SSLError as e:
            self.get_asset_history(edition_id, True)
        except ChunkedEncodingError as e:
            self.get_asset_history(edition_id, True)
        except ProtocolError as e:
            self.get_asset_history(edition_id, True)
        except JSONDecodeError as e:
            self.get_asset_history(edition_id, True)
        except Exception as e:
            print(edition_id)
            traceback.print_exc()
            if retry:
                self.get_asset_history(edition_id, False)

    def run(self):
        self.saving_arr = []
        print(f"Starting History fetch for {self.collection} at {datetime.datetime.now()}")
        pool = ThreadPool(90)
        results = pool.map(self.get_asset_history, self.editions)
        pool.close()
        pool.join()

        print(f"Saving {len(self.saving_arr)} results in the database for {self.collection}")
        self.save_to_db(self.saving_arr)
        if self.collection == 'kitty':
            molly_scheduler = HistoryScheduler('molly')
            molly_scheduler.run()

