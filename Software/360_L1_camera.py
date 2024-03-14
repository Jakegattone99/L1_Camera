import RPi.GPIO as GPIO
import time
import picamera
"""
This program is designed to run on raspberry pi 0 or 0Ws. It will
trigger a camera using a hall effect sensor, and will alert the
user to its activity with a buzzer (active). 

1) Program start, 1 long buzz
2) Wait for hall effect sensor to activate (debounce available)
3) Buzz once to alert user that camera sucessfully started
4) Wait for hall effect sensor to activate (")
5) Buzz twice to alert user that camera sucessfully stopped
6) Restart program after sucessful recording
7) If there is an error, buzz 3 times, then restart

"""
###################################################################   
##                          Definitions                          ##
###################################################################
hall_effect_pin = 37                                              # GPIO pin for the hall effect sensor (BOARD numbering)
buzzer_pin = 35                                                   # GPIO pin for the buzzer (BOARD numbering)
pis = 4                                                           # Number of pis
pi = 1                                                            # pi number, out of 4
#                                                                 ###
###################################################################   
##                          GPIO Setup                           ##
###################################################################
GPIO.setmode(GPIO.BOARD)                                          # GPIO Board numbering, not BCM
GPIO.setup(hall_effect_pin, GPIO.IN)                              # Hall effect sensor as input
GPIO.setup(buzzer_pin, GPIO.OUT)                                  # Buzzer as output
#                                                                 ###
###################################################################   
##                            Buzzer                             ##
###################################################################
def emit_beep(value, durration):                                  # Function definition, # of beeps, durration of buzzer, per beep
    while value > 0:                                              # While there are still more beeps to do:
        GPIO.output(buzzer_pin, GPIO.HIGH)                        # Turn the buzzer on
        time.sleep(durration / 2)                                 # Wait for half of buzz time
        GPIO.output(buzzer_pin, GPIO.LOW)                         # Turn the buzzer off
        time.sleep(durration / 2)                                 # Wait for second half of buzz time
        value -= 1                                                # Take 1 beep out of que because it has been competed
#                                                                 ###
###################################################################   
##                          Hall Effect                          ##
###################################################################
def read_hall_effect(debounce):                                   # Function definition, durration of debounce, 0 for none
    while GPIO.input(hall_effect_pin) == GPIO.HIGH:               # Poll the hall effect sensor at 2hz until it is read active
        time.sleep(0.5)                                           # Wait half a second to maintain 2hz poll rate
        print(GPIO.input(hall_effect_pin))                        #DEBUG
    print("Debounce")                                             #DEBUG
#                                                                 #
    if debounce:                                                  # If there is debouncing:
        counter = 0                                               # Initialiize a counter
        elapsed_time = 0                                          # Start 'stopwatch' at 0 seconds
        start_time = time.time()                                  # Record the start time
        while elapsed_time <= debounce:                           # While the 'stopwatch' is lower than the debounce time
            if GPIO.input(hall_effect_pin) == GPIO.LOW:           # Count how many times the sensor is still active (10hz)
                print(GPIO.input(hall_effect_pin))                #DEBUG
                counter += 1                                      # (Increase counter)
                time.sleep(0.1)                                   # Wait a tenth of a second to maintain 10hz poll rate
            elapsed_time = time.time() - start_time               # Update 'stopwatch' with elapsed time
        if counter >= 9 * debounce:                               # If the sensor was active for at least 90% of the debounce period:
            return                                                # End return to main function
        else:                                                     # If the sensor was not active for 90%
            read_hall_effect(debounce)                            # Go back to the while loop
#                                                                 #
#                                                                 # If there is no debouncing, return to main function imediatly
#                                                                 ###
###################################################################   
##                             Main                              ##
###################################################################
def main():                                                       # Function definition, main code
    print("Chirp to indicate program start.")                     #DEBUG
    time.sleep(pi - 1)                                            # Wait custom delay to make sure pi does not buzz over a different pi
    emit_beep(1, 0.5)                                             # Buzz to signify start of program
    time.sleep(pis - pi + 0.5)                                    # Wait for other pis to finish before polling the hall effect sensor
#                                                                 #
    read_hall_effect(2)                                           # Wait for hall effect, debounce 2 seconds
#                                                                 #
    print("Hall effect triggered. Starting camera recording.")    #DEBUG
#                                                                 #
    timestamp = time.strftime("%Y%m%d%H%M%S")                     # Generate timestamp for the video
    video_filename = 'video_{}.h264'.format(timestamp)            # Set video format to H264
    camera = picamera.PiCamera()                                  # Define camera object
    try:                                                          # Try to start the camera
        camera.start_recording(video_filename)                    # (Start camera)
    except Exception as e:                                        # If there is an error starting the camera
        print("Error stopping camera:", str(e))                   #DEBUG
        time.sleep(pi - 1)                                        # Wait custom delay to make sure pi does not buzz over a different pi
        emit_beep(3, 0.25)                                        # Beep 3 times to signify error
        time.sleep(pis - pi)                                      # Wait for other pis to finish before restarting
        main()                                                    # Restart program
#                                                                 #
    time.sleep(pi - 1)                                            # (If sucessful start) Wait custom delay to make sure pi does not buzz over a different pi
    emit_beep(1, 0.25)                                            # Buzz once to singify start of recording
    time.sleep(pis - pi)                                          # Wait for other pis to finsish before polling the hall effect sensor
#                                                                 #
    read_hall_effect(2)                                           # Wait for hall effect, debounce 2 seconds
#                                                                 #
    print("Hall effect triggered (2). Stopping camera recording.")#DEBUG
#                                                                 #
    try:                                                          # Try to stop the camera
        camera.stop_recording()                                   # (stop camera)
        camera.close()                                            # Release the camera for new recording
    except Exception as e:                                        # If there is an error stopping the camera                                  
        print("Error stopping camera:", str(e))                   #DEBUG
        time.sleep(pi - 1)                                        # Wait custom delay to make sure pi does not buzz over a different pi
        emit_beep(3, 0.25)                                        # Beep 3 times to signify error
        time.sleep(pis - pi)                                      # Wait for other pis to finish before restarting
        main()                                                    # Restart program
#                                                                 #
    time.sleep(pi - 1)                                            # (If sucessful stop) Wait custom delay to make sure pi does not buzz over a different pi
    emit_beep(2, 0.25)                                            # Buzz twice to signify end of recording
    time.sleep(pis - pi)                                          # Wait for other pis to finish before restarting
    main()                                                        # Restart program
#                                                                 ###
###################################################################   
##                             Start                             ##
###################################################################
try:                                                              # Start the program
    main()                                                        # Call main code
#                                                                 ###
###################################################################   
##                              End                              ##
###################################################################
except KeyboardInterrupt:                                         # If ctrl + C in console
    print("Program terminated by user")                           #DEBUG
    time.sleep(pi - 1)                                            # Wait a custom delay to make sure pi does not buzz over a different pi
    emit_beep(3, 0.25)                                            # Buzz 3 times to signify error
    time.sleep(pis - pi)                                          # Wait for other pis to finish
finally:                                                          # Then:
    GPIO.cleanup()                                                # Free GPIO for other programs or restart
    if 'camera' in locals():                                      # If the camera is running or still defined
        try:                                                      # Try to close the camera
            camera.close()                                        # (close the camera)
        except Exception as e:                                    # If there is an error closing the camera:
            print("Error closing camera:", str(e))                # Print the error
            time.sleep(pi - 1)                                    # Wait custom delay to make sure pi does not buzz over a different pi
            emit_beep(3, 0.25)                                    # Beep 3 times to signify error
            time.sleep(pis - pi)                                  # Wait for other pis to finish before restarting