import arcpy
import requests

projectPath = "C:/Users/rp376/ArcGIS-prosjekter/BysykkelLokalt"
arcpy.env.workspace = projectPath
featureClass = projectPath + "/BysykkelLokalt.gdb/Bysykkelstasjoner"
coordSys = 25832
tableLocation = "Data/BysykkelStasjoner.csv"
seperator = ";"
arcpy.AddMessage("Starting to process map data...")

allBysykkelAPIs = "https://gbfs.urbansharing.com/bergenbysykkel.no/gbfs.json"
responseAllAPIs = requests.get(allBysykkelAPIs)
apiArray = []

if responseAllAPIs.status_code == 200:
    allApisJSON = responseAllAPIs.json()
    data = allApisJSON['data']
    norwegian = data['nb']
    feeds = norwegian['feeds']

    for api in feeds:
        apiArray.append(api['url'])

systemInformation = apiArray[0]
stationInformation = apiArray[1]
stationStatus = apiArray[2]

stInfoResponse = requests.get(stationInformation)
print("Using: " + stationInformation)
stStatResponse = requests.get(stationStatus)
print("Using:" + stationStatus)
sysInfoResponse = requests.get(systemInformation)
print("Using:" + systemInformation)

if stInfoResponse.status_code == 200 and sysInfoResponse.status_code == 200:
    stInfoJson = stInfoResponse.json()
    infoData = stInfoJson['data']
    stations = infoData['stations']

    stStatsJson = stStatResponse.json()
    statusData = stStatsJson['data']
    stStatuses = statusData['stations']

    with open(tableLocation, 'w+') as file:
        file.write("Station ID" + seperator + "Navn" + seperator + "Adresse" + seperator + "Latitude" + seperator +
                   "Longitude" + seperator + "Plasser" + seperator + "Har ledige sykler" + seperator)

    # TODO Kombinere statusene til stasjonene for å gi data på hvor mange sykler som er ledig f.eks.
    # TODO Finn  en måte å bruke ID på for å kombinere dataene
    # for stationStatus in stStatuses:

    for station in stations:
        with open(tableLocation, 'a+') as file:
            file.write("\n" + station['station_id'] + seperator + station['name'] + seperator + station['address'] +
                       seperator + str(station['lat']) + seperator + str(station['lon']) + seperator +
                       str(station['capacity']) + seperator)

    arcpy.XYTableToPoint_management(tableLocation, featureClass, 'Longitude', 'Latitude')
    arcpy.AddMessage("Processing finished. Bysykkelstasjoner is complete.")

else:
    arcpy.AddMessage("There was en error connecting to the API.\nErrocode as follows: " +
                     str(stInfoResponse.status_code))
