# text adventure game framework
# contributions by:
# - Tate Rowney
# - Kyler Smith
# - Emmanuel Ezirim

import time
import math


# an instance of this handles all attributes of the playable character (location, inventory, whether the player is
# dead, etc.). For best results, just one of these should be made...
class Player:
    def __init__(self):
        print("Type 'help' for information on how to play.")
        print()
        print(
            "Hello Player! Welcome to Rowell Mansion, aka the Mystery Mansion. 70 years ago, Thomas Rowell went missing, along with his will and the entire Rowell family history. To this day, no one knows where he is, or what happened to the papers. Now, your company is sending you. You’re here to do your job, and do it well. Find those papers, Player.")
        print()
        time.sleep(3)
        print(
            "You stand in front of the Mansion. Cold, clammy tendrils of fog grasp at you. The tall wooden front door hangs ajar.")
        print()
        print(mainHelp)
        print()
        print("""
|_____________[     ]________________|
               - - -                  
                - - -""")
        # inventory format: {instance, count}
        self.inventory = {}
        self.location = STARTROOM
        self.prev_location = None
        self.onDeathLocation = rooms["foyer"]  # when the player dies, they'll go here
        # append to these arrays pointers to any functions which need to be run when the player Moves or Uses any
        # item use the globally defined instance of this class (called "PLAYER") to access specifics about where they
        # are/what they're carrying
        self.onMove = []
        self.onUse = []

    # add an item to player's inventory
    # if you want to add more than 1, change the value of "count"
    def add_item(self, item, count=1):
        if isinstance(item, str):
            self.inventory[items[item.lower()]] = count
        else:
            self.inventory[item] = count

    # remove an item from player's inventory specify an integer instead to "count" to remove that number of the item (
    # removing more than the player has will simply erase that item)
    def remove_item(self, item, count="all"):
        if isinstance(item, str):
            item = items[item.lower()]
        if count == "all":
            count = self.inventory[item]
        self.inventory[item] -= count
        if self.inventory[item] <= 0:
            del self.inventory[item]

    # to kill the player, run this method
    # TODO: change it to what people decide on for death mechanics (does dying reset progress, or inventory?)
    def kill(self):
        print()
        self.location = self.onDeathLocation

    def win(self):
        roll_credits(0.5)
        global has_won
        has_won = True

    # move the player from their current room to an adjoining room
    def move(self, direction):
        if self.location.connectingRooms[direction]:
            self.prev_location = self.location
            self.location = self.location.connectingRooms[direction]
            if self.onMove:
                for fxn in self.onMove:
                    fxn()
            print("You move %s" % direction)
            print()
            #            if not self.location.has_been_visited:
            #                self.location.has_been_visited = True
            print(self.location.get_description())
            print()
            print(self.location.format_map())
            return
        else:
            print("You can't go that way.")
            return


# add an instance of this class for each room created
# supply the name of the room which will be printed to the screen to the constructor
# Example: >>> my_bedroom = Room("bedroom")
class Room:
    def __init__(self, name):
        global rooms
        self.name = name.lower()
        self.is_dark = False
        rooms[self.name] = self
        self.items = {}
        self.description = "DEV: This is the generic room description. Change it to make it more interesting!"
        self.connectingRooms = {'north': None, 'east': None, 'west': None, 'south': None, 'up': None, 'down': None}
        self.hint = "Looks like you're on your own for this one..."
        self.enemies = []
        self.has_been_visited = False
        self.map = """DEV: change this please"""

    # place an item in the room supply the name or a pointer to an instance of Kyler's "Item class" Example: >>>
    # my_flashlight = Item("flashlight")     # or however Kyler decides to do it
    # >>> my_bedroom.add_item(my_flashlight, "A lit flashlight rests on the ground. Its beam of light projects
    #       a bright circle on the wall.")
    def add_item(self, item, addition_to_room_description):
        if isinstance(item, str):
            self.items[items[item]] = addition_to_room_description.strip()
        else:
            self.items[item] = addition_to_room_description.strip()

    # remove an item from the room
    # TODO: remember to integrate this with the "pick up item" method, or the player will get infinite items!!
    def remove_item(self, item):
        if isinstance(item, str):
            del self.items[items[item]]
        else:
            del self.items[item]

    # add an adjoining room, letting the player move from this room into the other. Also adds a corresponding path of
    # return to this room
    # Example:
    # >>> my_bedroom.add_connecting_room(somebody_elses_room, "north")
    def add_connecting_room(self, roomname, direction):
        if direction.lower() not in ['north', 'east', 'west', 'south', 'up', 'down']:
            raise KeyError(
                'DEV: Please specify a cardinal direction ("north", "south", "east", "west", "up", or "down")')
        if isinstance(roomname, str):
            self.connectingRooms[direction.lower()] = rooms[roomname.lower()]
            rooms[roomname.lower()].connectingRooms[OPPOSITE_DIRECTIONS[direction.lower()]] = self
        else:
            self.connectingRooms[direction.lower()] = roomname
            roomname.connectingRooms[OPPOSITE_DIRECTIONS[direction.lower()]] = self

    # adds an ASCII map
    # TODO: maybe add compass points automatically; add doors automatically?
    def add_map(self, newmap):
        self.map = newmap

    def format_map(self):
        if not self.is_dark:
            return self.map
        elif self.is_dark and items["flashlight"] in PLAYER.inventory:
            if items["flashlight"].lit:
                return self.map
        return ""

    def get_description(self):
        if not self.is_dark:
            ret = self.description
            for item in self.items:
                ret += ' '
                ret += self.items[item]
            return ret
        elif self.is_dark and items["flashlight"] in PLAYER.inventory:
            if items["flashlight"].lit == True:
                ret = self.description
                for item in self.items:
                    ret += ' '
                    ret += self.items[item]
                return ret
        return "It is pitch-black in this room, you can't see a thing."


class Item:
    def __init__(self, name, description, can_pick_up=True):
        # Item name
        self.name = name
        # The description of the item
        self.description = description
        # The actions that you can do with this item
        self.registered_actions = {}
        #        self.actioninstances = {}
        items[self.name] = self
        self.is_weapon = False
        self.add_action("look at", on_success=self.description)
        if can_pick_up:
            self.add_action("pick up", on_success="You pick up the %s" % self.name,
                            on_fail="There's no %s here." % self.name, action=pick_up_item)
            self.add_action("drop", on_success="You drop the %s" % self.name,
                            on_fail="You're not carrying a %s" % self.name, action=drop_item)

    def add_action(self, action_name, on_success=None, on_fail="You can't do that here", action=None, rooms=False,
                   can_use_while_picked_up=True, can_use_while_on_ground=True):
        if not action:
            action = empty
        if not on_success:
            on_success = self.format_success(action_name)
        newaction = Action(self, action_name, on_success, on_fail, action, rooms,
                           (can_use_while_on_ground, can_use_while_picked_up))
        self.registered_actions[action_name] = newaction

    def format_success(self, action):
        return "You %s the %s" % (action, self.name)

    def run_action(self, actionname):
        self.registered_actions[actionname].run_action()

    def change_description(self, new):
        self.description = new
        del self.registered_actions["look at"]
        self.add_action("look at", on_success=self.description)


class Action:
    def __init__(self, item, actionname, onsuccess, onfail, pointer, rooms, when_usable):
        self.item = item
        self.actionname = actionname
        self.onsuccess = onsuccess
        self.onfail = onfail
        self.pointer = pointer
        self.rooms = rooms
        self.on_ground = when_usable[0]
        self.picked_up = when_usable[1]
        if actionname not in item_commands:
            item_commands.append(actionname)

    def run_action(self):
        if (self.on_ground and self.item in PLAYER.location.items) or (
                self.picked_up and self.item in PLAYER.inventory):
            if not self.rooms:
                result = self.pointer(self.item)
                if self.onsuccess and result != False:
                    print(self.onsuccess)
                    return
            else:
                if PLAYER.location.name in self.rooms:
                    result = self.pointer(self.item)
                    if self.onsuccess and result != False:
                        print(self.onsuccess)
                        return
            if self.onfail:
                print(self.onfail)
                return
        else:
            if not self.on_ground:
                print("You can't %s %s because you haven't picked it up." % (self.actionname, self.item.name))
            elif not self.picked_up:
                print("You can't %s %s while you're holding it." % (self.actionname, self.item.name))


def empty(item):
    return


def drop_item(item):
    PLAYER.location.add_item(item, "A %s lies on the floor." % item.name.title())
    PLAYER.remove_item(item, count=1)


def pick_up_item(item):
    if item in PLAYER.location.items:
        PLAYER.location.remove_item(item)
        PLAYER.add_item(item, count=1)
    else:
        return False


# WIP
class Enemy:
    def __init__(self, name, description, AI="default"):
        self.name = name
        self.description = description
        if AI == "default":
            self.AI = default_AI
        elif callable(AI):
            self.AI = AI
        else:
            raise TypeError


def default_AI(instance):
    PLAYER.onMove.append(detect_enemy)


def detect_enemy():
    if len(PLAYER.location.enemies):
        for enemy in PLAYER.location.enemies:
            enemy.combat_round = 0


# main function
# grabs command from user and executes it using created instances of Rooms and Player
# detects "core commands" (move, look around, help, etc.), as well as all registered commands to interact with items
def get_command():
    command = input('> ').strip()
    command_history.append(command)
    if command == '':
        return "invalid"
    PLAYER.prev_location = PLAYER.location
    for i in range(len(command.lower().split(' '))):
        prospective_command = ' '.join(command.lower().split(' ')[:i + 1])
        # check for core commands (just add another if statement here to detect another)
        for c in core_commands:
            if prospective_command == c or prospective_command in synonyms[c]:
                if prospective_command in synonyms["quit"] + ["quit"]:
                    if len(command.split(' ')) == 1:
                        global has_exited, has_won
                        has_won = True
                        has_exited = True
                    else:
                        print('Type "quit" to exit the game.')
                    return
                if prospective_command in synonyms["move"] + ["move"]:
                    try:
                        direction = command.lower().split(' ')[i + 1]
                        if direction in ["north", "east", "south", "west", "up", "down"]:
                            PLAYER.move(direction)
                        else:
                            print(
                                "Please specify a cardinal direction to move.\nExamples:\n> move north\n> walk east\n")
                    except IndexError:
                        print("You didn't say which way you want to go! \nExamples:\n> move north\n> walk east\n")
                    return
                elif prospective_command in synonyms["look around"] + ["look around"]:
                    print(PLAYER.location.get_description())
                    print()
                    print(PLAYER.location.format_map())
                    return
                elif prospective_command in synonyms["help"] + ["help"]:
                    has_printed = False
                    try:
                        item = ' '.join(command.lower().split(' ')[i + 1:])
                        if item in items:
                            print("With %s, you can:" % item)
                            print(' > ' + '\n > '.join(items[item].registered_actions))
                            has_printed = True
                    except IndexError:
                        pass
                    if not has_printed:
                        print(mainHelp)
                    return
                elif prospective_command in synonyms["inventory"] + ["inventory"]:
                    if PLAYER.inventory != {}:
                        print("You have:")
                        for item in PLAYER.inventory:
                            if PLAYER.inventory[item] > 0:
                                print("  - " + str(PLAYER.inventory[item]) + " " + item.name)
                    else:
                        print("You're not carrying anything right now.")
                    return
                elif prospective_command in synonyms["hint"] + ["hint"]:
                    print(PLAYER.location.hint)
                    return
        # if an item has been created on which one can execute this command, get the item and run it
        # TODO: once the
        #   "Item" implementation has been created, add a system to pass extra arguements to item commands (i.e. "turn
        #  lamp on", "turn lamp off")
        true_command = None
        for c in item_commands:
            if prospective_command == c:
                true_command = c
                break
            elif c in synonyms.keys():
                if prospective_command in synonyms[c]:
                    true_command = c
        if true_command in item_commands:
            try:
                item_string = ' '.join(command.lower().split(' ')[i + 1:])
            except IndexError:
                print(
                    "You didn't say which item you want to %s! \nExamples:\n> look at painting\n> pick up sword\n" %
                    str(prospective_command))
                return
            try:
                item = items[item_string]
                if item not in PLAYER.location.items and item not in PLAYER.inventory:
                    print("There is no %s in this room" % item_string)
                elif true_command in item.registered_actions:
                    item.run_action(true_command)
                else:
                    print("You can't %s %s" % (prospective_command, item.name))
            except KeyError:
                print("There is no %s in this room" % item_string)
            return
    print("This command isn't recognized. Type 'help' for a list of commands.")
    return "invalid"


def do_command_update():
    if PLAYER.prev_location.enemies:
        if PLAYER.prev_location.is_dark:
            if flashlight not in PLAYER.inventory:
                print(
                    "You hear a faint hissing from the darkness, accompanied by a nauseating stench of decay. Suddenly, a vaguely humanoid shape, hunched and bounding on all fours, looms out of the darkness.")
            else:
                if not flashlight.lit:
                    print(
                        "You hear a faint hissing from the darkness, accompanied by a nauseating stench of decay. Suddenly, a vaguely humanoid shape, hunched and bounding on all fours, looms out of the darkness.")
        print(
            """It’s on you in an instant; it’s sharp nails slice at your skin, tearing it open. Pain shoots through the wounded areas, and through the haze, you worry about infection. It’s such a stupid, useless thought, yet it fills your head as the creature’s jaw falls open, it’s teeth dirty and crusted will blood. And bites into your throat.""")
        PLAYER.kill()
    display_death_message()


# stores all names and instances of Items and Rooms
# formatted as {"name":<instance>}
items = {}
rooms = {}

# all commands which have been executed
command_history = []

# if there's multiple ways to say an action, put 'em here (i.e. move north, walk north, go north will all be treated
# the same
synonyms = {"move": ["move", "walk", "go"], "look around": ["look around", "examine my surroundings"],
            "help": ["help", "info", "commands"], "look at": ["look at", "examine", "investigate"], "inventory": [],
            "hint": [], "pick up": ["grab", "take"], "drop": ["put down"], "reel in": ["retract"],
            "reel out": ["extend"], "open": ["unlock"], "wear":["put on"], "pull":["flick", "flip"], "press":["push", "click"], "quit":["exit"]}

core_commands = ["move", "look around", "help", "inventory", "hint", "quit"]
# Item class will add more of these I'm envisioning something where someone could add any type of action to their
# item, which would then be stored here so that it would be recognized
# things like Eat, Open/Close, Turn On, etc. could be added like this just to the items which need them
item_commands = ["look at", "pick up", "drop"]

OPPOSITE_DIRECTIONS = {"north": "south", "south": "north", "east": "west", "west": "east", "up": "down", "down": "up"}

ALL = True

# What's printed when typing the "help" command
mainHelp = """Welcome to the Bay 2022 Computer Science Text Adventure Game! If you're new here, these are some 
commands to get you started:
 > move north        # move around to a nearby room; you can move north, south, east, or west
 > look around       # see what's in the room you're in. Will also give a map
 > look at candle    # examine an object in detail
 > take candle       # some objects can be picked up, and even used in other ways. Type 'help <item>' 
for info on what you can do 
 > inventory         # look at all the items you are carrying. You can examine, drop and use items in your inventory
 > hint              # stuck? Ask for some help! Only some rooms have this
 > quit              # exit the game
 """

credits = """Mystery Mansion
A TBS Computer Science Final Project, 2022
Brought to you by Good Studios™ in cooperation with The Bay School of San Francisco.




Creative Brief | Corey Walsh
Story Lead | Neve Blumenthal, Hudson Webster, Katherine Hansen
Game Mechanics and Framework | Tate Rowney, Kyler Smith




ROOMS:
Foyer - Tate Rowney
Hallways - Tate Rowney
Ballroom - Katherine Hansen
Conservatory - Henry Walen
Lounge - Hudson Webster
Dining room - Madeleine Chen
Library - Neve Blumenthal
Kitchen - Avery Tirva
Dumbwaiter - Kyler Smith
Cellar - Emmanuel Ezirim
Storage Room - Henry Walen
Master Bedroom - Kyler Smith
Billiards Room - Fletcher Boyd
Music Room - Fletcher Boyd
Study - Hudson Webster

Master bedroom - Kyler Smith
Dressing room - Chris Lam
Cellar - Manny Ezirim
Storage room - Henry Walen

Additional
Library - Neve Blumenthal
Study - Hudson Webster
Dining room - Madeleine Chen
Music room - Fletcher Boyd
Billiard room - Fletcher Boyd
Conservatory - Henry Walen

CS2
Secret passageway - Tate Rowney
Dumbwaiter - Kyler Smith



"""


def roll_credits(speed):
    for i in credits.split("\n"):
        time.sleep(speed)
        print(i)
        print()


# roll_credits(1)


def get_admin_command(item):
    command = input("Enter command:   >>> ")
    try:
        exec(command)
    except:
        print("Command invalid, please try again.")


admin_dice = Item("dice", "These three shiny bone cubes are engraved with mysterious symbols.")
admin_dice.add_action("roll",
                      on_success="You roll the dice. Each one of them lands with the same symbol facing up: a skull with glaring eye sockets.",
                      action=get_admin_command)


def fight(item):
    has_weapon = False
    for item in PLAYER.inventory.keys():
        if item.is_weapon:
            has_weapon = True
    if has_weapon:
        has_selected = False
        while not has_selected:
            print("Which weapon do you want to use? You have:")
            for item in PLAYER.inventory.keys():
                if item.is_weapon:
                    print("   - " + item.name)
            selection = input("   > ")
            try:
                selection = items[selection]
                if not selection.is_weapon:
                    print("That can't be used as a weapon.")
                else:
                    print(selection.on_kill)
                    PLAYER.location.remove_item(zombie)
                    PLAYER.location.enemies = []
                    PLAYER.location.add_item(zombie_corpse,
                                             "The putrid, slimy Corpse, once moving feverishly, now lies still, face-down in the center of the floor.")
                    PLAYER.location.add_item(key,
                                             "A silver Key has slipped from a fold in its grimy rags onto the floor.")
                    has_selected = True
            except KeyError:
                print("You don't have that in your inventory.")
                print()

    else:
        print("You try to fight off the monster with your bare hands, but it is useless.")
        return


def use_weapon(item):
    if PLAYER.location == cellar and zombie in cellar.items:
        PLAYER.location.remove_item(zombie)
        PLAYER.location.enemies = []
        PLAYER.location.add_item(zombie_corpse,
                                 "The putrid, slimy Corpse, once moving feverishly, now lies still, face-down in the center of the floor.")
        PLAYER.location.add_item(key, "A silver Key has slipped from a fold in its grimy rags onto the floor.")
        return True
    else:
        return False


zombie = Item("zombie",
              "Something lies in the corner, covered in ragged scraps of cloth. It stirs slightly -- it seems to be alive.\nThe creature begins to move toward you. It crawls. Quickly. You squint to try and see it in the dark. It could’ve been human at some point, but not now.",
              can_pick_up=False)
zombie.add_action("fight", action=fight, on_success=" ")

zombie_corpse = Item("corpse", "It was definitely human. At some point. Definitely a long, long time ago.",
                     can_pick_up=False)

key = Item("key", "A small silver key. It has a coat of arms embossed on it, which looks somehow familiar...")

# --------------INSERT YOUR CODE HERE------------------


flashlight = Item("flashlight", "The bulb still seems in working order.")
flashlight.lit = False


def turn_on(item):
    if not item.lit:
        item.lit = True
        item.change_description("The bulb emits a blinding cone of light.")
    else:
        return False


def turn_off(item):
    if item.lit:
        item.lit = False
        item.change_description("The bulb still seems in working order")
    else:
        return False


flashlight.add_action("turn on", on_success="You flip the switch. The bulb emits a bright cone of light.",
                      on_fail="The flashlight is already on.", action=turn_on, can_use_while_on_ground=False)

flashlight.add_action("turn off",
                      on_success="You flip the switch. The bulb slowly transitions from white, to glowing red, to a dull gray.",
                      on_fail="The flashlight is already off.", action=turn_off, can_use_while_on_ground=False)

# ------------- Henry ------------
Conservatory = Room("conservatory")
Conservatory.description = "Dead plants and flowers all around, with dirt sprawled all over the place. Rays of light fall through the white stained glass onto a hard stone floor. Behind you, to the west, a door leads back into the hallway."
Conservatory.map = """
_______________________________
|       |        _    ┌ _  ┐  |
--    (_|_)      ║_   └-╩--┘  |
--      |      ┌ ║║ ┐     ¥   |
|      ████    └----┘    ███  |
-------------------------------"""
carrot = Item("carrot", "Is it rotten? Who knows.", can_pick_up=True)
carrot.eat_carrot = False


def eat_carrot(item):
    if not item.eat_carrot:
        item.eat_carrot = True
        PLAYER.remove_item(carrot, count=1)
    else:
        return False


carrot.add_action("eat", on_success="Well, that was a bad idea.",
                  on_fail="You have already eaten this carrot. It is in your stomach, unfortunately.",
                  action=eat_carrot, can_use_while_on_ground=False)

Conservatory.add_item(carrot, "A dubiously green Carrot lies discarded inside an empty flower pot.")

# -------------- Hudson ----------------
lounge = Room("lounge")

lounge.description = "The room is filled with velvet chairs and a deep red armoire leans against the floral walls. Despite the clear effort to make this a cozy space, you feel cold and afraid. Behind you, to the west, a door leads back into the hallway."

lounge.map = """
┌───────────────────┐
┴                   │
┬                   │    
│                   │    
│                  ││    
│                  ││    
│                   │    
│                   │    
│                   │    
│                   │
│      └──────┘     │
│                   │
│          ┌───┐    │
└───────────────────┘
"""

Couch = Item("couch", "An old musty couch. Reminds you of your grandma's house.", can_pick_up=False)
# Painting = Item("Painting", "An old painting. Most of the detail has been stripped away.", can_pick_up=False)

Couch.add_action("sit on",
                 on_success="You sit on the couch. It's about as uncomfortable as you thought it would be.",
                 on_fail="You would sit on the couch again but, it wasn't very fun.")

lounge.add_item(Couch, "An old, musty Couch stands in the middle of the room.")
# lounge.add_item(Painting, "An old painting hangs crooked on the wall. Most of the detail has been stripped away.")


# -------------- Neve ----------------
library = Room("library")
library.description = "You find yourself in a dimly lit library illuminated only by vintage lamps. You are surprised they still work. Behind you, to the west, a door leads back into the hallway. Charred books are scattered across the floor."
library.map = """
_______________________________
|            ▓      ░░         |
--     ░░░░  ▓▓▓▓▓     ▓▓  |_| |
--     ░░     ▓▓   ▓▓    ▓▓    |
|    ░░░░  |_|         ▓▓      |
--------------------------------
"""


def open_secret_hatch(item):
    item.change_description("Beyond the open hatch lies a rickety ladder leading down into darkness.")
    library.remove_item(secret_hatch)
    library.add_item(secret_hatch,
                     "A small metal Hatch, flush with the floor, lies in the back corner of the room, in the spot where the rug used to be. It leads downwards.")
    library.add_connecting_room(cellar, "down")


secret_hatch = Item("hatch",
                    "Besides a small handle, this rusted metal hatch lies perfectly level with the floor. It has no visible lock.",
                    can_pick_up=False)
secret_hatch.add_action("open",
                        on_success="You grab the cold, rusted handle, and the hatch opens with a creak. The smells of death and dust hits you and you wince. It is dark down there. The kind of darkness that feels like it will swallow you whole.",
                        action=open_secret_hatch)


def reveal_secret_hatch(item):
    item.change_description("The rug is covered in a red stripes forming moire pattern.")
    library.add_item(secret_hatch,
                     "A small metal Hatch, flush with the floor, lies in the back corner of the room, in the spot where the rug used to be.")
    Rug.registered_actions["pick up"] = Action(Rug, "pick up",
                                               "You pick up the rug.",
                                               "You're already carrying the rug.", pick_up_item, False, (True, False))
    library.remove_item(item)
    PLAYER.add_item(item)


Rug = Item("rug",
           "You shove the books away to get a closer look at the rug. It's covered in red stripes, forming a moire pattern. The amount of dust covering it is conspicuously less than that on the surrounding floor. It looks small enough to pick up.",
           can_pick_up=True)

Rug.registered_actions["pick up"] = Action(Rug, "pick up",
                                           "You pull at the faded red fabric up with surprising ease. As the rug comes away, you see a small metal Hatch on the floor beneath it.",
                                           " ", reveal_secret_hatch, False, (True, False))

Bookshelf = Item("bookcase",
                 "The shelves of this collapsing bookcase sag under the weight of hundreds of leather-bound tomes. The few that lie open display signs of water damage.",
                 can_pick_up=False)
Bookshelf.add_action("climb", on_success="Hmm, nothing up here...")

Ladder = Item("ladder", "The wheels which once allowed the ladder to move are caked with rust.", can_pick_up=False)
Ladder.add_action("climb", on_success="Hmm, nothing up here...")

Desk = Item("desk",
            "The pages of the books blanketing this dark mahogany desk have rotted away with time. Everything is covered in a thick layer of dust.",
            can_pick_up=False)

#library.add_item(Desk,
#                 "In the far left corner, you can see a desk: Dark mahogany and old with opened books flung over them.")
library.add_item(Rug,
                 "In the other corner there is a patterned red Rug. It somehow looks newer than the rest of the house.")
library.add_item(Bookshelf,
                 "In in the center of the room the largest Bookcase you've ever seen: flowing shelves of dozens of books of varying faded colors.")
library.add_item(Ladder, "There's even one of those movable Ladders from those movies.")

library.hint = "Rug repair can be expensive..."


# -------------- Manny ----------------
def open_cabinet(item):
    if not key in PLAYER.inventory:
        return False
    print(
        "You squint at the door, covering your nose. There’s a small keyhole under the rickety handle, gaping at you. So, that’s what the key was for.")
    time.sleep(2)
    print(
        "You fumble inside your pocket, fingers brushing around for the cool metal. There. You curl your fingers around it and bring it out, sliding it into the keyhole. It turns with a click, the only sound echoing through the silence.")
    time.sleep(2)
    print(
        "You reach out and grip the wooden handle, surprised that it doesn't immediately break off. You can feel your heart in your chest. Every nerve in your body is screaming at you to run, to leave this alone. But you can’t. Not now.")
    time.sleep(2)
    print(
        "The door creaks open slowly; the stench is worse, causing you to groan. You try to breathe through your mouth as you shine the flashlight inside the cabinet. And your chest freezes over. You think you might actually throw up. Or maybe pass out. A corpse stares at you as you try to stave off the panic. You shudder as you shine the light over the corpse, trying not to gag at the way the flesh has turned a sickly green, and how it resembles spoiled meat. Best to not think of another person that way. This must be Thomas Rowell, though you have no idea how he isn’t a skeleton yet. Maybe you don’t want to know.")
    time.sleep(5)
    print(
        "Your flashlight beam falls on something in the corpse’s decayed hand. It looks like a file of papers, though it has yellowed and the pages seem to be the same color as the corpse’s sickly hand. That’s it; that’s what you’ve come for. You know what you have to do. You don’t want to, god, you don’t want to touch that thing. But Player, you have to. The world needs to know the information I died with. You reach out to the files and bite back a cry at the way it oozes onto your hand. The file easily falls into your hand and you grip it tightly, staring at the corpse’s rotting eyelids. You wonder how it died. It wasn't pretty; you don’t want to know. Your chest heaves and you grip the file even harder.")
    time.sleep(2)
    print()
    print("Congratulations player; you won.")
    print("\n\n")
    #    print("You gulp in the fresh night air, tilting your face to the starry sky. Your chest heaves and you grip the file even harder. Congratulations player; you won.")
    time.sleep(8)
    PLAYER.win()
    return True


cabinet = Item("cabinet",
               "This heavy oak door has an intricate coat of arms engraved on it. Strangely, the inner handle has a keyhole over it.",
               can_pick_up=False)
cabinet.add_action("open", on_success=" ",
                   on_fail="You grasp the door handle, but it won't budge. Maybe you need a key?", action=open_cabinet)

cellar = Room("cellar")
cellar.description = "An old, dusty cellar, with a ladder leading up. Something isn’t right. You sense an ominous aura coming from the darkness. Stone brick lines the walls, leaving a rough feeling on your hands, and your shoes grind against the pebbly floor."
cellar.map = """
_______________________________
|\ ) /                        |
| \)/          __     ├--┴┤   |
| ƒ     __     ▒▒     ├---┤   |
|ƒ    ├-┴┴-┤          ├┴--┤   |
|     ├----┤        ___      /|
|     ├---┴┤   xx   ▒×▒     /\|
|              xx           /  |
-------------------------------"""
cellar.is_dark = True
cellar.add_item(zombie,
                "There it is. You’ve felt its presence, and now you’ve seen it with your own two eyes. \nFirst, a silhouette, then a pair of soggy boots… finally, you see its face, wide eyed and hungry for human flesh.\n")
cellar.enemies.append(zombie)
cellar.add_item(cabinet,
                "A tall wooden Cabinet rests in one corner. It's tall enough to stand inside. The stench eminates more strongly from that direction.")

# -------------- Avery ----------------
kitchen = Room("kitchen")
kitchen.description = "The green cupboards and wood iron stove give away the room’s identity immediately - it’s a kitchen, or at least it used to be… The room is very dusty and looks like it has’t been used in a very long time. The kitchen floor is cluttered with dirty dishes and utensils. Doors lead out of the room to the south and east. An old-fashioned dumbwaiter is mounted in the west wall, big enough to crawl inside."
kitchen.map = """ 
—-------------------
|    _____         |
--  |     |        ┴
--  |_____|        _
|           |-|    |
|                  |
—--_|  |_----------- """

apron = Item("apron",
             "This ancient-looking floral apron seems to have an infinite quantity of dust embedded within it.")
apron.wear_apron = False


def wear_apron(item):
    if not item.wear_apron and apron in PLAYER.inventory:
        item.wear_apron = True
        item.change_description("The apron is sitting on your body.")
        PLAYER.remove_item(apron)
    else:
        return False


apron.add_action("wear", on_success="You put on the apron. You are now ready to move on to the dining room.",
                 on_fail="You're already wearing it.", action=wear_apron, can_use_while_on_ground=False)

kitchen.add_item(apron, "There is still an Apron hanging from a hook on the wall.")

# -------------- Madeline ----------------
madeleine_diningroom = Room("dining room")
madeleine_diningroom.description = "A dark and classic looking dining room is illuminated by your flashlight beam. Doors lead out of the room to the north, south, and east."
madeleine_diningroom.map = """

___    _______________________
|   _______________________   |
|  |                       | --
|  |      (|) (()) |)      | --             
|  |_______|_______|_______|  |
|                             |
|____________________     ____|

"""

madeleine_diningroom.is_dark = True

knife = Item("knife",
             "This corroded silver eating utensil is embossed with unintelligible symbols. The blade still looks sharp.",
             can_pick_up=True)
knife.on_kill = "You grab the knife, fingers slick with sweat. The creature snarls at you, one long, spindly leg moving toward you. You stab wildly at the creature’s neck and pray. You close your eyes. Stupid, yes, but there is no way that this will work. … there is crunching sound, a thump, and then silence. You crack your eyes open to see the creature stagger backward, knife embedded in its skull. It slowly topples to the ground and ceases to move. A silver Key slips from a fold in its grimy rags onto the floor."
knife.add_action("stab", on_success=knife.on_kill,
                 on_fail="You have stabbed with the knife... but I don't see any scary monsters around...",
                 action=use_weapon, can_use_while_on_ground=False)
knife.is_weapon = True

fork = Item("fork",
            "This corroded silver eating utensil is embossed with unintelligible symbols. The tines still look sharp.",
            can_pick_up=True)
fork.on_kill = "You grab the fork, fingers slick with sweat. The creature snarls at you, one long, spindly leg moving toward you. You stab wildly at the creature’s neck and pray. You close your eyes. Stupid, yes, but there is no way that this will work. … there is crunching sound, and a muffled gurgling. You crack your eyes open to see the creature stagger backward, fork embedded in its skull. It slowly topples to the ground and ceases to move. A silver Key slips from a fold in its grimy rags onto the floor."
fork.add_action("stab", on_success=fork.on_kill,
                on_fail="You have stabbed with the fork... but I don't see any scary monsters around...",
                action=use_weapon, can_use_while_on_ground=False)
fork.is_weapon = True

plate = Item("plate", "The china of this wide dinner plate is split by tiny fractures.", can_pick_up=True)
table = Item("table", "This long trestle table is made from finely finished wood. It takes up almost half of the room.",
             can_pick_up=False)

madeleine_diningroom.add_item(table,
                              "An old, grand-looking Table takes up almost the whole room. It still holds some cutlery;")

madeleine_diningroom.add_item(knife, "a Knife,")
madeleine_diningroom.add_item(fork, "a Fork,")
madeleine_diningroom.add_item(plate, "and a Plate.")

# -------------- Katherine ----------------
katherine_ballroom = Room("ballroom")
katherine_ballroom.description = "This once-opulent ballroom is covered in a thick layer of dust. Doors lead out of this room to the north and east."
katherine_ballroom.map = """
______________[   ]____________
|                             |
|                         ----
|                        |  
|                         ----
|       |                     |
|     --|--                  --
|    |     |            --   --
|                       --    |
-------------------------------"""

katherine_ballroom.is_dark = True
chandelier_switch = Item("switch", "Turns on the only light source in the room.", can_pick_up=False)
chandelier_switch.lit = False

katherine_ballroom.is_dark = True
chandelier = Item("chandelier",
                  "This glittering chandelier hangs from the ceiling by an impossibly narrow cord. When you look at it out of the corner of your eye, you could swear it is slowly spinning...",
                  can_pick_up=False)
chandelier.lit = False


def turn_on_chandelier(item):
    if not chandelier.lit:
        chandelier.lit = True
        chandelier.change_description(
            "This glittering chandelier hangs from the ceiling by an impossibly narrow thread. It flickers with inconsistent light emanating from a bulb buried deep within it.")
        katherine_ballroom.is_dark = False
    else:
        return False


def turn_off_chandelier(item):
    if chandelier.lit:
        chandelier.lit = False
        chandelier.change_description(
            "This glittering chandelier hangs from the ceiling by an impossibly narrow thread. When you look at it out of the corner of your eye, you could swear it is moving...")
        katherine_ballroom.is_dark = True
    else:
        return False


chandelier_switch.add_action("turn on",
                             on_success="You flip the switch. The chandelier flickers back on and lights up the ballroom.",
                             on_fail="The chandelier is already on.", action=turn_on_chandelier)

chandelier_switch.add_action("turn off",
                             on_success="You flip the switch. The chandelier slowly flickers off, leaving you alone in the dark room.",
                             on_fail="The chandelier is already off.", action=turn_off_chandelier)

katherine_ballroom.add_item(chandelier,
                            "The reflection of a huge Chandelier, hanging from the ceiling, sparkles on the marble floor.")
katherine_ballroom.add_item(chandelier_switch, "A Switch is embedded in the wall next to the door.")

# --------------Fletcher------------------
# FLETCHER ROOMS
BILLIARDS = Room("billiards")
MUSIC = Room("music")

# --------------------- Music room -------------------------
MUSIC.description = "This rambunctious territory is for those who plan to let their inner demon or teenage white girl out, jamming to Katy Perry and Taylor Swift. To the east, a door leads back into the hallway."

MUSIC.map = """
______________________
||.|                 |
| ¯                 --
|                   --
|_ _                 |
|{=}                 |
|¯ ¯                 |
|      _ _ _ _ _ _   |
|     |_¯_¯_¯_¯_¯_|  |
¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
"""

# Record disc to slice enemy (weapon)
Record = Item("record",
              "This vinyl disc has a peeled label surrounding the central cavity. Its edges are incredibly sharp.")
Record.wind = False
Record.is_weapon = True
Record.on_kill = "You grab the record disk, fingers slick with sweat. The creature snarls at you, one long, spindly leg moving toward you. You chuck the record at the creature’s neck and pray. You close your eyes. Stupid, yes, but there is no way that this will work. … there is a wet tearing sound, a thump, and then silence. You crack your eyes open to see the creature's head rolling around the floor like a soccer ball. Nice. \nA silver Key slips from a fold in its grimy rags onto the floor."


# [TATE]: I removed these b/c by the time you manage to wind up AND throw, the zombie will have killed you lol
def wind_up(item):
    if not item.wind:
        item.wind = True
        item.change_description("The disc is viable to kill and will slice your enemy.")
    else:
        return False


def wind_down(item):
    if item.wind:
        item.wind = False
        item.change_description("The disc seems difficult to hold on your person.")
    else:
        return False


# Record.add_action("wind up", on_success="You wind up your arm ready to hit your enemy.",
#                  on_fail="You have already wound up your arm.", action=wind_up, can_use_while_on_ground=False)
# Record.add_action("wind down",
#                  on_success="You put the record by your side. The disc slowly retracts from being wound up, from your head, to your stomach, to your thigh.",
#                  on_fail="The record has wound-down.", action=wind_down, can_use_while_on_ground=False)

Record.add_action("throw", on_success=Record.on_kill,
                  on_fail="You hurl the disc into the wall. But I don't see any scary monsters around...",
                  action=use_weapon, can_use_while_on_ground=False)

# -------- Furniture w/actions -----------
DiscJokey = Item("record player",
                 "The system is caked in dust and grime. As you examine it closely, you notice something out of place: a small, shiny metal Button has been affixed to the side with screws.",
                 can_pick_up=False)
DiscJokey.add_action("play",
                     on_success="It is possible to hear creepy music while you are chased by a psychotic thing.")
RecordStand = Item("record stand",
                   "The wood is covered in dust and grime. It is impossible to see your grand-parents' favorite hits as a teenager.",
                   can_pick_up=False)

secret_door_music = Item("secret door music", "", can_pick_up=False)
secret_door_music.is_open = False


def reveal_secret_door_music(item):
    if not secret_door_music.is_open:
        MUSIC.add_item(secret_door_music,
                       "In the northern wall, a section of panelling has been slid aside to reveal a passage beyond.")
        secret_door_music.is_open = True
        MUSIC.map = """
        _______| |____________
        ||.|                 |
        | ¯                 --
        |                   --
        |_ _                 |
        |{=}                 |
        |¯ ¯                 |
        |      _ _ _ _ _ _   |
        |     |_¯_¯_¯_¯_¯_|  |
        ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
        """
        MUSIC.add_connecting_room(secret_passage_music, "north")
    else:
        return False


lever_music = Item("button",
                   "This metal button is subtly mounted on the side of the record player. It bears no markings: you're not sure what it does.",
                   can_pick_up=False)
lever_music.add_action("press",
                       on_success="As you push the button, you hear a muffled beeping noise, followed by a faint rumbling and clicking sound in the walls. A seemingly ordinary section of the northern wall moves smoothly aside to reveal a secret passage beyond.",
                       on_fail="You push the button, but nothing happens.", action=reveal_secret_door_music)

# Items

# Interactions
MUSIC.add_item(DiscJokey, "A Record Player rests on the ground in the western direction.")
MUSIC.add_item(RecordStand, "A Record Stand rests on the ground in the eastern direction.")
MUSIC.add_item(Record, "An undamaged Billy Joel Record rests on the record stand.")
MUSIC.add_item(lever_music, "")

# -------------- Still Fletcher ----------------
BILLIARDS.description = "This fine established room is for those who plan to partake in the game of billiards or pool. A door leads out of this room to the west."

BILLIARDS.map = """
__________ _ _ _ ______________
|         \+ + +/             |
--                            |
--                           \|
|      (O¯¯¯¯¯O¯¯¯¯¯O)        }
|      |             |        }
|      (O_____O_____O)       /|
|                             |
|                             |
|                          _  |
|                         |.| |
¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
"""

# Pool Cue to impale enemy (weapon)
PoolCue = Item("cue", "This long wooden rod seems like it could work as a weapon.")
PoolCue.charge = False
PoolCue.is_weapon = True
PoolCue.on_kill = "Your fingers clench around the pool cue and you pull it back. You shove it toward the creature, stabbing the end of it through the creature’s chest. It screeches and claws at you, but it crumples to the ground before it can go any further. It is dead and still. A silver Key slips from a fold in its grimy rags onto the floor."


def charge_up(item):
    if not item.charge:
        item.charge = True
        item.change_description("The cue is viable to kill and will impale your enemy.")
    else:
        return False


def charge_down(item):
    if item.charge:
        item.charge = False
        item.change_description("The cue seems unwieldy to hold on your person.")
    else:
        return False


# PoolCue.add_action("charge up", on_success="You charge the cue to stab your enemy.",
#                   on_fail="You have already charged the cue.", action=charge_up, can_use_while_on_ground=False)
# PoolCue.add_action("charge down",
#                   on_success="You hold the cue next to you like a staff. The cue slowly gets charged down, from your head, to your stomach, to your thigh.",
#                   on_fail="The cue is already charged down.", action=charge_down, can_use_while_on_ground=False)

PoolCue.add_action("stab", on_success=PoolCue.on_kill, on_fail="Hefting the cue, you viciously impale... the air...",
                   action=use_weapon, can_use_while_on_ground=False)

secret_door_billiards = Item("secret door billiards", "", can_pick_up=False)
secret_door_billiards.is_open = False


def reveal_secret_door_billiards(item):
    if not secret_door_billiards.is_open:
        BILLIARDS.add_item(secret_door_billiards,
                           "In the northern wall, a section of panelling has been slid aside to reveal a passage beyond.")
        secret_door_billiards.is_open = True
        BILLIARDS.map = """
        __________ _ _ _ ___| |________
        |         \+ + +/             |
        --                            |
        --                           \|
        |      (O¯¯¯¯¯O¯¯¯¯¯O)        }
        |      |             |        }
        |      (O_____O_____O)       /|
        |                             |
        |                             |
        |                          _  |
        |                         |.| |
        ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
        """
        BILLIARDS.add_connecting_room(secret_passage_billiards, "north")
    else:
        return False


# -------- Furniture w/actions -----------
PoolTable = Item("pool table", "The surface and balls are covered in dust and grime.", can_pick_up=False)
#PoolTable.add_action("imagine how people used to play", on_success="It is impossible to play with how old it is.")

CueRack = Item("cue rack",
               "The pool cues are covered in dust and grime. As you examine it up close, you see a tiny Lever attached to the wall behind the cues.",
               can_pick_up=False)  # "can_pick_up=True"??
#CueRack.add_action("pick what is the most reliable",
#                   on_success="It is possible to use one of these as a weapon for the future.")

lever_billiards = Item("lever",
                       "This tiny wooden lever is well-hidden behind rows of pool cues. It bears no markings: you're not sure what it does.",
                       can_pick_up=False)
lever_billiards.add_action("pull",
                           on_success="As you pull the lever, you hear a faint rumbling and clicking sound in the walls. A seemingly ordinary section of the northern wall moves smoothly aside to reveal a secret passage beyond.",
                           on_fail="You pull the lever, but nothing happens.", action=reveal_secret_door_billiards)


def kill(item):
    PLAYER.kill()


Painting = Item("Painting", " ", can_pick_up=False)
Painting.registered_actions["look at"] = Action(Painting, "look at",
                                                "You admire how beautiful the painting is -- and your skin is sucked into it, leaving your intestines, blood, bones, and arteries!",
                                                " ", kill, False, (True, False))

# Items/Interactions
BILLIARDS.add_item(PoolTable, "A Pool Table stands on the eastern ground.")
BILLIARDS.add_item(Painting, "A Painting is hung on the southern wall.")
BILLIARDS.add_item(CueRack, "A Cue Rack is displayed on the northern wall.")
BILLIARDS.add_item(PoolCue, "A Cue rests on the stand.")
BILLIARDS.add_item(lever_billiards, "")

# ---------- Tate ------------
secret_passage_billiards = Room("secret passage billiards")
secret_passage_billiards.description = "This narrow hallway is walled with unfinished boards. Candle sconces, encrusted with congealed wax, are mounted along the walls. The passage proceeds west into the gloom. To the south, the passage ends in a door."
secret_passage_billiards.is_dark = True
secret_passage_billiards.hint = "The pendulum of the clock is important! It can be examined, and maybe interacted with in other ways..."
secret_passage_billiards.add_map("""
-------------------------------|
                               |
-------------------------[  ]--|""")
secret_passage_billiards.connectingRooms["south"] = BILLIARDS

secret_passage_music = Room("secret passage music")
secret_passage_music.description = "This narrow hallway is walled with unfinished boards. Candle sconces, encrusted with congealed wax, are mounted along the walls. The passage proceeds east into the gloom. A door is embedded in the south wall."
secret_passage_music.is_dark = True
secret_passage_music.add_map("""
--------------------------------
|
--[ ]---------------------------""")
secret_passage_music.connectingRooms["south"] = MUSIC


def check_for_secret_passage_exit():
    if PLAYER.location == BILLIARDS and PLAYER.prev_location == secret_passage_billiards:
        reveal_secret_door_billiards(secret_door_billiards)
    elif PLAYER.location == MUSIC and PLAYER.prev_location == secret_passage_music:
        reveal_secret_door_music(secret_door_music)


grandfather_clock = Item("clock",
                         "This ancient clock is covered in dust. Its hour and minute hands both point straight down. The guts of the machine are visible through the area formerly covered by the casing now lying on the floor. Dozens -- maybe hundreds -- of separate gears line the insides, as well as the clock's brass pendulum, which has a bizarre pulley mechanism attached to it.",
                         can_pick_up=False)


def swing(item):
    period = 2 * math.pi * math.sqrt(item.length / 9.8)
    hour_pos = math.floor((period / 2.2) * 12)
    minute_pos = (period / 2.2) * 12 - math.floor((period / 2.2) * 12)
    hour_pos = (hour_pos + 6) % 12
    if hour_pos == 0:
        hour_pos = 12
    minute_pos = round(minute_pos * 12)
    item.uses += 1
    if item.uses == 6:
        print(
            "An avalanche of cogs, gears, and rods comes tumbling out of the clock with a tremendous clatter. The clocks hands drop off of the face and onto the floor.")
        grandfather_clock.change_description(
            "This ancient clock is covered in dust. The gears formerly occupying the inside of the clock lie scattered across the floor.")
        secret_passage_billiards.remove_item(grandfather_clock)
        secret_passage_billiards.add_item(grandfather_clock,
                                          "A decrepit grandfather Clock, covered in a thick layer of dust, sits on one side of the hallway. Brass gears lie scattered on the floor around it.")
        secret_passage_billiards.remove_item(pendulum)
        secret_passage_billiards.add_item(pendulum,
                                          "Inside the clock is a brass Pendulum with a strange mechanism attached to it.")
    elif item.uses > 6:
        print(
            "The pendulum swings, but nothing happens; only reasonable, considering the fact that the guts of the clock are lying all over the floor.")
    else:
        if hour_pos == 6 and minute_pos == 0:
            print(
                "The clock grinds to life, its gears whirring. The clock's hands twitch slightly, but don't move from their positions facing straight downward. After a few seconds, the pendulum stops abruptly in its original position, and the clock's gears stop moving.")
        elif hour_pos == 12 and minute_pos == 0:
            print(
                "The clock grinds to life, its gears whirring. Both hands rotate in unison to point at the 12 position. A thunderous, resounding chime issues from the clock, vibrating inside your skull. With a clatter the entire clock collapses into a pile of gears and detritus. Three strange dice lie on top of the pile.")
            secret_passage_billiards.remove_item(item)
            secret_passage_billiards.remove_item(grandfather_clock)
            secret_passage_billiards.add_item(admin_dice,
                                              "Three strange bone Dice lie on top of the remains of the grandfather clock.")
        else:
            print(
                "The clock grinds to life, its gears whirring. The clock's hour hand twists to point at the %s position, while the minute hand settles at %s. After a few seconds, the pendulum stops abruptly in its original position, and the clock's hands both shift back to their original positions." % (
                    str(hour_pos), str(minute_pos)))


def reel_in(item):
    if item.length == 0:
        print("The pendulum is retracted all the way.")
        return False
    try:
        delta = input("How many times do you want to turn the spool? (type 'all' to roll it up all the way) > ")
        if delta.lower() == 'all':
            print("You reel in the pendulum. It is now a tiny fraction of a centimeter long.")
            item.length = 0
        else:
            delta = float(delta) / 6
            if delta < 0:
                raise ValueError
            if item.length - delta > 0:
                item.length -= delta
            else:
                item.length = 0
    except ValueError:
        print("Please specify a positive real number (Example: 1, 2.2, 3.1412857)")
        return False


def reel_out(item):
    if item.length == 1.1:
        print("The pendulum is extended all the way.")
        return False
    try:
        delta = input("How many times do you want to turn the spool? (type 'all' to roll it down all the way) > ")
        if delta.lower() == 'all':
            item.length = 1.1
            return
        else:
            delta = float(delta) / 6
            if delta < 0:
                raise ValueError
            if item.length + delta < 1.1:
                item.length += delta
            else:
                item.length = 1.1
    except ValueError:
        print("Please specify a positive real number (Example: 1, 2.2, 3.1412857)")
        return False


pendulum = Item("pendulum",
                "The grandfather clock's brass pendulum has a tiny spool attached to it, which holds up a thin wire tied to the bottom half of the pendulum. This appears to adjust the length of the bottom half of the pendulum.",
                can_pick_up=False)
pendulum.length = 0.75
pendulum.uses = 0
pendulum.add_action("swing", on_success=" ", action=swing)
pendulum.add_action("reel in", on_success="You reel in the spool. The pendulum shortens.", on_fail=" ", action=reel_in)
pendulum.add_action("reel out", on_success="You reel out the spool. The pendulum lengthens.", on_fail=" ",
                    action=reel_out)

secret_passage_billiards.add_item(grandfather_clock,
                                  "A decrepit grandfather Clock, covered in a thick layer of dust, sits on one side of the hallway. The dark mahogany casing which formerly covered the front lies detached on the ground, revealing a myriad of shining brass gears within.")
secret_passage_billiards.add_item(pendulum,
                                  "Inside the clock is a brass Pendulum with a strange mechanism attached to it.")

window = Item("window", "The panes are covered in dust and grime.", can_pick_up=False)
window.add_action("look out",
                  on_success="The outside is blanketed in dull-gray fog. Besides a few indistinct shapes in the distance, you can't make out anything.")
window.add_action("jump out",
                  on_success="You jump from the window. You want to get out. The wind screams in your ears as the ground approaches. You don’t see it when you hit the earth. Your death is a quick snapping of the neck. A good, clean way to die.",
                  action=kill)

upper_hallway_south = Room("upper hallway south")
upper_hallway_south.description = "The faded, peeling wallpaper of this wide hallway is barely illuminated by flickering fluorescent lights. Two doors are inset in the walls, one to the east and one to the west. The hall continues north -- you can see more doors in that direction."
upper_hallway_south.add_map("""
|      |
|      |
-      -
-      -
|      |
|      |
---  ---
""")
upper_hallway_south.add_item(window, "A grimy Window is embedded in the southern wall.")

upper_hallway_center = Room("upper hallway center")
upper_hallway_center.description = "The faded, peeling wallpaper of this wide hallway is barely illuminated by flickering fluorescent lights. The hall continues north and south -- you can see more doors in both directions."
upper_hallway_center.add_map("""
|      |
|      |
|      |
|      |
|      |
|      |
""")

upper_hallway_north = Room("upper hallway north")
upper_hallway_north.description = "The faded, peeling wallpaper of this wide hallway is barely illuminated by flickering fluorescent lights. Two doors are inset in the walls, one to the east and one to the west. The hall continues south -- you can see more doors in that direction. To the north is a long, broad staircase."
upper_hallway_north.add_map("""
  - - -
 - - -
- - -
|      |
|      |
-      -
-      -
|      |
|      |
""")

lower_hallway_south = Room("lower hallway south")
lower_hallway_south.description = "The faded, peeling wallpaper of this wide hallway is barely illuminated by flickering fluorescent lights. Three doors are inset in the west, south, and east walls. The hall continues north -- you can see more doors in that direction."
lower_hallway_south.add_map("""|      |
|      |
-      -
-      -
|      |
|      |
---  ---
""")

lower_hallway_center = Room("lower hallway center")
lower_hallway_center.description = "The faded, peeling wallpaper of this wide hallway is barely illuminated by flickering fluorescent lights. Two more doors are inset in the walls, one to the east and one to the west. The hall continues north and south -- you can see more doors in both directions."
lower_hallway_center.add_map("""|      |
|      |
-      -
-      -
|      |
|      |
""")

lower_hallway_north = Room("lower hallway north")
lower_hallway_north.description = "The faded, peeling wallpaper of this wide hallway is barely illuminated by flickering fluorescent lights. Two more doors are inset in the walls, one to the east and one to the west. The hall continues south -- you can see more doors in that direction. To the north is a long, broad staircase, leading upward."
lower_hallway_north.add_map("""  - - -
 - - -
- - -
|      |
|      |
-      -
-      -
|      |
|      |
""")

stairway = Room("stairway")
stairway.description = "This long, curving flight of stairs is carpeted with faded red fabric. Spiderwebs cake the dusty wooden handrails. Illumination is provided by a grime-coated skylight far above. The stairway leads up and down."
stairway.add_map("""
_____________________
|                    |
| - - -| - - -| - - -|
|- - - |  - - |- - - |
| - -  |   - -| - -  |
|- -   |    - |- -   |
|      |      |      |
""")

lower_hallway_north.connectingRooms["north"] = stairway
upper_hallway_north.connectingRooms["north"] = stairway

# ---------- Kyler -------------
masterbedroom = Room("master bedroom")
masterbedroom.description = "The master bedroom. Fancy. Doors lead out to the east and south. An old-fashioned dumbwaiter is mounted in the west wall, big enough to crawl inside."
# This looks fine when printed to the terminal. Google docs just formats it weirdly.
masterbedroom.map = """
-------------------------------
|         ██ ║███║ ██         |
--  ▓▓▓▓▓    ║███║           --
--  ▓▓▓▓▓    ╚═══╝           --
|   ▓▓▓▓▓                     |
-------------|   |-------------"""

masterbed = Item("bed", "The bed looks super soft. Perfect for a short power nap.", can_pick_up=False)
masterbed.add_action("sleep in", on_success="You plop onto the bed and immediately fall asleep. You don't wake up.",
                     action=kill, can_use_while_on_ground=True)

leftdresser = Item("left dresser", "A simple dresser.", can_pick_up=False)
rightdresser = Item("right dresser", "The right dresser has nothing on it, except for a layer of dust.",
                    can_pick_up=False)

suspiciouscheese = Item("cheese", "A piece of cheese. Suspicious cheese.")
def cheese_kill(item):
    PLAYER.kill()
    PLAYER.remove_item(suspiciouscheese)
suspiciouscheese.add_action("eat",
                            on_success="You eat the suspicious cheese. Soon after you faint and crumple to the floor.",
                            action=cheese_kill, can_use_while_on_ground=False)

burntcandle = Item("candle",
                   "This candle looks to have seen it's fair share of use. A multitude of hardened drops of wax cling to it's sides.")

giantcarpet = Item("carpet", "This giant sprawling carpet is adorned with a pattern of majestic polka dots.",
                   can_pick_up=False)

masterbedroom.add_item(masterbed, 'A giant, soft, almost heavenly looking Bed sits in the center of the room.')
masterbedroom.add_item(leftdresser, 'Simple Dressers on the Left')
masterbedroom.add_item(rightdresser, 'and Right side of the bed.')
masterbedroom.add_item(burntcandle, 'A burnt out Candle,')
masterbedroom.add_item(suspiciouscheese, 'a piece of Cheese,')
masterbedroom.add_item(flashlight, 'and a Flashlight lie on the right dresser.')
masterbedroom.add_item(giantcarpet, 'A giant Carpet lays on the left side of the room.')

study = Room("study")

study.description = "It's a musty old room covered in a mess of papers and a thick layer of dust. The varnished wood would almost give it a homey feeling, if not for being located in a scary, rotting mansion."

study.map = """
┌──────────────┐
│ 	       |
│              │
┴              │
              ▌│
┬           └ ▌│
│              │ 
│              │
│     ┌─┐      │
└──────────────┘
"""

Desk = Item("desk", "This creaky, rotten desk sits in the middle of the room. Its so unstable you're afraid to even breathe near it.", can_pick_up=False)
Mirror = Item("mirror",
              "The mirror is shattered in a few places, but in the center you can still make out your face, although it seems contorted. You feel uneasy.", can_pick_up=False)
Revolver = Item("revolver", "This revolver has turned matte from rust and ash. You're not even sure if it works.")

Revolver.on_kill = 'You pull the trigger. The resounding "bang" from the gun echoes unbearably in the confined space. The creature falls to the floor, a small, round hole in the center of what passes for its face. A silver Key slips from a fold in its grimy rags onto the floor.'
Revolver.add_action("shoot", on_success=Revolver.on_kill, on_fail="The gun jams. Seems like a skill issue.",
                    action=use_weapon)
Revolver.is_weapon = True
# Mirror.add_action("look at", on_success="The mirror is shattered in a few places, but in the center you can still make out your face, although it seems contorted. You feel uneasy.", can_use_while_on_ground=True)

study.add_item(Desk, "A rickety wooden Desk sits in the center of the room.")
study.add_item(Mirror, "An old, crusty Mirror leans against the north wall.")
study.add_item(Revolver, "A Revolver, turned matte from rust and ash, lies on the ground.")

# ------------ Chris -------------
dressingroom = Room("dressing room")
dressingroom.description = "Mysterious, suspiciously clean walk in closet. Dark, with a flashing light bulb centered on the ceiling. A door to the south leads back into the master bedroom."
dressingroom.map = """
___________[   ]___________
| - -                     |
| | /                  [] |
| | \                  [] |
| - -       I----I        |
--------------------------- """

paper = Item("paper",
             "The charred end of this small sheet of Paper crumbles as you touch it. On the paper is written: \nYOU ARE MY LAST HOPE. FIND ME IN A DARK ROOM")
paper.add_action("read", on_success="YOU ARE MY LAST HOPE. FIND ME IN A DARK ROOM")


def add_paper(item):
    dressingroom.remove_item(wardrobe)
    dressingroom.add_item(wardrobe, "A dusty brown Wardrobe stands against one wall, with both its doors open.")
    dressingroom.add_item(paper, "A sheet of Paper lies inside the wardrobe.")


wardrobe = Item("wardrobe", "A tall wardrobe with two doors.", can_pick_up=False)
wardrobe.add_action("open",
                    on_success='You open the doors. Within lies a small sheet of paper, partially charred on one side. It reads: \nYOU ARE MY LAST HOPE. FIND ME IN A DARK ROOM',
                    action=add_paper)

shirt = Item("shirt", "This shirt seems to be fresh, as if someone just put it here.",
             can_pick_up=True)
def remove_shirt(item):
    PLAYER.remove_item(item)

shirt.add_action("wear",
                 on_success="You wear the shirt. It seems to do nothing, but you now look cool and get a giant boost of confidence.", action=remove_shirt, can_use_while_on_ground=False)

jacket = Item("jacket", "A weird looking jacket with minuscule red dots covering it.")
jacket.add_action("wear",
                  on_success="You put on the jacket. Only too late, you discover that it is seething with fire ants inside. You struggle to breath as the ants suffocate you to death.",
                  action=kill, can_use_while_on_ground=False)

giantdrawer = Item("drawers", "This giant chest of drawers is missing a leg. It's covered in spider webs.", can_pick_up=False)
giantdrawer.add_action("open",
                       on_success="You open the drawer and it starts wobbling. You quickly move to the right and avoid it falling on you.")

dressingroom.add_item(wardrobe, "A dusty brown Wardrobe stands against one wall. Its two doors lie closed.")
dressingroom.add_item(shirt, "A Shirt hangs on a clothing rack against the opposite wall.")
dressingroom.add_item(jacket, "Further down hangs a weird-looking Jacket.")
dressingroom.add_item(giantdrawer, "A giant chest of Drawers sits against the back wall.")

basement = Room("basement")
basement.description = "The wooden beams holding up the ceiling of this musty room are sagging dangerously. In front of you, they have given way; the room is blocked by an insurmountable pile of rubble. An old-fashioned dumbwaiter is mounted in the west wall, big enough to crawl inside."
basement.is_dark = True
basement.add_map("""
 _________
--        |
--        |
 ---------
""")

# ------------ Kyler does it again (thx man) ---------
basement_dumbwaiter = Room("basement dumbwaiter")
basement_dumbwaiter.description = "This old, deformed dumbwaiter is cluttered with rotten food and broken plates. It is barely usable. A hole to the east leads out into a musty basement."
basement_dumbwaiter.map = """"""
basement_dumbwaiter.floor = 0
basement_dumbwaiter.add_connecting_room(basement, "east")

kitchen_dumbwaiter = Room("kitchen dumbwaiter")
kitchen_dumbwaiter.description = "This old, deformed dumbwaiter is cluttered with rotten food and broken plates. It is barely usable. A hole to the east leads out into a cluttered kitchen."
kitchen_dumbwaiter.map = """"""
kitchen_dumbwaiter.floor = 1
kitchen_dumbwaiter.add_connecting_room(kitchen, "east")

masterbedroom_dumbwaiter = Room("masterbedroom dumbwaiter")
masterbedroom_dumbwaiter.description = "This old, deformed dumbwaiter is cluttered with rotten food and broken plates. It is barely usable. A hole to the east leads out into an opulent bedroom."
masterbedroom_dumbwaiter.map = """"""
masterbedroom_dumbwaiter.floor = 2
masterbedroom_dumbwaiter.add_connecting_room(masterbedroom, "east")


def send_to_room(room):
    PLAYER.location = room


def dumbwaiter(room, direction):
    if (direction == "broken"):
        print("Nothing happens...")
        return
    elif (room.floor == 0 or room.floor == 2):
        send_to_room(kitchen_dumbwaiter)
        print(kitchen_dumbwaiter.get_description())
    elif (room.floor == 1):
        if (direction == "up"):
            send_to_room(masterbedroom_dumbwaiter)
            print(masterbedroom_dumbwaiter.get_description())
        elif (direction == "down"):
            send_to_room(basement_dumbwaiter)
            print(basement_dumbwaiter.get_description())


def dumbwaiter_broken(item):
    dumbwaiter(PLAYER.location, "broken")


def dumbwaiter_up(item):
    dumbwaiter(PLAYER.location, "up")


def dumbwaiter_down(item):
    dumbwaiter(PLAYER.location, "down")


up_button = Item("up", "A button with a up arrow on it is mounted on the frame.", can_pick_up=False)
up_button.add_action("press", on_success="You press the button", action=dumbwaiter_up)
down_button = Item("down", "A button with a down arrow on it is mounted on the frame.", can_pick_up=False)
down_button.add_action("press", on_success="You press the button", action=dumbwaiter_down)
# up_button_broken = Item("up", "A button with a up arrow on it is mounted on the frame.", can_pick_up=False)
# up_button.add_action("press", on_success="You press the button", action=dumbwaiter_broken)
# down_button_broken = Item("down", "A button with a down arrow on it is mounted on the frame.", can_pick_up=False)
# down_button.add_action("press", on_success="You press the button", action=dumbwaiter_broken)

basement_dumbwaiter.add_item(up_button, 'A button with a button marked "Up" is mounted on the frame.')

kitchen_dumbwaiter.add_item(up_button, 'Buttons marked "Up" ')
kitchen_dumbwaiter.add_item(down_button, 'and "Down" are mounted on the frame.')

masterbedroom_dumbwaiter.add_item(down_button, 'A button with a button marked "Down" is mounted on the frame.')

# ------------ Tate (again) (because no one did this) (WHY) -----------------
foyer = Room("foyer")
foyer.description = "Your shoes click along the marble floor of this once opulent foyer. Your eyes follow the long hallway to your north, decorated with mirrors and oil paintings."
foyer.add_map("""
--------[   ]---------
|                    |
|                    |
|                    |
|                    |
--------▓▓▓▓----------
""")


def seal_front_door():
    if PLAYER.location == foyer:
        foyer.connectingRooms["south"] = None


def open_front_door(item):
    if not key in PLAYER.inventory:
        return False
    print(
        "You gulp in the fresh night air, tilting your face to the starry sky. Your chest heaves and you grip the file even harder. Congratulations player; you won.")
    time.sleep(3)
    PLAYER.win()
    return True


front_door = Item("door",
                  "This heavy oak door has an intricate coat of arms engraved on it. Strangely, the inner handle has a keyhole over it. It is locked.",
                  can_pick_up=False)
# front_door.add_action("open", on_success=" ", on_fail="You grasp the door handle, but it won't budge. Maybe you need a key?", action=open_front_door)
foyer.add_item(front_door,
               "A rush of wind sweeps around you, and you look behind, checking to make sure you closed the Door. You did.")

outside = Room("outside")
outside.description = "You stand in front of the Mansion. Cold, clammy tendrils of fog grasp at you. The tall wooden front door hangs ajar."
outside.add_map("""
|_____________[     ]________________|
               - - -
                - - -""")

# FLOOR 1 (north to south)
stairway.add_connecting_room(upper_hallway_north, "up")

lower_hallway_north.add_connecting_room(stairway, "up")
lower_hallway_south.add_connecting_room(lower_hallway_center, "north")
lower_hallway_center.add_connecting_room(lower_hallway_north, "north")

kitchen.add_connecting_room(lower_hallway_north, "east")
kitchen.add_connecting_room(madeleine_diningroom, "south")

library.add_connecting_room(lower_hallway_north, "west")

madeleine_diningroom.add_connecting_room(lower_hallway_center, "east")
madeleine_diningroom.add_connecting_room(katherine_ballroom, "south")

lounge.add_connecting_room(lower_hallway_center, "west")

katherine_ballroom.add_connecting_room(lower_hallway_south, "east")

Conservatory.add_connecting_room(lower_hallway_south, "west")

lower_hallway_south.add_connecting_room(foyer, "south")

foyer.add_connecting_room(outside, "south")

# FLOOR 2 (north to south)

stairway.add_connecting_room(upper_hallway_north, "up")

upper_hallway_south.add_connecting_room(upper_hallway_center, "north")
upper_hallway_center.add_connecting_room(upper_hallway_north, "north")

masterbedroom.add_connecting_room(dressingroom, "south")
masterbedroom.add_connecting_room(upper_hallway_north, "east")

BILLIARDS.add_connecting_room(upper_hallway_north, "west")

upper_hallway_south.add_connecting_room(MUSIC, "west")
upper_hallway_south.add_connecting_room(study, "east")

secret_passage_billiards.add_connecting_room(secret_passage_music, "west")

basement_dumbwaiter.add_connecting_room(kitchen_dumbwaiter, "up")
kitchen_dumbwaiter.add_connecting_room(masterbedroom_dumbwaiter, "up")

lower_hallway_south.add_connecting_room(lower_hallway_center, "north")
lower_hallway_center.add_connecting_room(lower_hallway_north, "north")

library.hint = "That’s a really interesting rug! Wow! Holy Rug! Maybe you should pick it up!!!!"
secret_passage_billiards.hint = "The Pendulum of the clock is important! It can be examined, and maybe interacted with in other ways..."
cellar.hint = "That Cabinet is... suspicious... *Among Us noises*"
BILLIARDS.hint = "You might want to look at the Cue Rack..."
MUSIC.hint = "That’s a cool Record Player."

# the place we want the character to start the game
STARTROOM = outside

# ----------------------------------------------------------

def display_death_message():
    if PLAYER.location == foyer and PLAYER.prev_location not in [outside, lower_hallway_south, foyer]:
        time.sleep(1)
        print()
        print("You have died.")
        print()
        time.sleep(1)
        print("You awaken resting on a cold, shiny marble floor. You get up and look around you. You are back in the foyer. The huge wooden Door to your south is still closed, and the hallway to the north is still lit by its flickering bulbs.")
        print(foyer.format_map())
        PLAYER.prev_location = foyer


PLAYER = Player()

PLAYER.onMove.append(seal_front_door)
PLAYER.onMove.append(check_for_secret_passage_exit)

# TODO: uncomment the line below if you want to playtest with administrator privileges. MAKE SURE IT'S COMMENTED BEFORE RELEASE!!!
PLAYER.add_item(admin_dice)

has_won = False
has_exited = False

if __name__ == '__main__':
    # main loop
    try:
        while not has_exited:
            while not has_won:
                if get_command() != "invalid":
                    do_command_update()
            print("\nThanks for playing!")
            if not has_exited:
                print("Run the game again to play from the start. See if you can discover more of the secrets of the Rowell Mansion (there are many)!\n")
            has_exited = True
            #if not has_exited:
            #    print()
            #    print("Do you want to play again? (y/n)")
            #    if input(" > ").lower().strip() in ["y", "yes", "again", "play again"]:
            #        has_won = False
            #        PLAYER = Player()
            #    else:
            #        has_exited = True
            #        break
    except KeyboardInterrupt:
        # exit message
        print("\nThanks for playing!")
