import os
import re
import time
import datetime

class DateCheck(object):
	def __init__(self):
		self.inactive_days = 365 

	def date_compare(self, proc_stdout):
		"""Takes the output from 'finger user' as a string. Processes regcheck() and date_convert(). Returns True if user hasn't logged in for self.inactive_days. Otherwise returns False if the user is logged in or has logged in in under self.inactive_days."""
		regexp = self.regcheck(proc_stdout)
		if not regexp:
			return False #User isn't above date threshold because they're currently online.
		else:
			user_datetime = self.date_convert()
			current_datetime = datetime.datetime.now()
			if (current_datetime - user_datetime).days > self.inactive_days:
				return True #User has been inactive longer than allowed.
			else:
				return False #User has been active

	def regcheck(self, string):
		"""Processes the regexp and stores the results in the tuple self.last_on and returns True. If the user is currently online, return False."""
		last_on_reg = "Last login (Sun|Mon|Tue|Wed|Thu|Fri|Sat) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \s{0,1}(\d{1,2}) (\d{1,2}):(\d{1,2}) (\d{1,4}){0,1}.+"
	 	self.last_on = re.compile(last_on_reg).findall(string)
		if not self.last_on:
			return False 
		else:
			self.last_on = self.last_on[0]
			return True 

	def date_convert(self):
		"""Converts the output of the user's last login and returns a datetime object for date_compare() to check."""
		if not self.last_on[5]:
			time_str = "%s %s %s %s %s" % (self.last_on[1], self.last_on[2], time.localtime()[0], self.last_on[3], self.last_on[4]) #Month day year hour minute
		else:
			time_str = "%s %s %s %s %s" % (self.last_on[1], self.last_on[2], self.last_on[5], self.last_on[3], self.last_on[4]) #Month day year hour minute
		user_time = time.strptime(time_str, "%b %d %Y %H %M")
		user_datetime = datetime.datetime(user_time[0], user_time[1], user_time[2], user_time[3], user_time[4], user_time[5])
		return user_datetime

