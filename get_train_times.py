#!/bin/python

from prettytable import PrettyTable
from bs4 import BeautifulSoup
import requests
import os
import sys
import time



class TranslinkTimetable:
	def __init__(self, departure, destination):
		self.departure = departure
		self.destination = destination
		self.station_code = ""
		self.url = "https://apis.opendatani.gov.uk/translink/"
		self.headers = {
			"Content-Type": 'text/css; charset=utf-8',
			"Accept": 'text/css,json,*/*;q=0.1',
			"User-Agent":'''Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chromium/78.0.3904.97 Chrome/78.0.3904.97 Safari/537.36'''
		}
		
		
	def get_station_codes(self):
		print("API call at: %s"%(time.asctime()))
		print("Retrieving station codes...")
		try:
			response = requests.get(
				url = self.url,
				headers = self.headers
			)
			if response.status_code == 200:
				print("Response OK: %d"%(response.status_code))
				self.station_codes = response.json()
		except Exception as ex:
			print("Something else has gone wrong : %s"%(ex.__str__()))
			sys.exit()
	
	
	def get_departure_station_code(self):
		try:
			for station in self.station_codes['stations']:
				if station['name'] == self.departure:
					self.station_code = str(station['code'])
					break
			if self.station_code:
				print("Retrieved station code: %s"%(self.station_code))
			else:
				print("Station not listed. Exiting...")
				sys.exit()
		except Exception as ex:
			print("Something else has gone wrong : %s"%(ex.__str__()))
			sys.exit()
							
		
	def download_xml_translink_times(self):
		print("Retrieving translink timetables for %s to %s"%(
			self.departure, self.destination
		))
		try:
			response = requests.get(
				url = self.url + self.station_code + ".xml",
				headers = self.headers
			)
			self.translink_times_xml = response.text
		except Exception as ex:
			print("Something else has gone wrong : %s"%(ex.__str__()))
			print("Trying wget...")
			##try wget request instead
			os.system("wget -O translink.text %d".format(
				self.url + self.station_code + ".xml"
			))
			with open("translink.text", "r") as TRANSLINK_FILE:
				self.translink_times_xml = TRANSLINK_FILE.read() 
						
						
	def parse_translink_times_xml(self):
		self.soup = BeautifulSoup(
			markup = self.translink_times_xml,
			features = 'html.parser'
		)
			
							
	def get_station_board(self):
		try:
			self.stationboard = self.soup.find("stationboard")
		except Exception as ex:
			print("Something else has gone wrong : %s"%(ex.__str__()))
	
		
	
	def get_departure_name(self):
		try:
			self.name = self.stationboard.get("name")
			print("\nDeparting:", self.name)
		except Exception as ex:
			print("Something else has gone wrong : %s"%(ex.__str__()))
	
		
	
	def get_timestamp(self):
		try:
			self.timestamp = self.stationboard.get("timestamp")
			print("Current date & time:", self.timestamp)
		except Exception as ex:
			print("Something else has gone wrong : %s"%(ex.__str__()))
	
		
	
	def get_services(self):
		try:
			self.services = self.stationboard.find_all("service")
		except Exception as ex:
			print("Something else has gone wrong : %s"%(ex.__str__()))
	
	
	def get_service_type(self):
		self.service_type = self.service.find('servicetype').get("type")
		
	
	def get_arrival_time(self):
		try:
			self.arrival_time = self.service.find("arrivetime")
			self.arrive_time = self.arrival_time.get("time")
			self.arrival_status = self.arrival_time.get("arrived")
			print("Arrival Time:", self.arrive_time)
			print("Arrived:", self.arrival_status)
		except Exception as ex:
			print("Something else has gone wrong : %s"%(ex.__str__()))
	
		
	
	def get_departure_time(self):
		try:
			self.departure_time = self.service.find("departtime").get("time")
			print("Departure Time:", self.departure_time)
		except Exception as ex:
			print("Something else has gone wrong : %s"%(ex.__str__()))
	
		
	def get_platform(self):
		try:
			self.platform = self.service.find("platform")
			self.platform_number = self.platform.get("number")
			self.platform_status = self.platform.get("changed")
			print("Platform No:", self.platform_number)
			print("Platform Changed:", self.platform_status)
		except Exception as ex:
			print("Something else has gone wrong : %s"%(ex.__str__()))
		
		
	def get_status(self):
		try:
			self.status = self.service.find("servicestatus").get("status")
			print("Status:", self.status)
		except Exception as ex:
			print("Something else has gone wrong : %s"%(ex.__str__()))
	
			
	def get_delay(self):
		try:
			self.delay = self.service.find("delay").get("minutes")
			if not self.delay:
				print("Delay Time: No Delays")
			else:
				print("Delay Time:", self.delay,"minutes")
		except Exception as ex:
			print("Something else has gone wrong : %s"%(ex.__str__()))
	
		
	def get_delay_cause(self):
		try:
			self.delay_cause = self.service.find("delaycause").text
			if self.delay_cause:
				print("Delay Cause:", self.delay_cause)
		except Exception as ex:
			print("Something else has gone wrong : %s"%(ex.__str__()))
	
			
	def get_last_report(self):
		try:
			self.last_report = self.service.find("lastreport")
			self.report_time = self.last_report.get("time")
			self.last_station_reported = self.last_report.get("station1")
			if not self.last_station_reported:
				print("No report")
			else:
				print("Last Report: at %s (%s)"%(
					self.last_station_reported, self.report_time
				)) 
		except Exception as ex:
			print("Something else has gone wrong : %s"%(ex.__str__()))
	

	def get_termination_point(self):
		try:
			self.destination_element = self.service.find("destination1")
			self.termination_point = self.destination_element.get("name")
			self.destination_arrival_time = self.destination_element.get("ttarr")
		except Exception as ex:
			print("Something else has gone wrong : %s"%(ex.__str__()))
			
		
	def get_calling_points(self):
		self.calling_points = self.service.find_all("callingpoint")
	
	
	def build_table_of_results(self):
		self.results_table = PrettyTable()
		self.results_table.add_column("Station", self.station_names)
		self.results_table.add_column("TTA", self.arrival_times)
		self.results_table.add_column("TTD", self.departure_times)
		self.results_table.add_column("ETA", self.ETAs)
		self.results_table.add_column("ETD", self.ETDs)	

		
	def get_top_level_results(self):
		print("\n")
		self.get_arrival_time()
		self.get_departure_time()
		self.get_platform()
		self.get_status()
		self.get_delay()
		self.get_delay_cause()
		self.get_last_report()
		print("Terminating at: %s (%s)"%(
			self.termination_point, self.destination_arrival_time
		))
		
		
	def get_service_details(self):		
		try:
			self.get_calling_points()
		except Exception as ex:
			print("Something else has gone wrong : %s"%(ex.__str__()))
		
		self.station_names = list()
		self.arrival_times = list()
		self.departure_times = list()
		self.ETAs = list()
		self.ETDs = list()
		for calling_point in self.calling_points:
			self.station_names.append(calling_point.get("name"))
			self.arrival_times.append(calling_point.get("ttarr"))
			self.departure_times.append(calling_point.get("ttdep"))
			self.ETAs.append(calling_point.get("etarr"))
			self.ETDs.append(calling_point.get("etdep"))
		
		
		if self.destination.title() in self.station_names:
			self.get_top_level_results()
			self.build_table_of_results()
			print(self.results_table)
		elif self.termination_point.lower() == self.destination.lower():
			self.get_top_level_results()
			self.build_table_of_results()
			print(self.results_table)
		else:
			pass
		         
	
	def print_results(self):
		for service in self.services:
			self.service = service
			self.get_service_type()
			if self.service_type == "Terminating":
				continue
			else:
				try:
					self.get_termination_point()
					self.get_service_details()
				except Exception as ex:
					print("Something else has gone wrong : %s"%(ex.__str__()))
			
				
	def get_special_notice(self):
		self.specialnotice_element = self.soup.find('specialnotice')
		if self.specialnotice_element:
			self.specialnotice_text = self.specialnotice_element.text.strip()
			for line in self.specialnotice_text.split('\n'):
				print(line.strip())



if __name__ == '__main__':
   ##get the departure and destination station
   departure_station = input("departure station: ").strip().title()
   requested_destination = input("destination station: ").strip().title()

   translink_timetable_obj = TranslinkTimetable(
   	departure = departure_station,
   	destination = requested_destination
   )
   
   ##api requests and parsing
   translink_timetable_obj.get_station_codes()
   translink_timetable_obj.get_departure_station_code()
   translink_timetable_obj.download_xml_translink_times()
   translink_timetable_obj.parse_translink_times_xml()
   
   ##top level: stationboard results
   translink_timetable_obj.get_station_board()
   translink_timetable_obj.get_departure_name()
   translink_timetable_obj.get_timestamp()
   
   ##get each service
   translink_timetable_obj.get_services()
   if translink_timetable_obj.services:
      translink_timetable_obj.print_results()
   else:
      print('\n\n\t\t\tSpecial Notice!!')
      translink_timetable_obj.get_special_notice()

   
