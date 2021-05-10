from pony.orm import Database, Required, Json

from settings import DB_CONFIG

db = Database()
db.bind(**DB_CONFIG)


class UserState(db.Entity):
    user_id = Required(str, unique=True)
    scenario_name = Required(str)
    step_name = Required(str)
    context = Required(Json)


class Registration(db.Entity):
    data = Required(str)
    town_from = Required(str)
    town_end = Required(str)
    phone = Required(str)
    reis = Required(str)
    place = Required(str)
    comment = Required(str)
    answer = Required(str)


db.generate_mapping(create_tables=True)
