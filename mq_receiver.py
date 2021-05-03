import pika
import json
import models as db
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import myClass as MyC
from sqlalchemy import insert

# ORM Settings
engine = create_engine("sqlite:///my_wow.db")
db.Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db.Base.metadata.create_all(engine)
session_db = DBSession()


def callback(ch, method, properties, body):
    #if "https://eu.api.blizzard.com/data/wow/realm/" in body.decode():
    #    add_realms_to_bd_new(json.loads(body.decode()))
    #    print('     [*] Received realms')

    if "periods" in body.decode():
        add_dungeons_index(json.loads(body.decode()))
        print('     [*] Received period index')

    if "upgrade_level" in body.decode():
        add_dungeons_to_bd_new(json.loads(body.decode()))
        print('     [*] Received Dungeons')

    if "spec_icon" in body.decode():
        add_spec_to_bd(json.loads(body.decode()))
        print('     [*] Received Class specialization')

    if "faction" in body.decode():
        #print(json.loads(body.decode()))
        print('     [*] Received LeaderBoard')
        add_leader_to_bd(json.loads(body.decode()))

    if "UrlKey" in body.decode():
        add_url_log(json.loads(body.decode()))
        print('     [*] Received Url log')


    ch.basic_ack(delivery_tag=method.delivery_tag)


# add realms in bd
def add_realms_to_bd_new(realms):
    for realm in realms["realms"]:
        server = db.Realm(server_id=realm["id"], server_name=realm["slug"])
        session_db.merge(server)
    session_db.commit()


# add dungeon index in bd
def add_dungeons_index(index_dungeon):
    for index in index_dungeon["periods"]:
        server = db.PeriodsIndex(index_id=index["id"])
        session_db.merge(server)
    session_db.commit()


# add dungeon in bd
def add_dungeons_to_bd_new(dungeon):
    server = db.Dungeon(
        dungeon_id=dungeon["dungeon_id"],
        dungeon_name=dungeon["dungeon_name"],
        upgrade_level=dungeon["upgrade_level"],
        upgrade_leve2=dungeon["upgrade_level2"],
        upgrade_leve3=dungeon["upgrade_level3"], )
    session_db.merge(server)
    session_db.commit()


# add spec in bd
def add_spec_to_bd(final_specs):
    server = db.Character_specializations(
        spec_id=final_specs["spec_id"],
        spec_name=final_specs["spec_name"],
        spec_type=final_specs["spec_type"],
        spec_class=final_specs["spec_class"],
        spec_icon=final_specs["spec_icon"],)
    session_db.merge(server)
    session_db.commit()

def add_leader_to_bd(leaders):
    result=[]
    member = {}
    member["duration"] = leaders["map_challenge_mode_id"]
    for x in leaders["leading_groups"]:
        member["duration"] = x["duration"]
        member["completed_timestamp"] = x["completed_timestamp"]
        member["keystone_level"] = x["keystone_level"]
        member["keystone_id"] = leaders["map_challenge_mode_id"]
        for profile in x["members"]:
            member["player_id"] = profile["profile"]["id"]
            member["player_name"] = profile["profile"]["name"]
            member["player_server"] = profile["profile"]["realm"]["id"]
            member["player_faction"] = profile["faction"]["type"]
            member["player_specialization"] = profile["specialization"]["id"]
            result.append(MyC.Leaderboard(**member))
    for lead in result:
        server = db.Leaderboard(
            duration=lead.duration,
            completed_timestamp=lead.completed_timestamp,
            keystone_level=lead.keystone_level,
            keystone_id=lead.keystone_id,
            player_id=lead.player_id,
            player_name=lead.player_name,
            player_server=lead.player_server,
            player_faction=lead.player_faction,
            player_specialization=lead.player_specialization,
        )
    session_db.merge(server)
    session_db.commit()



def add_url_log(url_s):
    server_url = db.Url_log(url=url_s["UrlKey"], url_state=url_s["State"])
    session_db.add(server_url)
    session_db.commit()


connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
channel = connection.channel()

channel.queue_declare(queue="iloverabbit", durable=True)
print(' [*] Waiting for messages. To exit press CTRL+C')

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue="iloverabbit", on_message_callback=callback)
channel.start_consuming()

