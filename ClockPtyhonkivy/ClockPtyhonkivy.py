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

# Animation is used to animate Widget properties
from kivy.animation import Animation

# The Properties classes are used when you create an EventDispatcher.
from kivy.properties import StringProperty, NumericProperty


# create a label class
class Clock(Label):

    # Set the numeric property
    # i.e set the counter number you can change it accordingly
    a = NumericProperty(100)  # seconds

    # To start countdown
    def start(self):
        Animation.cancel_all(self)  # stop any current animations
        self.anim = Animation(a = 0, duration = self.a)

        # TO finish count down
        def finish_callback(animation, clock):
            clock.text = "FINISHED"

        self.anim.bind(on_complete = finish_callback)
        self.anim.start(self)

    # If u remove this there will be nothing on screen
    def on_a(self, instance, value):
        self.text = str(round(value, 1))

        
# Create the App class
class TimeApp(App):
    def build(self):
        # Create the object of Clock class
        clock = Clock()

        # call the function from class Clock
        clock.start()
        return clock

# Run the App
if __name__ == "__main__":
    TimeApp().run()
