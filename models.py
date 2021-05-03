from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Realm(Base):
    __tablename__ = "realm"

    server_id = Column(Integer, primary_key=True)
    server_name = Column(String(250), nullable=False)


class Url_log(Base):
    __tablename__ = "url_log"

    url_id = Column(Integer, autoincrement=True, primary_key=True)
    url = Column(String(250), nullable=False)
    url_state = Column(Integer, nullable=False)


class PeriodsIndex(Base):
    __tablename__ = "periodsindex"
    index_id = Column(Integer, primary_key=True)


class Dungeon(Base):
    __tablename__ = "dungeon"

    dungeon_id = Column(Integer, primary_key=True)
    dungeon_name = Column(String(250), nullable=False)
    upgrade_level = Column(Integer, nullable=False)
    upgrade_leve2 = Column(Integer, nullable=False)
    upgrade_leve3 = Column(Integer, nullable=False)


class Character_specializations(Base):
    __tablename__ = "character_specializations"

    spec_id = Column(Integer, primary_key=True)
    spec_name = Column(String(50), nullable=True)
    spec_type = Column(String(25), nullable=True)
    spec_class = Column(String(50), nullable=True)
    spec_icon = Column(String(250), nullable=True)


class Leaderboard(Base):
    __tablename__ = "leaderboard"
    duration = Column(Integer, primary_key=True)
    completed_timestamp = Column(Integer, primary_key=True)
    keystone_level = Column(Integer)
    keystone_id = Column(Integer)
    player_id = Column(Integer, primary_key=True)
    player_name = Column(String(100))
    player_server = Column(Integer)
    player_faction = Column(String(100))
    player_specialization = Column(Integer)
