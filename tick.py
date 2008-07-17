import time

class Tick(object):
    def __init__(self):
        self.refresh = 1
        self.current_time = time.localtime()
        self.hour = self.current_time[3]

    def update(self):
        self.current_time = time.localtime()
        self.hour = self.current_time[3]
        self.to_twelve()
        self.display()
        time.sleep(self.refresh)

    def to_twelve(self):
        if self.hour > 12:
            self.hour -= 12
            self.suffix = "PM"
        else:
            self.suffix = "AM"

    def digit_tostring(self, digit):
        if digit < 10:
            return "0%d" % digit
        else:
            return "%d" % digit
        
    def display(self):
        self.sync()
        print "%s:%s:%s %s" % (self.hour, self.digit_tostring(self.current_time[4]), self.digit_tostring(self.current_time[5]), self.suffix)

    def sync(self):
        s_second = self.current_time[5]
        while s_second == self.current_time[5]:
            self.current_time = time.localtime()

def main_loop():
    t = Tick()
    while 1:
        t.update()

if __name__ == "__main__":
    main_loop()

