import requests
import time
import myClass as MyC
import pika
import json
import models as db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from multiprocessing.dummy import Pool as ThreadPool

# threadPool setting
pool = ThreadPool(10)

# Settings for token
client_id = "2de30865a7884bfda49b23fc398c639a"
client_secret = "8D4F9eD4sm8TxYpZ1CLJ07uFXIyl7ivB"
token_url = "https://eu.battle.net/oauth/token"


# ORM Settings
engine = create_engine("sqlite:///my_wow.db")
db.Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db.Base.metadata.create_all(engine)
session_db = DBSession()


# give my token plz
def create_access_token(client_ids, client_secrets):
    data = {"grant_type": "client_credentials"}
    response = requests.post(token_url, data=data, auth=(client_ids, client_secrets))

    if response.status_code == 200:
        print("Create_access_token:", response.status_code)
        return response.json()
    else:
        print("Create_access_token:", response.status_code)


# get server list
def get_realms(access_token):
    response = requests.get(
        "https://eu.api.blizzard.com/data/wow/realm/index?namespace=dynamic-eu&locale=eu_EU&access_token={}".format(
            access_token
        )
    )
    if response.status_code == 200:
        print("Get_realms:", response.status_code)
        return response.json()
    else:
        print("Get_realms:", response.status_code)


# get id class spec
def get_spec(access_token):
    response_spec = requests.get(
        "https://us.api.blizzard.com/data/wow/playable-specialization/index?namespace=static-us&locale=en_US&access_token={}".format(
            access_token
        )
    )
    if response_spec.status_code == 200:
        print("Get_spec:", response_spec.status_code)
        return response_spec.json()
    else:
        print("Get_spec:", response_spec.status_code)


# get details spec1
def get_spec2(specs):
    start_time = time.perf_counter()
    list_url = []
    for spec in specs["character_specializations"]:
        list_url.append(
            "https://eu.api.blizzard.com/data/wow/playable-specialization/{}?namespace=static-eu&locale=en_US&access_token={}".format(
                spec["id"], token["access_token"]
            )
        )
    results = pool.map(threadpool_geturl, list_url)
    print("Time get_spec2:", time.perf_counter() - start_time)
    return results


# get details spec2
def get_spec3(specs):
    start_time = time.perf_counter()
    list_url = []
    for spec in specs["character_specializations"]:
        list_url.append(
            "https://us.api.blizzard.com/data/wow/media/playable-specialization/{}?namespace=static-us&locale=en_US&access_token={}".format(
                spec["id"], token["access_token"]
            )
        )
    results = pool.map(threadpool_geturl, list_url)
    print("Time get_spec3:", time.perf_counter() - start_time)
    return results


# group details spec
def make_spec(specs, specs2, specs3):
    result = []
    for spec in specs["character_specializations"]:
        for spec2 in specs2:
            if spec2["id"] == spec["id"]:
                for spec3 in specs3:
                    if spec3["id"] == spec["id"]:
                        class_spec = MyC.ClassSpecialization(
                            spec["id"],
                            spec["name"],
                            spec2["role"]["name"],
                            spec2["playable_class"]["name"],
                            spec3["assets"][0]["value"],
                        )
                        result.append(class_spec)
    return result


# get dungeon index
def get_dungeon_index(access_token):
    response_spec = requests.get(
        "https://eu.api.blizzard.com/data/wow/mythic-keystone/period/index?namespace=dynamic-eu&locale=eu_EU&access_token={}".format(
            access_token
        )
    )
    if response_spec.status_code == 200:
        print("Get_dungeon_index:", response_spec.status_code)
        return response_spec.json()
    else:
        print("Get_dungeon_index:", response_spec.status_code)


# Получаем id подземелей
def get_dungeons_id(access_token):
    response = requests.get(
        "https://eu.api.blizzard.com/data/wow/mythic-keystone/dungeon/index?namespace=dynamic-eu&locale=eu_EU&access_token={}".format(
            access_token
        )
    )
    if response.status_code == 200:

        print("Get_dungeons_id:", response.status_code)
        dungeons_id = response.json()

        JsonDungeon = []
        for dungeon_id in dungeons_id["dungeons"]:
            response_dungeon = requests.get(
                "https://eu.api.blizzard.com/data/wow/mythic-keystone/dungeon/{}?namespace=dynamic-eu&locale=eu_EU&access_token={}".format(
                    dungeon_id["id"], access_token
                )
            )

            JsonDungeon.append(
                MyC.DungeonObject(
                    response_dungeon.json()["id"],
                    response_dungeon.json()["zone"]["slug"],
                    response_dungeon.json()["keystone_upgrades"][0][
                        "qualifying_duration"
                    ],
                    response_dungeon.json()["keystone_upgrades"][1][
                        "qualifying_duration"
                    ],
                    response_dungeon.json()["keystone_upgrades"][2][
                        "qualifying_duration"
                    ],
                )
            )
        return JsonDungeon
    else:
        print("Get_dungeons:", response.status_code)


# Получаем JSONы лидеров за весь период
def get_Leaderboard(token):
    created_url = []
    bad_url = []
    for bad in session_db.query(db.Url_log):
        bad_url.append(bad.url)

    for realm in session_db.query(db.Realm):  # .filter(db.Realm.server_id == 1615):
        for dungeon in session_db.query(db.Dungeon):
            for index in session_db.query(
                db.PeriodsIndex
            ):  # .filter(db.PeriodsIndex.index_id == 798):  # 774
                created_url.append(
                    "https://eu.api.blizzard.com/data/wow/connected-realm/{}/mythic-leaderboard/{}/period/{}?namespace=dynamic-eu&locale=en_EU&access_token=".format(
                        realm.server_id, dungeon.dungeon_id, index.index_id
                    )
                )

    print("created_url_good:", len(created_url))
    created_url_good=(set(created_url) - set(bad_url))

    finish_url=[]
    for url in created_url_good:
        finish_url.append(url+token)

    print("finish_url:", len(finish_url))

    leaders = pool.map(threadpool_geturl, finish_url)



# worker of year
def threadpool_geturl(url):
    response_spec = requests.get(url)
    rabbit_publisher({"UrlKey": url[:-34], "State": response_spec.status_code})
    if response_spec.status_code == 200:

        rabbit_publisher(response_spec.json())

        return response_spec.json()
    else:
        print("threadpool_get_url:", response_spec.status_code)



# message to rabbit
def rabbit_publisher(msg_to_rabbit):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()
    channel.queue_declare(queue="iloverabbit", durable=True)
    channel.basic_publish(exchange="", routing_key="iloverabbit", body=json.dumps(msg_to_rabbit),
                          properties=pika.BasicProperties(delivery_mode=2))

    connection.close()


# get token
token = create_access_token(client_id, client_secret)

# get server
realms = get_realms(token["access_token"])

# get spec
specs = get_spec(token["access_token"])
specs2 = get_spec2(specs)
specs3 = get_spec3(specs)
group_spec_details = make_spec(specs, specs2, specs3)

# get index
index_dungeon = get_dungeon_index(token["access_token"])

# get dungeon
dungeons_id = get_dungeons_id(token["access_token"])

# get leaderboard
get_Leaderboard(token["access_token"])

# send to rabbit realms info
rabbit_publisher(realms)

# send to rabbit dungeon index
rabbit_publisher(index_dungeon)

# send to rabbit dungeon id
for dungeon in dungeons_id:
    rabbit_publisher(dungeon.__dict__)

# send to rabbit spec info
for spec_id in group_spec_details:
    rabbit_publisher(spec_id.__dict__)
