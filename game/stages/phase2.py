import pygame, random, sys, gc
from . import phase0
from game.stages.phase0 import *
from framework import assets, engine, animations, text
from framework.assets import *
from framework.geometry import *
from framework.stage import *

class ItemTag():
    FLOOR = 'Floor'
    WALL = 'Wall'
    WALL_ITEM = 'Wall Item'
    FURNITURE = 'Furniture'
    OBJECT = 'Object'


ITEM_TAGS = [
 ItemTag.FLOOR, ItemTag.WALL, ItemTag.WALL_ITEM, ItemTag.FURNITURE, ItemTag.OBJECT]

class ItemState():
    NORMAL = IsoState('Normal', '')
    OPENED = IsoState('Opened', 'o')


ITEM_STATES = [
 ItemState.NORMAL, ItemState.OPENED]

class PlaceHolderType():
    NORMALCLUE = (1, )
    NORMALITEM = (2, )
    BELOWCLUE = (3, )
    BELOWITEM = (4, )
    INSIDECLUE = (5, )
    INSIDEITEM = (6, )
    OUTSIDECLUE = (7, )
    OUTSIDEITEM = 8


class PlaceHolderTag():
    CLUEA = (
     'ClueA', ['i509'], PlaceHolderType.NORMALCLUE)
    CLUEB = ('ClueB', ['i529'], PlaceHolderType.NORMALCLUE)
    CLUEC = ('ClueC', ['i511'], PlaceHolderType.NORMALCLUE)
    CLUED = ('ClueD', ['i510'], PlaceHolderType.NORMALCLUE)
    CLUEE = ('ClueE', ['i526'], PlaceHolderType.NORMALCLUE)
    CLUEF = ('ClueF', ['i527'], PlaceHolderType.NORMALCLUE)
    CLUEG = ('ClueG', ['i528'], PlaceHolderType.NORMALCLUE)
    CLUEH = ('ClueH', ['i523'], PlaceHolderType.NORMALCLUE)
    ITEMA = ('ItemA', ['i505'], PlaceHolderType.NORMALITEM)
    ITEMB = ('ItemB', ['i503'], PlaceHolderType.NORMALITEM)
    ITEMC = ('ItemC', ['i504'], PlaceHolderType.NORMALITEM)
    ITEMD = ('ItemD', ['i512'], PlaceHolderType.NORMALITEM)
    ITEME = ('ItemE', ['i507'], PlaceHolderType.NORMALITEM)
    ITEMF = ('ItemF', ['i502'], PlaceHolderType.NORMALITEM)
    ITEMG = ('ItemG', ['i501'], PlaceHolderType.NORMALITEM)
    ITEMH = ('ItemH', ['i513'], PlaceHolderType.NORMALITEM)
    ITEMI = ('ItemI', ['i534'], PlaceHolderType.NORMALITEM)
    ITEMJ = ('ItemJ', ['i535'], PlaceHolderType.NORMALITEM)
    ITEMK = ('ItemK', ['i536'], PlaceHolderType.NORMALITEM)
    ITEML = ('ItemL', ['i537'], PlaceHolderType.NORMALITEM)
    ITEMM = ('ItemM', ['i538'], PlaceHolderType.NORMALITEM)
    ITEMN = ('ItemN', ['i539'], PlaceHolderType.NORMALITEM)
    ITEMO = ('ItemO', ['i540'], PlaceHolderType.NORMALITEM)
    ITEMP = ('ItemP', ['i541'], PlaceHolderType.NORMALITEM)
    ITEMQ = ('ItemQ', ['i542'], PlaceHolderType.NORMALITEM)
    ITEMR = ('ItemR', ['i543'], PlaceHolderType.NORMALITEM)
    ITEMS = ('ItemS', ['i544'], PlaceHolderType.NORMALITEM)
    ITEMT = ('ItemT', ['i545'], PlaceHolderType.NORMALITEM)
    ITEMU = ('ItemU', ['i546'], PlaceHolderType.NORMALITEM)
    ITEMV = ('ItemV', ['i547'], PlaceHolderType.NORMALITEM)
    ITEMW = ('ItemW', ['i548'], PlaceHolderType.NORMALITEM)
    ITEMX = ('ItemX', ['i549'], PlaceHolderType.NORMALITEM)
    ITEMY = ('ItemY', ['i550'], PlaceHolderType.NORMALITEM)
    ITEMZ = ('ItemZ', ['i551'], PlaceHolderType.NORMALITEM)
    ITEMZA = ('ItemZA', ['i552'], PlaceHolderType.NORMALITEM)
    ITEMZB = ('ItemZB', ['i553'], PlaceHolderType.NORMALITEM)
    ITEMZC = ('ItemZC', ['i554'], PlaceHolderType.NORMALITEM)
    ITEMZD = ('ItemZD', ['i555'], PlaceHolderType.NORMALITEM)
    ITEMZE = ('ItemZE', ['i556'], PlaceHolderType.NORMALITEM)
    ITEMZF = ('ItemZF', ['i557'], PlaceHolderType.NORMALITEM)
    ITEMZG = ('ItemZG', ['i558'], PlaceHolderType.NORMALITEM)
    BELOWCLUEA = (
     'BelowClueA', ['i509'], PlaceHolderType.BELOWCLUE)
    BELOWCLUEB = ('BelowClueB', ['i529'], PlaceHolderType.BELOWCLUE)
    BELOWCLUEC = ('BelowClueC', ['i511'], PlaceHolderType.BELOWCLUE)
    BELOWCLUED = ('BelowClueD', ['i510'], PlaceHolderType.BELOWCLUE)
    BELOWCLUEE = ('BelowClueE', ['i526'], PlaceHolderType.BELOWCLUE)
    BELOWCLUEF = ('BelowClueF', ['i527'], PlaceHolderType.BELOWCLUE)
    BELOWCLUEG = ('BelowClueG', ['i528'], PlaceHolderType.BELOWCLUE)
    BELOWCLUEH = ('BelowClueH', ['i523'], PlaceHolderType.BELOWCLUE)
    BELOWITEMA = ('BelowItemA', ['i505'], PlaceHolderType.BELOWITEM)
    BELOWITEMB = ('BelowItemB', ['i503'], PlaceHolderType.BELOWITEM)
    BELOWITEMC = ('BelowItemC', ['i504'], PlaceHolderType.BELOWITEM)
    BELOWITEMD = ('BelowItemD', ['i512'], PlaceHolderType.BELOWITEM)
    BELOWITEME = ('BelowItemE', ['i507'], PlaceHolderType.BELOWITEM)
    BELOWITEMF = ('BelowItemF', ['i502'], PlaceHolderType.BELOWITEM)
    BELOWITEMG = ('BelowItemG', ['i501'], PlaceHolderType.BELOWITEM)
    BELOWITEMH = ('BelowItemH', ['i513'], PlaceHolderType.BELOWITEM)
    BELOWITEMI = ('BelowItemI', ['i534'], PlaceHolderType.BELOWITEM)
    BELOWITEMJ = ('BelowItemJ', ['i535'], PlaceHolderType.BELOWITEM)
    BELOWITEMK = ('BelowItemK', ['i536'], PlaceHolderType.BELOWITEM)
    BELOWITEML = ('BelowItemL', ['i537'], PlaceHolderType.BELOWITEM)
    BELOWITEMM = ('BelowItemM', ['i538'], PlaceHolderType.BELOWITEM)
    BELOWITEMN = ('BelowItemN', ['i539'], PlaceHolderType.BELOWITEM)
    BELOWITEMO = ('BelowItemO', ['i540'], PlaceHolderType.BELOWITEM)
    BELOWITEMP = ('BelowItemP', ['i541'], PlaceHolderType.BELOWITEM)
    BELOWITEMQ = ('BelowItemQ', ['i542'], PlaceHolderType.BELOWITEM)
    BELOWITEMR = ('BelowItemR', ['i543'], PlaceHolderType.BELOWITEM)
    BELOWITEMS = ('BelowItemS', ['i544'], PlaceHolderType.BELOWITEM)
    BELOWITEMT = ('BelowItemT', ['i545'], PlaceHolderType.BELOWITEM)
    BELOWITEMU = ('BelowItemU', ['i546'], PlaceHolderType.BELOWITEM)
    BELOWITEMV = ('BelowItemV', ['i547'], PlaceHolderType.BELOWITEM)
    BELOWITEMW = ('BelowItemW', ['i548'], PlaceHolderType.BELOWITEM)
    BELOWITEMX = ('BelowItemX', ['i549'], PlaceHolderType.BELOWITEM)
    BELOWITEMY = ('BelowItemY', ['i550'], PlaceHolderType.BELOWITEM)
    BELOWITEMZ = ('BelowItemZ', ['i551'], PlaceHolderType.BELOWITEM)
    BELOWITEMZA = ('BelowItemZA', ['i552'], PlaceHolderType.BELOWITEM)
    BELOWITEMZB = ('BelowItemZB', ['i553'], PlaceHolderType.BELOWITEM)
    BELOWITEMZC = ('BelowItemZC', ['i554'], PlaceHolderType.BELOWITEM)
    BELOWITEMZD = ('BelowItemZD', ['i555'], PlaceHolderType.BELOWITEM)
    BELOWITEMZE = ('BelowItemZE', ['i556'], PlaceHolderType.BELOWITEM)
    BELOWITEMZF = ('BelowItemZF', ['i557'], PlaceHolderType.BELOWITEM)
    BELOWITEMZG = ('BelowItemZG', ['i558'], PlaceHolderType.BELOWITEM)
    INSIDECLUEA = (
     'InsideClueA', ['i509'], PlaceHolderType.INSIDECLUE)
    INSIDECLUEB = ('InsideClueB', ['i529'], PlaceHolderType.INSIDECLUE)
    INSIDECLUEC = ('InsideClueC', ['i511'], PlaceHolderType.INSIDECLUE)
    INSIDECLUED = ('InsideClueD', ['i510'], PlaceHolderType.INSIDECLUE)
    INSIDECLUEE = ('InsideClueE', ['i526'], PlaceHolderType.INSIDECLUE)
    INSIDECLUEF = ('InsideClueF', ['i527'], PlaceHolderType.INSIDECLUE)
    INSIDECLUEG = ('InsideClueG', ['i528'], PlaceHolderType.INSIDECLUE)
    INSIDECLUEH = ('InsideClueH', ['i523'], PlaceHolderType.INSIDECLUE)
    INSIDEITEMA = ('InsideItemA', ['i505'], PlaceHolderType.INSIDECLUE)
    INSIDEITEMB = ('InsideItemB', ['i503'], PlaceHolderType.INSIDEITEM)
    INSIDEITEMC = ('InsideItemC', ['i504'], PlaceHolderType.INSIDEITEM)
    INSIDEITEMD = ('InsideItemD', ['i512'], PlaceHolderType.INSIDEITEM)
    INSIDEITEME = ('InsideItemE', ['i507'], PlaceHolderType.INSIDEITEM)
    INSIDEITEMF = ('InsideItemF', ['i502'], PlaceHolderType.INSIDEITEM)
    INSIDEITEMG = ('InsideItemG', ['i501'], PlaceHolderType.INSIDEITEM)
    INSIDEITEMH = ('InsideItemH', ['i513'], PlaceHolderType.INSIDEITEM)
    INSIDEITEMI = ('InsideItemI', ['i534'], PlaceHolderType.INSIDEITEM)
    INSIDEITEMJ = ('InsideItemJ', ['i535'], PlaceHolderType.INSIDEITEM)
    INSIDEITEMK = ('InsideItemK', ['i536'], PlaceHolderType.INSIDEITEM)
    INSIDEITEML = ('InsideItemL', ['i537'], PlaceHolderType.INSIDEITEM)
    INSIDEITEMM = ('InsideItemM', ['i538'], PlaceHolderType.INSIDEITEM)
    INSIDEITEMN = ('InsideItemN', ['i539'], PlaceHolderType.INSIDEITEM)
    INSIDEITEMO = ('InsideItemO', ['i540'], PlaceHolderType.INSIDEITEM)
    INSIDEITEMP = ('InsideItemP', ['i541'], PlaceHolderType.INSIDEITEM)
    INSIDEITEMQ = ('InsideItemQ', ['i542'], PlaceHolderType.INSIDEITEM)
    INSIDEITEMR = ('InsideItemR', ['i543'], PlaceHolderType.INSIDEITEM)
    INSIDEITEMS = ('InsideItemS', ['i544'], PlaceHolderType.INSIDEITEM)
    INSIDEITEMT = ('InsideItemT', ['i545'], PlaceHolderType.INSIDEITEM)
    INSIDEITEMU = ('InsideItemU', ['i546'], PlaceHolderType.INSIDEITEM)
    INSIDEITEMV = ('InsideItemV', ['i547'], PlaceHolderType.INSIDEITEM)
    INSIDEITEMW = ('InsideItemW', ['i548'], PlaceHolderType.INSIDEITEM)
    INSIDEITEMX = ('InsideItemX', ['i549'], PlaceHolderType.INSIDEITEM)
    INSIDEITEMY = ('InsideItemY', ['i550'], PlaceHolderType.INSIDEITEM)
    INSIDEITEMZ = ('InsideItemZ', ['i551'], PlaceHolderType.INSIDEITEM)
    INSIDEITEMZA = ('InsideItemZA', ['i552'], PlaceHolderType.INSIDEITEM)
    INSIDEITEMZB = ('InsideItemZB', ['i553'], PlaceHolderType.INSIDEITEM)
    INSIDEITEMZC = ('InsideItemZC', ['i554'], PlaceHolderType.INSIDEITEM)
    INSIDEITEMZD = ('InsideItemZD', ['i555'], PlaceHolderType.INSIDEITEM)
    INSIDEITEMZE = ('InsideItemZE', ['i556'], PlaceHolderType.INSIDEITEM)
    INSIDEITEMZF = ('InsideItemZF', ['i557'], PlaceHolderType.INSIDEITEM)
    INSIDEITEMZG = ('InsideItemZG', ['i558'], PlaceHolderType.INSIDEITEM)
    OUTSIDECLUEA = (
     'OutsideClueA', ['i509'], PlaceHolderType.OUTSIDECLUE)
    OUTSIDECLUEB = ('OutsideClueB', ['i529'], PlaceHolderType.OUTSIDECLUE)
    OUTSIDECLUEC = ('OutsideClueC', ['i511'], PlaceHolderType.OUTSIDECLUE)
    OUTSIDECLUED = ('OutsideClueD', ['i510'], PlaceHolderType.OUTSIDECLUE)
    OUTSIDECLUEE = ('OutsideClueE', ['i526'], PlaceHolderType.OUTSIDECLUE)
    OUTSIDECLUEF = ('OutsideClueF', ['i527'], PlaceHolderType.OUTSIDECLUE)
    OUTSIDECLUEG = ('OutsideClueG', ['i528'], PlaceHolderType.OUTSIDECLUE)
    OUTSIDECLUEH = ('OutsideClueH', ['i523'], PlaceHolderType.OUTSIDECLUE)
    OUTSIDEITEMA = ('OutsideItemA', ['i505'], PlaceHolderType.OUTSIDECLUE)
    OUTSIDEITEMB = ('OutsideItemB', ['i503'], PlaceHolderType.OUTSIDEITEM)
    OUTSIDEITEMC = ('OutsideItemC', ['i504'], PlaceHolderType.OUTSIDEITEM)
    OUTSIDEITEMD = ('OutsideItemD', ['i512'], PlaceHolderType.OUTSIDEITEM)
    OUTSIDEITEME = ('OutsideItemE', ['i507'], PlaceHolderType.OUTSIDEITEM)
    OUTSIDEITEMF = ('OutsideItemF', ['i502'], PlaceHolderType.OUTSIDEITEM)
    OUTSIDEITEMG = ('OutsideItemG', ['i501'], PlaceHolderType.OUTSIDEITEM)
    OUTSIDEITEMH = ('OutsideItemH', ['i513'], PlaceHolderType.OUTSIDEITEM)
    OUTSIDEITEMI = ('OutsideItemI', ['i534'], PlaceHolderType.OUTSIDEITEM)
    OUTSIDEITEMJ = ('OutsideItemJ', ['i535'], PlaceHolderType.OUTSIDEITEM)
    OUTSIDEITEMK = ('OutsideItemK', ['i536'], PlaceHolderType.OUTSIDEITEM)
    OUTSIDEITEML = ('OutsideItemL', ['i537'], PlaceHolderType.OUTSIDEITEM)
    OUTSIDEITEMM = ('OutsideItemM', ['i538'], PlaceHolderType.OUTSIDEITEM)
    OUTSIDEITEMN = ('OutsideItemN', ['i539'], PlaceHolderType.OUTSIDEITEM)
    OUTSIDEITEMO = ('OutsideItemO', ['i540'], PlaceHolderType.OUTSIDEITEM)
    OUTSIDEITEMP = ('OutsideItemP', ['i541'], PlaceHolderType.OUTSIDEITEM)
    OUTSIDEITEMQ = ('OutsideItemQ', ['i542'], PlaceHolderType.OUTSIDEITEM)
    OUTSIDEITEMR = ('OutsideItemR', ['i543'], PlaceHolderType.OUTSIDEITEM)
    OUTSIDEITEMS = ('OutsideItemS', ['i544'], PlaceHolderType.OUTSIDEITEM)
    OUTSIDEITEMT = ('OutsideItemT', ['i545'], PlaceHolderType.OUTSIDEITEM)
    OUTSIDEITEMU = ('OutsideItemU', ['i546'], PlaceHolderType.OUTSIDEITEM)
    OUTSIDEITEMV = ('OutsideItemV', ['i547'], PlaceHolderType.OUTSIDEITEM)
    OUTSIDEITEMW = ('OutsideItemW', ['i548'], PlaceHolderType.OUTSIDEITEM)
    OUTSIDEITEMX = ('OutsideItemX', ['i549'], PlaceHolderType.OUTSIDEITEM)
    OUTSIDEITEMY = ('OutsideItemY', ['i550'], PlaceHolderType.OUTSIDEITEM)
    OUTSIDEITEMZ = ('OutsideItemZ', ['i551'], PlaceHolderType.OUTSIDEITEM)
    OUTSIDEITEMZA = ('OutsideItemZA', ['i552'], PlaceHolderType.OUTSIDEITEM)
    OUTSIDEITEMZB = ('OutsideItemZB', ['i553'], PlaceHolderType.OUTSIDEITEM)
    OUTSIDEITEMZC = ('OutsideItemZC', ['i554'], PlaceHolderType.OUTSIDEITEM)
    OUTSIDEITEMZD = ('OutsideItemZD', ['i555'], PlaceHolderType.OUTSIDEITEM)
    OUTSIDEITEMZE = ('OutsideItemZE', ['i556'], PlaceHolderType.OUTSIDEITEM)
    OUTSIDEITEMZF = ('OutsideItemZF', ['i557'], PlaceHolderType.OUTSIDEITEM)
    OUTSIDEITEMZG = ('OutsideItemZG', ['i558'], PlaceHolderType.OUTSIDEITEM)


PLACE_HOLDER_TAGS = [
 PlaceHolderTag.CLUEA,
 PlaceHolderTag.CLUEB,
 PlaceHolderTag.CLUEC,
 PlaceHolderTag.CLUED,
 PlaceHolderTag.CLUEE,
 PlaceHolderTag.CLUEF,
 PlaceHolderTag.CLUEG,
 PlaceHolderTag.CLUEH,
 PlaceHolderTag.ITEMA,
 PlaceHolderTag.ITEMB,
 PlaceHolderTag.ITEMC,
 PlaceHolderTag.ITEMD,
 PlaceHolderTag.ITEME,
 PlaceHolderTag.ITEMF,
 PlaceHolderTag.ITEMG,
 PlaceHolderTag.ITEMH,
 PlaceHolderTag.ITEMI,
 PlaceHolderTag.ITEMJ,
 PlaceHolderTag.ITEMK,
 PlaceHolderTag.ITEML,
 PlaceHolderTag.ITEMM,
 PlaceHolderTag.ITEMN,
 PlaceHolderTag.ITEMO,
 PlaceHolderTag.ITEMP,
 PlaceHolderTag.ITEMQ,
 PlaceHolderTag.ITEMR,
 PlaceHolderTag.ITEMS,
 PlaceHolderTag.ITEMT,
 PlaceHolderTag.ITEMU,
 PlaceHolderTag.ITEMV, PlaceHolderTag.ITEMW,
 PlaceHolderTag.ITEMX,
 PlaceHolderTag.ITEMY,
 PlaceHolderTag.ITEMZ,
 PlaceHolderTag.ITEMZA,
 PlaceHolderTag.ITEMZB,
 PlaceHolderTag.ITEMZC,
 PlaceHolderTag.ITEMZD,
 PlaceHolderTag.ITEMZE,
 PlaceHolderTag.ITEMZF,
 PlaceHolderTag.ITEMZG,
 PlaceHolderTag.BELOWCLUEA,
 PlaceHolderTag.BELOWCLUEB,
 PlaceHolderTag.BELOWCLUEC,
 PlaceHolderTag.BELOWCLUED,
 PlaceHolderTag.BELOWCLUEE,
 PlaceHolderTag.BELOWCLUEF,
 PlaceHolderTag.BELOWCLUEG,
 PlaceHolderTag.BELOWCLUEH,
 PlaceHolderTag.BELOWITEMA,
 PlaceHolderTag.BELOWITEMB,
 PlaceHolderTag.BELOWITEMC,
 PlaceHolderTag.BELOWITEMD,
 PlaceHolderTag.BELOWITEME,
 PlaceHolderTag.BELOWITEMF,
 PlaceHolderTag.BELOWITEMG,
 PlaceHolderTag.BELOWITEMH,
 PlaceHolderTag.BELOWITEMI,
 PlaceHolderTag.BELOWITEMJ,
 PlaceHolderTag.BELOWITEMK,
 PlaceHolderTag.BELOWITEML,
 PlaceHolderTag.BELOWITEMM,
 PlaceHolderTag.BELOWITEMN,
 PlaceHolderTag.BELOWITEMO,
 PlaceHolderTag.BELOWITEMP,
 PlaceHolderTag.BELOWITEMQ,
 PlaceHolderTag.BELOWITEMR,
 PlaceHolderTag.BELOWITEMS,
 PlaceHolderTag.BELOWITEMT,
 PlaceHolderTag.BELOWITEMU,
 PlaceHolderTag.BELOWITEMV,
 PlaceHolderTag.BELOWITEMW,
 PlaceHolderTag.BELOWITEMX,
 PlaceHolderTag.BELOWITEMY,
 PlaceHolderTag.BELOWITEMZ,
 PlaceHolderTag.BELOWITEMZA,
 PlaceHolderTag.BELOWITEMZB,
 PlaceHolderTag.BELOWITEMZC,
 PlaceHolderTag.BELOWITEMZD,
 PlaceHolderTag.BELOWITEMZE,
 PlaceHolderTag.BELOWITEMZF,
 PlaceHolderTag.BELOWITEMZG,
 PlaceHolderTag.INSIDECLUEA,
 PlaceHolderTag.INSIDECLUEB,
 PlaceHolderTag.INSIDECLUEC,
 PlaceHolderTag.INSIDECLUED,
 PlaceHolderTag.INSIDECLUEE,
 PlaceHolderTag.INSIDECLUEF,
 PlaceHolderTag.INSIDECLUEG,
 PlaceHolderTag.INSIDECLUEH,
 PlaceHolderTag.INSIDEITEMA,
 PlaceHolderTag.INSIDEITEMB,
 PlaceHolderTag.INSIDEITEMC,
 PlaceHolderTag.INSIDEITEMD,
 PlaceHolderTag.INSIDEITEME,
 PlaceHolderTag.INSIDEITEMF,
 PlaceHolderTag.INSIDEITEMG,
 PlaceHolderTag.INSIDEITEMH,
 PlaceHolderTag.INSIDEITEMI,
 PlaceHolderTag.INSIDEITEMJ,
 PlaceHolderTag.INSIDEITEMK,
 PlaceHolderTag.INSIDEITEML,
 PlaceHolderTag.INSIDEITEMM,
 PlaceHolderTag.INSIDEITEMN,
 PlaceHolderTag.INSIDEITEMO,
 PlaceHolderTag.INSIDEITEMP,
 PlaceHolderTag.INSIDEITEMQ,
 PlaceHolderTag.INSIDEITEMR,
 PlaceHolderTag.INSIDEITEMS,
 PlaceHolderTag.INSIDEITEMT,
 PlaceHolderTag.INSIDEITEMU,
 PlaceHolderTag.INSIDEITEMV,
 PlaceHolderTag.INSIDEITEMW,
 PlaceHolderTag.INSIDEITEMX,
 PlaceHolderTag.INSIDEITEMY,
 PlaceHolderTag.INSIDEITEMZ,
 PlaceHolderTag.INSIDEITEMZA,
 PlaceHolderTag.INSIDEITEMZB,
 PlaceHolderTag.INSIDEITEMZC,
 PlaceHolderTag.INSIDEITEMZD,
 PlaceHolderTag.INSIDEITEMZE,
 PlaceHolderTag.INSIDEITEMZF,
 PlaceHolderTag.INSIDEITEMZG,
 PlaceHolderTag.OUTSIDECLUEA,
 PlaceHolderTag.OUTSIDECLUEB,
 PlaceHolderTag.OUTSIDECLUEC,
 PlaceHolderTag.OUTSIDECLUED,
 PlaceHolderTag.OUTSIDECLUEE,
 PlaceHolderTag.OUTSIDECLUEF,
 PlaceHolderTag.OUTSIDECLUEG,
 PlaceHolderTag.OUTSIDECLUEH,
 PlaceHolderTag.OUTSIDEITEMA,
 PlaceHolderTag.OUTSIDEITEMB,
 PlaceHolderTag.OUTSIDEITEMC,
 PlaceHolderTag.OUTSIDEITEMD,
 PlaceHolderTag.OUTSIDEITEME,
 PlaceHolderTag.OUTSIDEITEMF,
 PlaceHolderTag.OUTSIDEITEMG,
 PlaceHolderTag.OUTSIDEITEMH,
 PlaceHolderTag.OUTSIDEITEMI,
 PlaceHolderTag.OUTSIDEITEMJ,
 PlaceHolderTag.OUTSIDEITEMK,
 PlaceHolderTag.OUTSIDEITEML,
 PlaceHolderTag.OUTSIDEITEMM,
 PlaceHolderTag.OUTSIDEITEMN,
 PlaceHolderTag.OUTSIDEITEMO,
 PlaceHolderTag.OUTSIDEITEMP,
 PlaceHolderTag.OUTSIDEITEMQ,
 PlaceHolderTag.OUTSIDEITEMR,
 PlaceHolderTag.OUTSIDEITEMS,
 PlaceHolderTag.OUTSIDEITEMT,
 PlaceHolderTag.OUTSIDEITEMU,
 PlaceHolderTag.OUTSIDEITEMV,
 PlaceHolderTag.OUTSIDEITEMW,
 PlaceHolderTag.OUTSIDEITEMX,
 PlaceHolderTag.OUTSIDEITEMY,
 PlaceHolderTag.OUTSIDEITEMZ,
 PlaceHolderTag.OUTSIDEITEMZA,
 PlaceHolderTag.OUTSIDEITEMZB,
 PlaceHolderTag.OUTSIDEITEMZC,
 PlaceHolderTag.OUTSIDEITEMZD,
 PlaceHolderTag.OUTSIDEITEMZE,
 PlaceHolderTag.OUTSIDEITEMZF,
 PlaceHolderTag.OUTSIDEITEMZG]

class Phase2Content(phase0.PhaseContent):

    def __init__(self):
        return

    def initialize(self, game, stage):
        self.game = game
        self.stage = stage
        self.hand = ItemImage(0, 0, assets.load_image('hand_cursor.png'))
        self.hand_item = ItemImage(0, 0, assets.load_image('hand_item.png'))
        self.hand_magnifier = ItemImage(0, 0, assets.load_image('hand_magnifiergrab.png'))
        self.hand_open = ItemImage(0, 0, assets.load_image('p2_handcursor_open_002.png'))
        self.magnifier_take_sound = assets.load_sound('p2_magnifying_glass_grab.ogg')
        self.magnifier_drop_sound = assets.load_sound('p2_magnifying_glass_drop.ogg')
        self.no_clue_sound = assets.load_sound('No_Pista_Mujer.ogg')
        self.clue_sound = assets.load_sound('p1_minigame_right.ogg')
        self.door_close_big_sound = assets.load_sound('p2_door_close_big.ogg')
        self.door_close_small_sound = assets.load_sound('p2_door_close_small.ogg')
        self.door_open_big_sound = assets.load_sound('p2_door_open_big.ogg')
        self.door_open_small_sound = assets.load_sound('p2_door_open_small.ogg')
        self.drawer_open_sound = assets.load_sound('p2_drawer_open.ogg')
        self.drawer_close_sound = assets.load_sound('p2_drawer_close.ogg')
        self.fridge_open_sound = assets.load_sound('p2_fridge_open.ogg')
        self.fridge_close_sound = assets.load_sound('p2_fridge_close.ogg')
        self.chest_open_sound = assets.load_sound('p2_chest_open.ogg')
        self.chest_close_sound = assets.load_sound('p2_chest_close.ogg')
        self.oven_open_sound = assets.load_sound('p2_oven_open.ogg')
        self.oven_close_sound = assets.load_sound('p2_oven_close.ogg')
        self.music_intro = assets.load_music('p2_music_intro.ogg')
        self.music_loop = assets.load_music('p2_music_loop.ogg')
        self.magnifier_taken = False
        self.clues_count = 0
        self.build_tags_dictionary()
        return

    def get_music(self):
        return (
         self.music_intro, self.music_loop)

    def add_content_layers(self):
        self.stage.prepare_items_set(self.stage, False)
        self.small_back_layer = Layer()
        self.small_items_layer = Layer()
        self.magnifier_layer = Layer()
        self.large_back_layer = Layer()
        self.large_items_layer = Layer()
        self.stage.add_layer(self.small_back_layer)
        self.stage.add_layer(self.small_items_layer)
        self.magnifier_image = assets.load_image('p2-magnifier.png')
        self.magnifier_mask = assets.load_mask('p2-magnifier-mask.gif')
        magnifier_width = self.magnifier_image.get_width()
        magnifier_height = self.magnifier_image.get_height()
        self.magnifier = ItemCustomDraw(330, 170, magnifier_width, magnifier_height, self.draw_magnifier, self.magnifier_mask)
        self.magnifier.add_event_handler(ItemEvent.CLICK, self.magnifier_click)
        self.magnifier.add_event_handler(ItemEvent.MOUSE_MOVE, self.magnifier_mouse_move)
        self.magnifier.add_event_handler(ItemEvent.MOUSE_LEAVE, self.magnifier_mouse_leave)
        self.magnifier_layer.add(self.magnifier)
        (stage_width, stage_height) = self.game.window.get_size()
        target_surface = pygame.Surface((stage_width * 2, stage_height * 2))
        large_background = assets.load_image('p0_stage_background_large.jpg')
        self.large_stage = StageIso(self.game, ITEM_TAGS, large_background, target_surface)
        self.large_stage.set_changed_handler(self.large_stage_changed)
        self.stage.prepare_items_set(self.large_stage, True, self.stage.get_item_definitions())
        self.large_stage.add_layer(self.large_back_layer)
        self.large_stage.add_layer(self.large_items_layer)
        self.stage.set_prerender_buffer(self.small_items_layer)
        self.build_stage()
        return

    def add_above_options_layers(self):
        self.stage.add_layer(self.magnifier_layer)
        return

    def add_above_info_layers(self):
        self.items_found_layer = Layer()
        self.stage.add_layer(self.items_found_layer)
        self.load_progress()
        return

    def load_progress(self):
        case = self.stage.game.datastore.user_character_progress.case
        clues_found = case.clues_found[:]
        for clue_found in clues_found:
            for item in self.large_items_layer.items:
                if item.get_type() == clue_found and hasattr(item, 'is_clue') and item.is_clue:
                    self.found_item(item, False)
                    break

        return

    def magnifier_click(self, item, args):
        if self.magnifier_taken:
            new_mouse_x = self.magnifier.get_left() + 74
            new_mouse_y = self.magnifier.get_top() + 66
            self.drop_magnifier()
            self.stage.set_mouse_pos(new_mouse_x, new_mouse_y)
            self.magnifier_drop_sound.play()
            if self.stage.hit_test(new_mouse_x, new_mouse_y) == self.magnifier:
                args.x = new_mouse_x
                args.y = new_mouse_y
                self.magnifier_mouse_move(item, args)
        else:
            (result, hit_test_item) = self.hit_test_over_magnifier(item, args.x, args.y)
            if result == 1:
                self.stage.set_mouse_cursor(self.magnifier, (
                 _div(self.magnifier.get_width() , 2), _div(self.magnifier.get_height() , 2)), False, False, Rect(88, 65, 648, 535))
                pygame.event.set_grab(True)
                self.magnifier_taken = True
                self.magnifier_take_sound.play()
            elif result == 2:
                self.show_item_found_message(hit_test_item, True)
            elif result == 3:
                state = hit_test_item.get_state()
                if state == ItemState.NORMAL:
                    hit_test_item.set_state(ItemState.OPENED)
                    hit_test_item.small_item.set_state(ItemState.OPENED)
                else:
                    hit_test_item.set_state(ItemState.NORMAL)
                    hit_test_item.small_item.set_state(ItemState.NORMAL)
                self.update_magnifier_mouse_cursor(item, args)
                self.stage.render()
                if state == ItemState.NORMAL:
                    type = hit_test_item.get_type()
                    if type == 'i101':
                        self.drawer_open_sound.play()
                    elif type == 'i105':
                        self.oven_open_sound.play()
                    elif type == 'i106':
                        self.fridge_open_sound.play()
                    elif type == 'i116':
                        self.chest_open_sound.play()
                    elif type == 'i110' or type == 'i104' or type == 'i108' or type == 'i125':
                        self.door_open_small_sound.play()
                    else:
                        self.door_open_big_sound.play()
                else:
                    type = hit_test_item.get_type()
                    if type == 'i101':
                        self.drawer_close_sound.play()
                    elif type == 'i105':
                        self.oven_close_sound.play()
                    elif type == 'i106':
                        self.fridge_close_sound.play()
                    elif type == 'i116':
                        self.chest_close_sound.play()
                    elif type == 'i110' or type == 'i104' or type == 'i108' or type == 'i125':
                        self.door_close_small_sound.play()
                    else:
                        self.door_close_big_sound.play()
        return

    def magnifier_mouse_move(self, item, args):
        self.update_magnifier_mouse_cursor(item, args)
        return

    def update_magnifier_mouse_cursor(self, item, args):
        if not self.magnifier_taken:
            (result, hit_test_item) = self.hit_test_over_magnifier(item, args.x, args.y)
            if result == 0:
                self.stage.set_mouse_cursor(None)
            elif result == 1:
                self.stage.set_mouse_cursor(self.hand_magnifier, (25, 30))
            elif result == 2:
                self.stage.set_mouse_cursor(self.hand_item, (23, 18))
            elif result == 3:
                self.stage.set_mouse_cursor(self.hand_open, (25, 20))
            else:
                self.stage.set_mouse_cursor(self.hand, (23, 18))
        return

    def hit_test_over_magnifier(self, item, x, y):
        hand_center_x = x - item.get_left()
        hand_center_y = y - item.get_top()
        if hand_center_x >= 0 and hand_center_y >= 0 and hand_center_x < self.magnifier_mask.get_width() and hand_center_y < self.magnifier_mask.get_height():
            c = self.magnifier_mask.get_at((hand_center_x, hand_center_y))
            if c == (255, 0, 0, 255):
                return (1, None)
            else:
                c_2 = self.magnifier_mask.get_at((hand_center_x, hand_center_y))
                if c == (0, 0, 255, 255) or c_2 == (0, 0, 255, 255):
                    (large_x, large_y) = self.get_amplified_pos(x, y)
                    hit_test_stack = self.large_stage.hit_test_stack(large_x, large_y, True)
                    for hit_test_item in hit_test_stack:
                        if isinstance(hit_test_item, ItemCell):
                            if hasattr(hit_test_item, 'is_clue'):
                                return (
                                 2, hit_test_item)
                            elif hit_test_item.get_definition().has_state(ItemState.OPENED):
                                has_outside_item = False
                                small_item = hit_test_item.small_item
                                if hasattr(small_item, 'place_holders_used'):
                                    for place_holder in small_item.place_holders_used:
                                        if place_holder.outside:
                                            has_outside_item = True
                                            break

                                if not has_outside_item:
                                    c = hit_test_item.get_at_mask(large_x, large_y, 'm')
                                    if c == (0, 0, 0, 255):
                                        return (
                                         3, hit_test_item)

                    return (4, None)
                else:
                    return (0, None)
        return (0, None)

    def drop_magnifier(self):
        if self.magnifier_taken:
            pygame.event.set_grab(False)
            self.magnifier_taken = False
            self.stage.set_mouse_cursor(None)
        return

    def magnifier_mouse_leave(self, item, args):
        mouse_cursor = self.stage.get_mouse_cursor()
        if mouse_cursor == self.hand or mouse_cursor == self.hand_item or mouse_cursor == self.hand_open or mouse_cursor == self.hand_magnifier:
            self.stage.set_mouse_cursor(None)
        return

    def show_item_found_message(self, item, from_stage):
        self.items_layer_selected_item = item
        if item.is_clue:
            sound = self.clue_sound
            self.update_case_last_department_lair()
            self.item_dialog = self.stage.show_clue_message(item, from_stage, False, self.item_dialog_close_click)
            if from_stage:
                clue_id = item.stage_clue.clue.id
                case = self.game.datastore.user_character_progress.case
                if clue_id not in case.clues_found:
                    case.clues_found.append(clue_id)
                self.stage.render()
                self.stage.save_progress(False)
        else:
            dialog = Layer()
            font = assets.load_font('evilgeniusbb_reg.ttf', 13)
            image = assets.load_image('p2_avatar_dialog_notaclue.png')
            box = ItemImage(62, 198, image)
            dialog.add(box)
            message = 'Esto no parece ser una pista interesante...'
            message = text.to_upper(message)
            text_item = ItemText(122, 239, font, 12, message, (0, 0, 0), None, 210, 30, 2, 2)
            dialog.add(text_item)
            close_x = 356
            close_y = 218
            sound = self.no_clue_sound
            image = assets.load_image('btn_testigo_x_normal.png')
            rollover_image = assets.load_image('btn_testigo_x_rollover.png')
            close_button = ItemImage(close_x, close_y, image, None, True)
            close_button.set_rollover_image(rollover_image, self.stage.rollover_sound)
            close_button.add_event_handler(ItemEvent.CLICK, self.item_dialog_close_click)
            dialog.add(close_button)
            self.item_dialog = dialog
            self.stage.prepare_dialog(dialog)
            self.stage.show_dialog(dialog, self.item_dialog_handle_event)
        if from_stage:
            self.stage.render()
            sound.play()
        return

    def item_dialog_handle_event(self, e):
        if e.type == KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                self.stage.render()
                self.stage.click_sound.play()
                self.close_item_dialog()
                return True
        return

    def found_item(self, item, show_animation=True):
        if show_animation:
            animations.fade_out_item(item.small_item, True)
            animations.fade_out_item(item, True)
            self.stage.fade_sound.play()
        else:
            item.small_item.get_layer().remove(item.small_item)
            item.get_layer().remove(item)
        self.add_item_found(item, show_animation)
        self.clues_count += 1
        if self.clues_count == 3:
            cp = self.stage.game.datastore.user_character_progress
            if not cp.phase2_help:
                self.stage.show_help_dialog(102, 1000, self.drop_magnifier)
                cp.phase2_help = True
        return

    def item_dialog_close_click(self, item=None, args=None):
        self.close_item_dialog()
        return

    def close_item_dialog(self):
        self.stage.close_dialog(self.item_dialog)
        self.item_dialog = None
        if self.items_layer_selected_item.is_clue:
            if self.items_layer_selected_item.get_layer() != None:
                self.found_item(self.items_layer_selected_item)
        self.stage.reset_dialog()
        return

    def add_item_found(self, items_layer_selected_item, show_animation):
        item = self.stage.add_item_found(items_layer_selected_item, show_animation)
        if show_animation:
            animations.fade_in_item(item, 500, self.check_map_help_shown)
        return

    def check_map_help_shown(self, item):
        if len(self.stage.items_found) == 1:
            self.stage.start_map_help_animation()
        return

    def item_found_click(self, item, args):
        self.show_item_found_message(item.stage_item, False)
        return

    def draw_magnifier(self, item, target):
        self.large_stage.render()
        x = item.get_left()
        y = item.get_top()
        (back_x, back_y) = self.get_amplified_pos(x, y)
        delta_x = 35
        delta_y = 21
        target.blit_stage(self.large_stage, (x + delta_x, y + delta_y), Rect(back_x + delta_x, back_y + delta_y, 76, 18))
        delta_x = 23
        delta_y = 39
        target.blit_stage(self.large_stage, (x + delta_x, y + delta_y), Rect(back_x + delta_x, back_y + delta_y, 101, 72))
        delta_x = 33
        delta_y = 111
        target.blit_stage(self.large_stage, (x + delta_x, y + delta_y), Rect(back_x + delta_x, back_y + delta_y, 74, 9))
        target.blit_image(self.magnifier_image, (x, y))
        return

    def get_amplified_pos(self, x, y):
        left = self.magnifier.get_left()
        top = self.magnifier.get_top()
        return (left * 2 + 73 + (x - left), top * 2 + 73 + (y - top))

    def build_stage(self):
        case = self.game.datastore.user_character_progress.case
        set_number = case.thief_lair_set[0]
        layout = case.thief_lair_set[1]
        old_magnifier_visible = self.magnifier.get_visible()
        self.magnifier.set_visible(False)
        stage_built = False
        build_stage_attempt = 0
        while not stage_built:
            self.small_back_layer.empty()
            self.small_items_layer.empty()
            self.large_back_layer.empty()
            self.large_items_layer.empty()
            self.load_level_in_stages('l%03da' % set_number[0], True)
            self.load_level_in_stages('l%03db' % set_number[1], False)
            empty_place_holders = []
            self.stage.load_place_holders(self.small_back_layer, empty_place_holders)
            if len(empty_place_holders) > 0:
                raise Exception('Place holder in the back items are not supported')
            self.stage.load_place_holders(self.small_items_layer, empty_place_holders)
            (clue_place_holders, item_place_holders) = self.analyze_place_holders(empty_place_holders)
            if layout != None:
                if self.load_layout(layout, clue_place_holders, item_place_holders):
                    stage_built = True
                else:
                    print('Invalid layout. Generating a new one')
                    layout = None
            else:
                layout = []
                if self.add_clues_and_extra_items(clue_place_holders, item_place_holders, build_stage_attempt, layout):
                    stage_built = True
                else:
                    build_stage_attempt += 1
                    layout = None

        case.thief_lair_set[1] = layout
        self.magnifier.set_visible(old_magnifier_visible)
        return

    def load_layout(self, layout, clue_place_holders, item_place_holders):
        case = self.game.datastore.user_character_progress.case
        clues = case.list_stage_clues
        for item in layout:
            item_type = item[0]
            place_holder_index = item[1]
            category = item[2]
            if category == 1:
                if place_holder_index >= len(clue_place_holders):
                    return False
                place_holder = clue_place_holders[place_holder_index]
                is_clue = True
            elif category == 2:
                if place_holder_index >= len(clue_place_holders):
                    return False
                place_holder = clue_place_holders[place_holder_index]
                is_clue = False
            elif category == 3:
                if place_holder_index >= len(item_place_holders):
                    return False
                place_holder = item_place_holders[place_holder_index]
                is_clue = False
            else:
                return False
            if item_type not in place_holder.items:
                return False
            if not self.add_item(item_type, place_holder, is_clue, clues, None):
                return False

        return True

    def disable_magnifier(self):
        self.magnifier.set_visible(False)
        return

    def add_clues_and_extra_items(self, clue_place_holders, item_place_holders, build_stage_attempt, layout):
        character_progress = self.stage.game.datastore.user_character_progress
        level = character_progress.range.level
        if level == 0:
            fake_clues = 2
            extra_items = 3
            below_prob = 0
            inside_clue_prob = 0
            inside_item_prob = 0.3
        elif level == 1:
            fake_clues = 3
            extra_items = 3
            below_prob = 0.1
            inside_clue_prob = 0.1
            inside_item_prob = 0.3
        elif level == 2:
            fake_clues = 3
            extra_items = 4
            below_prob = 0.2
            inside_clue_prob = 0.2
            inside_item_prob = 0.3
        elif level == 3:
            fake_clues = 4
            extra_items = 4
            below_prob = 0.3
            inside_clue_prob = 0.3
            inside_item_prob = 0.3
        elif level == 4:
            fake_clues = 4
            extra_items = 5
            below_prob = 0.4
            inside_clue_prob = 0.4
            inside_item_prob = 0.4
        else:
            fake_clues = 5
            extra_items = 5
            below_prob = 0.5
            inside_clue_prob = 0.5
            inside_item_prob = 0.4
        added_items = {}
        if not self.add_clues(clue_place_holders, fake_clues, below_prob, inside_clue_prob, build_stage_attempt, added_items, layout):
            return False
        self.add_extra_items(item_place_holders, extra_items, below_prob, inside_item_prob, added_items, layout)
        return True

    def add_clues(self, place_holders, fake_clues, below_prob, inside_prob, build_stage_attempt, added_items, layout):
        case = self.game.datastore.user_character_progress.case
        clues_left = [case.list_stage_clues[0].clue.id, case.list_stage_clues[1].clue.id, case.list_stage_clues[2].clue.id]
        clues = case.list_stage_clues
        used_place_holders = []
        (normal_place_holders, below_place_holders, inside_place_holders) = self.split_place_holders(place_holders)
        while len(clues_left) > 0 and len(normal_place_holders) > 0:
            place_holder = self.extract_random_place_holder(normal_place_holders, below_place_holders, below_prob, inside_place_holders, inside_prob)
            if self.valid_place_holder(place_holder):
                possible_items = place_holder.items[:]
                while len(possible_items) > 0:
                    possible_item = random.choice(possible_items)
                    if possible_item in clues_left:
                        if self.add_item(possible_item, place_holder, True, clues, layout):
                            clues_left.remove(possible_item)
                            added_items[possible_item] = place_holder
                            used_place_holders.append(place_holder)
                            break
                    possible_items.remove(possible_item)

        if len(clues_left) > 0 and build_stage_attempt < 3:
            print(('Some of the clues ' + str(clues_left) + " couldn't be located, building the stage again (attempt " + str(build_stage_attempt) + ')'))
            return False
        (normal_place_holders, below_place_holders, inside_place_holders) = self.split_place_holders(place_holders, used_place_holders)
        while len(normal_place_holders) > 0 and fake_clues > 0:
            place_holder = self.extract_random_place_holder(normal_place_holders, below_place_holders, below_prob, inside_place_holders, inside_prob)
            if self.valid_place_holder(place_holder):
                possible_items = place_holder.items[:]
                while len(possible_items) > 0:
                    possible_item = random.choice(possible_items)
                    if possible_item not in added_items:
                        if self.add_item(possible_item, place_holder, False, None, layout):
                            added_items[possible_item] = place_holder
                            fake_clues -= 1
                            break
                    possible_items.remove(possible_item)

        return True

    def add_extra_items(self, place_holders, extra_items, below_prob, inside_prob, added_items, layout):
        (normal_place_holders, below_place_holders, inside_place_holders) = self.split_place_holders(place_holders)
        while extra_items > 0 and len(normal_place_holders) > 0:
            place_holder = self.extract_random_place_holder(normal_place_holders, below_place_holders, below_prob, inside_place_holders, inside_prob)
            if self.valid_place_holder(place_holder):
                possible_items = place_holder.items[:]
                while len(possible_items) > 0:
                    possible_item = random.choice(possible_items)
                    if possible_item not in added_items:
                        if self.add_item(possible_item, place_holder, False, None, layout):
                            added_items[possible_item] = place_holder
                            extra_items -= 1
                            break
                    possible_items.remove(possible_item)

        return

    def valid_place_holder(self, place_holder):
        if place_holder.outside:
            stage_item = place_holder.stage_item
            if hasattr(stage_item, 'place_holders_used'):
                for place_holder_used in stage_item.place_holders_used:
                    if place_holder_used.inside:
                        return False

        elif place_holder.inside:
            stage_item = place_holder.stage_item
            if hasattr(stage_item, 'place_holders_used'):
                for place_holder_used in stage_item.place_holders_used:
                    if place_holder_used.outside:
                        return False

        return True

    def split_place_holders(self, place_holders, exclude_place_holders=[]):
        normal = []
        below = []
        inside = []
        for place_holder in place_holders:
            if place_holder not in exclude_place_holders:
                if place_holder.inside:
                    inside.append(place_holder)
                elif place_holder.below:
                    below.append(place_holder)
                else:
                    normal.append(place_holder)

        return (
         normal, below, inside)

    def extract_random_place_holder(self, normal_place_holders, below_place_holders, below_prob, inside_place_holders, inside_prob):
        if len(inside_place_holders) == 0:
            inside = False
        else:
            rand_value = random.random()
            inside = rand_value < inside_prob
        if inside:
            place_holder = random.choice(inside_place_holders)
            inside_place_holders.remove(place_holder)
        else:
            if len(below_place_holders) == 0:
                below = False
            else:
                rand_value = random.random()
                below = rand_value < below_prob
            if below:
                place_holder = random.choice(below_place_holders)
                below_place_holders.remove(place_holder)
            else:
                place_holder = random.choice(normal_place_holders)
                normal_place_holders.remove(place_holder)
        return place_holder

    def add_item(self, item_type, place_holder, is_clue, clues, layout):
        add_index = self.get_place_holder_add_index(place_holder)
        valid = self.validate_place_holder(place_holder, False, add_index)
        if not valid:
            return False
        if is_clue:
            stage_clue = self.stage.find_clue(clues, item_type)
        else:
            stage_clue = None
        if place_holder.inside:
            only_visible_in_states = [
             ItemState.OPENED]
        else:
            only_visible_in_states = None
        small_item = ItemCell(self.stage, item_type, ItemState.NORMAL)
        small_item.is_clue = is_clue
        small_item.place_holder = place_holder
        if stage_clue != None:
            small_item.stage_clue = stage_clue
        small_item.set_to_place_holder(place_holder.stage_item, place_holder.place_holder, place_holder.below, only_visible_in_states)
        self.small_items_layer.add(small_item, add_index)
        large_item = small_item.clone(self.large_stage)
        large_item.is_clue = is_clue
        large_item.small_item = small_item
        if stage_clue != None:
            large_item.stage_clue = stage_clue
        self.large_items_layer.add(large_item, add_index)
        place_holder.stage_item.large_item.register_placeholder_item(large_item)
        if layout != None:
            if place_holder.clue:
                if is_clue:
                    category = 1
                else:
                    category = 2
            else:
                category = 3
            layout.append((item_type, place_holder.list_index, category))
        stage_item = place_holder.stage_item
        if not hasattr(stage_item, 'place_holders_used'):
            stage_item.place_holders_used = [
             place_holder]
        else:
            stage_item.place_holders_used.append(place_holder)
        return True

    def analyze_place_holders(self, empty_place_holders):
        clue_place_holders = []
        item_place_holders = []
        for (stage_item, place_holder, index) in empty_place_holders:
            info = self.get_place_holder_info(place_holder.tag, stage_item, place_holder, index)
            if info.clue:
                info.list_index = len(clue_place_holders)
                clue_place_holders.append(info)
            else:
                info.list_index = len(item_place_holders)
                item_place_holders.append(info)

        return (
         clue_place_holders, item_place_holders)

    def get_place_holder_add_index(self, place_holder):
        stage_item = place_holder.stage_item
        index = self.small_items_layer.items.index(stage_item)
        if place_holder.below:
            while index > 0:
                previous_item = self.small_items_layer.items[index - 1]
                if not hasattr(previous_item, 'place_holder') or previous_item.place_holder.stage_item != place_holder.stage_item or previous_item.place_holder.index <= place_holder.index:
                    break
                index -= 1

        else:
            index += 1
            while index < len(self.small_items_layer.items):
                next_item = self.small_items_layer.items[index]
                if not hasattr(next_item, 'place_holder') or next_item.place_holder.stage_item != place_holder.stage_item or next_item.place_holder.index > place_holder.index:
                    break
                index += 1

        return index

    def build_tags_dictionary(self):
        self.place_holder_tags = {}
        for tag in PLACE_HOLDER_TAGS:
            self.place_holder_tags[tag[0]] = tag

        return

    def get_place_holder_info(self, id, stage_item, place_holder, place_holder_index):
        below = False
        inside = False
        outside = False
        clue = False
        tag = self.place_holder_tags.get(id)
        if tag == None:
            items = None
        else:
            items = tag[1]
            type = tag[2]
            if type == PlaceHolderType.NORMALCLUE:
                clue = True
            elif type == PlaceHolderType.NORMALITEM:
                pass
            if type == PlaceHolderType.OUTSIDECLUE:
                clue = True
                outside = True
            elif type == PlaceHolderType.OUTSIDEITEM:
                outside = True
            elif type == PlaceHolderType.BELOWCLUE:
                clue = True
                below = True
            elif type == PlaceHolderType.BELOWITEM:
                below = True
            elif type == PlaceHolderType.INSIDECLUE:
                clue = True
                inside = True
            elif type == PlaceHolderType.INSIDEITEM:
                inside = True
        return PlaceHolderInfo(below, inside, outside, clue, stage_item, place_holder, place_holder_index, items)

    def validate_place_holder(self, place_holder, check_covered, add_index):
        stage_item = place_holder.stage_item
        place_holder_def = place_holder.place_holder
        (x, y) = stage_item.get_place_holder_xy(place_holder_def)
        if not check_covered and not place_holder.below:
            is_over = self.is_over_item(stage_item, place_holder_def, place_holder.below, add_index, x, y)
            if is_over == 0:
                return True
            else:
                return False
        else:
            is_over = self.is_over_item(stage_item, place_holder_def, place_holder.below, add_index, x, y)
            if is_over != 0:
                return False
            is_over = self.is_over_item(stage_item, place_holder_def, place_holder.below, add_index, x - 4, y - 4)
            if is_over != 0:
                return False
            is_over = self.is_over_item(stage_item, place_holder_def, place_holder.below, add_index, x + 4, y + 4)
            if is_over != 0:
                return False
            return True
        return

    def is_over_item(self, stage_item, place_holder_def, below, add_index, x, y):
        if place_holder_def.tag.startswith('Inside'):
            item = self.stage.hit_test(x, y)
            if stage_item != item:
                return 1
            elif hasattr(stage_item, 'placeholder_items'):
                items = stage_item.placeholder_items
                for item in items:
                    if hasattr(item, 'place_holder'):
                        item_place_holder = item.place_holder.place_holder
                        if item_place_holder.tag.startswith('Inside') and abs(place_holder_def.x - item_place_holder.x) < 8 and abs(place_holder_def.y - item_place_holder.y) < 8:
                            return 1

            return 0
        else:
            item = self.stage.hit_test(x, y)
            if item != None:
                if stage_item == item:
                    hit_test_stack = self.stage.hit_test_stack(x, y)
                    for item in hit_test_stack:
                        if item != stage_item and item.get_layer() == self.small_items_layer and isinstance(item, ItemCell) and item.get_definition().tag != ItemTag.FLOOR and item.get_definition().tag != ItemTag.WALL:
                            if below:
                                return 1
                            if not hasattr(item, 'place_holder') or item.place_holder.stage_item != stage_item:
                                return 1

                    return 0
                else:
                    if item.get_layer() == self.small_items_layer:
                        if below:
                            return 1
                        if hasattr(item, 'place_holder'):
                            item_place_holder = item.place_holder.place_holder
                            if abs(place_holder_def.x - item_place_holder.x) < 8 and abs(place_holder_def.y - item_place_holder.y) < 8 and item.place_holder.stage_item == stage_item:
                                return 1
                        if hasattr(item, 'is_clue') and item.is_clue:
                            return 1
                        if self.small_items_layer.index_of(item) < add_index:
                            return 0
                    else:
                        cells = GRID_SIZE[0] + GRID_SIZE[1]
                        width = _div(GRID_CELL_WIDTH , 2) * cells
                        height = _div(GRID_CELL_HEIGHT , 2) * cells
                        margin = 5
                        y0 = GRID_ORIGIN[1] + height - _div(abs(x - GRID_ORIGIN[0]) * height , width)
                        if x < GRID_ORIGIN[0] - _div(width , 2) + margin or x > GRID_ORIGIN[0] + _div(width , 2) - margin or y > y0 - margin:
                            return 2
                        return 0
                    if isinstance(item, ItemCell):
                        if item.get_definition().tag != ItemTag.FLOOR and (not hasattr(item, 'place_holder') or item.place_holder.stage_item != stage_item):
                            return 1
                        if hasattr(item, 'is_clue'):
                            return 1
        return 2

    def load_level_in_stages(self, level_name, background):
        if os.path.isfile(os.path.join('data', self.stage.get_set_name() + level_name + '.tcl')):
            if background:
                small_layer = self.small_back_layer
                large_layer = self.large_back_layer
            else:
                small_layer = self.small_items_layer
                large_layer = self.large_items_layer
            small_items = self.stage.load_level(level_name, small_layer, ITEM_STATES)
            large_items = self.large_stage.load_level(level_name, large_layer, ITEM_STATES)
            for i in range(len(small_items)):
                large_items[i].small_item = small_items[i]
                small_items[i].large_item = large_items[i]

        return

    def large_stage_changed(self, stage):
        self.magnifier.set_dirty()
        return

    def update_case_last_department_lair(self):
        case = self.game.datastore.user_character_progress.case
        if case.last_department_lair == case.list_departments[0] and case.last_department_visited == case.list_departments[0]:
            self.game.datastore.user_character_progress.case.last_department_lair = case.list_departments[1]
        return


class PlaceHolderInfo():

    def __init__(self, below, inside, outside, clue, stage_item, place_holder, index, items):
        self.below = below
        self.inside = inside
        self.outside = outside
        self.clue = clue
        self.stage_item = stage_item
        self.place_holder = place_holder
        self.index = index
        self.items = items
        return


