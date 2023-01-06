from getConfig import getConfigClass
CC = getConfigClass()
from Maya_Functions.file_util_functions import loadJson, saveJson

target = 'OID'
filePath = CC.get_cryptomatte_list()
add_dict = {
    'Mia': 1,
    'Tilde': 2,
    'Oskar': 3,
    'Leafling': 4,
    'SmallDragon': 5,
    'FlipRockA': 21,
    'IceCreamBear': 6,
    'RainbowGuy': 7,
    'BeeBob': 8,
    'CoconutGirl': 9,
    'WatermelonCat': 10,
    'GumGirl': 11,
    'ToothFurry': 12,
    'HugeToothFurry': 13,
    'DandelionBirds': 14,
    'RoboCarrot': 15,
    'AsteroidBunny': 35,
    'AsteroidBunnyB': 35,
    'AsteroidBunnyC': 35,
    'MamaDandelionBird': 43,
    'RocketCat': 32,
    'MushiSnail': 29,
    'Snail': 28,
    'OctoBubbles': 17,
    'SeaweedLeafthing': 33,
    'SeaHorse': 18,
    'CactusFish': 19,
    'FlowerFish': 23,
    'SoccerSaurus': 30,
    'ChestnutAntA': 45,
    'ChestnutAntC': 46,
    'Buckie': 48,
    'BuckieWithoutHisBucket': 48,
    'Smarty': 20,
    'PuppyShoe': 34,
    'Monstertruck': 47,
    'CloudEvg': 44,
    'Bubble': 99,
    'MushroomA': 94,
    'MushroomB': 95,
    'MushroomC': 96,
    'MilkyWay': 93,
    'AstroBunniesFence': 99,
    'MushroomE': 94,
    'MushroomF': 94,
    'MushroomG': 94,
    'MushroomH': 94,
    'SmartyLightbulb': 47,
    'MicrophoneRainbow': 100,
    'MicrophoneRainbow': 100,
    'SmallSpinningPlanet': 101,
    'HoolaHooop': 102,
    'SmallPlanetA': 103,
    'SmallPlanetB': 104,
    'SmallPlanetC': 105,
    'SmallPlanetD': 106,
    'SmallPlanetE': 107,
    'SambaStar': 108,
    'Jellycano': 109,
    'JellyChunk': 110,
    'JellyClump': 111,
    'JellyFlow': 112,
    'JellygFGA': 113,
    'JellyLump': 114,
    'JellyPillow': 115,
    'JellyStageA': 116,
    'JellyStageB': 117,
    'JellyStageC': 118,
    'CloudMaker': 119,
    'CloudBeard': 120,
    'BunnyEars': 121,
    'Cloud': 122,
    'CloudBigA': 123,
    'SnowSculptureNCB': 124,
    'SnowSculptureRG': 125,
    'SnowSculptureBG': 126,
    'SnowLumps': 127,
    'SnowCircle': 128,
    'BrokenTreeTrunkSledge': 129,
    'SnowFootprints': 130,
    'SnowGlobe': 131,
    'SundaeBear': 132,
    'SparklyPants': 133,
    'PlainSwimmingShortsA': 134,
    'Calcugator': 135,
    'SwingingLilipopsA': 136,
    'BarrelA': 137,
    'CaptainsHatNiceCreamBearA': 138,
    'SuitcaseIceCreamBearA': 139,
    'BroomBuckleyA': 140,
    'WoodenBarrelA': 141,
    'TelescopeA': 142,
    'TelescopeB': 143,
    'PenA': 144,
    'CalcugatorsFootstepsA': 130,
    'RopeA': 145,
    'RopeTangledA': 146,
    'RopeLoopA': 147,
    'OskarsChecklistA': 148,
    'MoonChainlinkFence': 149,
    'MoonChainlinkFenceB': 149,
    'JunkyardRobot': 150,
    'OscarsToyRocketBrokenA': 151,
    'SpaceGlueA': 152,
    'Bucket': 131,
    'Feather': 153,
    'DJDeck': 154,
    'PillowA': 155,
    'BigPillowA': 156,
    'PinkShellA': 157,
    'JollyDuck': 158,
    'TentA': 159,
    'TentB': 160,
    'LargeSnowball': 161,
    'OpenBarrelA': 162
}

delete_list = [
]

cryptoTable = loadJson(filePath)
dict = cryptoTable[target]

for item in delete_list:
    if item in dict.keys():
        del dict[item]

for key in add_dict.keys():
    if key not in dict.keys():
        dict[key] = add_dict[key]

for key, value in add_dict.items():
    print(key + ': ' + str(value))

del cryptoTable[target]
cryptoTable[target] = dict

saveJson(filePath, cryptoTable)