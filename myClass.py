class DungeonObject:
    def __init__(
        self, dungeon_id, dungeon_name, upgrade_level, upgrade_level2, upgrade_level3
    ):
        self.dungeon_id = dungeon_id
        self.dungeon_name = dungeon_name
        self.upgrade_level = upgrade_level
        self.upgrade_level2 = upgrade_level2
        self.upgrade_level3 = upgrade_level3


class ClassSpecialization:
    def __init__(self, spec_id, spec_name, spec_type, spec_class, spec_icon):
        self.spec_id = spec_id
        self.spec_name = spec_name
        self.spec_type = spec_type
        self.spec_class = spec_class
        self.spec_icon = spec_icon


class Leaderboard:
    def __init__(
        self,
        duration,
        completed_timestamp,
        keystone_level,
        keystone_id,
        player_id,
        player_name,
        player_server,
        player_faction,
        player_specialization,
    ):
        self.duration = duration
        self.completed_timestamp = completed_timestamp
        self.keystone_level = keystone_level
        self.keystone_id = keystone_id
        self.player_id = player_id
        self.player_name = player_name
        self.player_server = player_server
        self.player_faction = player_faction
        self.player_specialization = player_specialization
