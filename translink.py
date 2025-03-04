import requests
import sys
import json
import os
import datetime
from bs4 import BeautifulSoup

RED   = "\033[1;31m"
BLUE  = "\033[1;34m"
CYAN  = "\033[1;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD    = "\033[;1m"
REVERSE = "\033[;7m"

def get_station_code(location):
	headers = {"User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0"}
	url = "https://www.translink.co.uk/locationApi/find?SearchString="
	response = requests.get(url=url+location,headers=headers)
	json_response = response.json()
	locations = json_response['Locations']
	for location in locations:
		location_type = location["LocationType"].strip()
		if location_type == "Train stop":
			return location["Id"].strip()


def curl_request_results():
	results = os.popen("""curl 'https://www.translink.co.uk/JourneyPlannerApi/GetJourneyResults' -X POST -H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0' -H 'Content-Type: application/json' --data-raw '{"OriginId":"10000038","DestinationId":"10000055","DepartureOrArrivalDate":"2024-11-11T23:55:00","isSearchByDepartureDate":false,"FindBusDepartures":false,"FindTrainDepartures":true,"HasStepFreeEnabled":false}' """).read()
	return json.loads(results)


def get_train_info(departure_id,destination_id):
	url = "https://www.translink.co.uk/JourneyPlannerApi/GetJourneyResults"
	data = "{\"OriginId\":\""+departure_id.strip()+"\",\"DestinationId\":\""+destination_id.strip()+"\",\"DepartureOrArrivalDate\":\""+datetime.datetime.today().strftime("%Y-%m-%dT%H:%M:%S")+"\",\"isSearchByDepartureDate\":true,\"FindBusDepartures\":false,\"FindTrainDepartures\":true,\"HasStepFreeEnabled\":false}"
	headers = {
		"User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0",
		"Content-Type": "application/json"
	}
	response = requests.post(url=url,data=data,headers=headers)
	results = response.json()
	return results['Result']['TripResults']


def get_results(results):
	for trip_details in results:
		print("----------------------------------------------")
		get_depart_platform(trip_details['Legs'][0])
		get_depart_time(trip_details['Legs'][0])
		get_arrive_time(trip_details['Legs'][0])
		get_stops(trip_details['Legs'][0])
		get_alerts(trip_details['Legs'][0])


def get_depart_platform(trip_details):
	print(RED + "Platform:", f"{trip_details['DepartureLocation']['PlatformName']:>15}", sep='\t')


def get_depart_time(trip_details):
	print(GREEN + "Departure time:",f"{trip_details['ActualDepartureTime']:>10}", sep='\t')


def get_arrive_time(trip_details):
        print(BLUE + "Arrival Time:", f"{trip_details['ActualArrivalTime']:>10}", sep='\t')


def get_stops(trip_details):
	stops = trip_details['Stops']
	for stop in stops:
		print(RESET + f"{stop['Name'].replace('Train Station',''):<10}", f"{stop['PlannedDepartureTime']:>10}", sep='\t')


def get_alerts(trip_details):
	alerts = trip_details['Alerts']
	for alert in alerts:
		try:
			soup = BeautifulSoup(alert['Content'], features='html.parser')
			print(BOLD+"Alert: "+BOLD+RED+f"{soup.text}"+RESET)
		except Exception as ex:
			print(str(ex))

if __name__=="__main__":
	departure = sys.argv[1].strip()
	destination = sys.argv[2].strip()

	departure_id = get_station_code(departure)
	destination_id = get_station_code(destination)

	print(f"\t\tTRANSLINK - {departure}: {departure_id} to {destination}: {destination_id}")

	results = get_train_info(departure_id,destination_id)
	get_results(results)
