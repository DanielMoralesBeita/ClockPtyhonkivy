'''
Code of How to create countdown using label only
'''
  
# Program to Show how to create a switch 
# import kivy module    
import kivy  
      
# base Class of your App inherits from the App class.    
# app:always refers to the instance of your application   
from kivy.app import App 
    
# this restrict the kivy version i.e  
# below this kivy version you cannot  
# use the app or software  
kivy.require('1.9.0')

# The Label widget is for rendering text.
from kivy.uix.label import Label

# The Clock object allows you to schedule
# a function call in the future; once or
# repeatedly at specified intervals.
from kivy.clock import Clock
 
# The kivy App that extends from the App class
class ClockDemo(App):

    count = 0

    def build(self):
       self.myLabel = Label(text ='Waiting for updates...')

       # Start the clock
       Clock.schedule_interval(self.Callback_Clock, 1)
       
       return self.myLabel

    def Callback_Clock(self, dt):
        self.count = self.count + 1
        self.myLabel.text = "Updated % d...times"% self.count

       
# Run the app
if __name__ == '__main__':
    ClockDemo().run()