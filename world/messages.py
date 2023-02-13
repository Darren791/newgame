
# Things.
GET = "You get %T."
OGET = "%N picks up %T."
GET_FAILED = "You cannot pick that up."
OGET_FAILED = ""
DROP_FAILED = ""
DROP = "You dropped %T."
ODROP = "dropped %T."
ODROP_FAILED = ""
RECEIVE = "You receive %T from %I."
ORECEIVE = ""

# Rooms.
VICTIM_EJECTION = ""
EJECTION = ""
OEJECTION = ""
ARRIVE = "You arrive at %T."
OARRIVE = "arrives from %I."
BAN = "You ban %T."
OBAN = ""

# Players.
#ARRIVE = ""
#OARRIVE = ""

# Exits.
LEAVE = "You leave %L."
OLEAVE = ""
NOGO = "You can't go that way."
ONOGO = ""

# Places.
JOIN = "You sit at %T."
OJOIN = "sits at %T."
DEPART = "You leave %T."
ODEPART = "leaves %T."

PLACE_MESSAGES = ("join", "ojoin", "depart", "odepart", "ban", "oban")
OBJECT_MESSAGES = ("get", "drop", "oget", "odrop", "get_failed", "drop_failed", "oget_failed", "receive", "oreceive")
ROOM_MESSAGES = ("victim_ejection", "ejection", "oejection", "arrive", "oarrive")
CHARACTER_MESSAGES = ("teleport", "oteleport")
EXIT_MESSAGES = ("leave", "oleave", "nogo", "onogo")
ALL_MESSAGES = OBJECT_MESSAGES+ROOM_MESSAGES+CHARACTER_MESSAGES+EXIT_MESSAGES+PLACE_MESSAGES
