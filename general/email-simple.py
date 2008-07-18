# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.MIMEText import MIMEText

# Open a plain text file for reading.  For this example, assume that
# the text file contains only ASCII characters.
fp = 'I love lamp'
msg = MIMEText(fp)
#fp = open(textfile, 'rb')
# Create a text/plain message

# me == the sender's email address
# you == the recipient's email address
msg['Subject'] = 'Testing pymail.'
msg['From'] = 'Purdue Sport Parachute Club <noreply@purdueskydiving.org>'
msg['To'] = 'mailinglist@purdueskydiving.org'
receive = ['blakesmith0@gmail.com', 'bhsmith@purdue.edu']

tolist = 'blakesmith0@gmail.com'
# Send the message via our own SMTP server, but don't include the
# envelope header.
s = smtplib.SMTP()
s.connect('localhost')
s.sendmail(msg['From'], receive, msg.as_string())
s.close()
