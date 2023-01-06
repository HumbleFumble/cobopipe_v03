How to create a p12 certificate:
SHELL COMMAND: <path to ZXPSignCmd.exe> -selfSignedCert <country abbreviation (US, CA, DK, RU)> <state> <organization> "<name of signiture>" <password> <name of p12 certificate file>
SHELL COMMAND EXAMPLE: P:\tools\_Scripts\Production_scripts\_base_production\PremierePro\extensions\_dist\ZXPSignCmd.exe -selfSignedCert DK Copenhagen CopenhagenBombay "Mads Hangaard" pandaParty70 coboCert.p12

How to create a .zxp package:
SHELL COMMAND: <path to ZXPSignCmd.exe> <path to extension> <path to p12 certificate> <p12 certificate password> -tsa <timestamp provider, recommended: http://timestamp.digicert.com/>
SHELL COMMAND EXAMPLE: P:\tools\_Scripts\Production_scripts\_base_production\PremierePro\extensions\_dist\ZXPSignCmd.exe -sign P:\tools\_Scripts\Production_scripts\_base_production\PremierePro\extensions\_dist\GatherHookup P:\tools\_Scripts\Production_scripts\_base_production\PremierePro\extensions\_dist\gatherHookup.zxp P:\tools\_Scripts\Production_scripts\_base_production\PremierePro\extensions\_dist\coboCert.p12 pandaParty70 -tsa http://timestamp.digicert.com/