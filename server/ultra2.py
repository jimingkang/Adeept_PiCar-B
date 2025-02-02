#!/usr/bin/python3
# File name   : Ultrasonic.py
# Description : Detection distance and tracking with ultrasonic
# Website     : www.adeept.com
# E-mail      : support@adeept.com
# Author      : William
# Date        : 2018/10/12
import RPi.GPIO as GPIO
import time
import motor
import turn,led
import Adafruit_PCA9685
import server2

def num_import_int(initial):       #Call this function to import data from '.txt' file
    with open("set.txt") as f:
        for line in f.readlines():
            if(line.find(initial) == 0):
                r=line
    begin=len(list(initial))
    snum=r[begin:]
    n=int(snum)
    return n

#Set GPIO for Leds
left_R = 22
left_G = 23
left_B = 24

right_R = 10
right_G = 9
right_B = 25

#Set for motors
left_spd   = num_import_int('E_M1:')         #Speed of the car
right_spd  = num_import_int('E_M2:')         #Speed of the car
left       = num_import_int('E_T1:')         #Motor Left
right      = num_import_int('E_T2:')         #Motor Right
look_up_max    = num_import_int('look_up_max:')
look_down_max  = num_import_int('look_down_max:')
look_right_max = num_import_int('look_right_max:')
look_left_max  = num_import_int('look_left_max:')
turn_speed     = num_import_int('look_turn_speed:')
pwm0     = 0
pwm1     = 1
status   = 1    
forward  = 0
backward = 1
spd_ad_u   = 0.8
Tr = 11
Ec = 8
Ec_back = 7
Ec_left = 21
Ec_right = 26

pwm = Adafruit_PCA9685.PCA9685()    #Horn Control

def checkdist(sensor):       #Reading distance
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(Tr, GPIO.OUT,initial=GPIO.LOW)
    GPIO.setup(sensor, GPIO.IN)
    GPIO.output(Tr, GPIO.HIGH)
    time.sleep(0.000015)
    GPIO.output(Tr, GPIO.LOW)
    while not GPIO.input(sensor):
        pass
    t1 = time.time()
    while GPIO.input(sensor):
        pass
    t2 = time.time()
    return (t2-t1)*340/2

def setup():          #initialization
    motor.setup()
    led.setup() 

def destroy():        #motor stops when this program exit
    motor.destroy()
    GPIO.cleanup()

def loop(distance_stay,distance_range,strip):   #Tracking with Ultrasonic
    setup()
    turn.ahead()
    turn.middle()
    time.sleep(0.5)
    dis_front = checkdist(Ec)
    dis_back = checkdist(Ec_back) 
#    if dis_front < distance_range:             #Check if the target is in diatance range
#        if dis_front > (distance_stay+0.1) :   #If the target is in distance range and out of distance stay, then move forward to track
#            turn.ahead()
#            moving_time = (dis_front-distance_stay)/0.38
#            if moving_time > 1:
#                moving_time = 1
#            print('mf')
#            led.both_off()
#            led.cyan()
#            motor.motor_left(status, backward,left_spd*spd_ad_u)
#            motor.motor_right(status,forward,right_spd*spd_ad_u)
#            time.sleep(moving_time)
#            motor.motorStop()
#        elif dis_front < (distance_stay-0.1) : #Check if the target is too close, if so, the car move back to keep distance at distance_stay
#            if dis_back > distance_stay:       
#               moving_time = (distance_stay-dis_front)/0.38
#               print('mb')
#               led.both_off()
#               led.pink()
#               motor.motor_left(status, forward,left_spd*spd_ad_u)
#               motor.motor_right(status,backward,right_spd*spd_ad_u)
#               time.sleep(moving_time)
#               motor.motorStop()
#        el
    if dis_back < distance_range:             #Check if the target is in diatance range
        if dis_back > (distance_stay+0.1) :   #If the target is in distance range and out of distance stay, then move backwards to track
            pwm.set_pwm(12, 0, 4095)
            turn.ahead()
            moving_time = (dis_back-distance_stay)/0.38
            if moving_time > 0.5:
                moving_time = 0.5
            print('mb')
            led.both_off()
            led.red()
            server2.colorWipe(strip, server2.Color(255,255,0))                     #Yellow LED when in reverse            
            motor.motor_left(status, forward,left_spd*spd_ad_u)
            motor.motor_right(status,backward,right_spd*spd_ad_u)
            time.sleep(moving_time)
            pwm.set_pwm(12, 0, 0)   
            motor.motorStop()
            server2.colorWipe(strip, server2.Color(255,0,0))                       #LED red when idle                  
        elif dis_back < (distance_stay-0.1) : #Check if the target is too close, if so, the car move forward to keep distance at distance_stay
            if dis_front > distance_stay :
                moving_time = (distance_stay-dis_back)/0.38
                print('mf')
                led.both_off()
                led.cyan()
                server2.colorWipe(strip, server2.Color(0,0,0))                     #LED off when moving forward                 
                motor.motor_left(status,backward,left_spd*spd_ad_u)
                motor.motor_right(status,forward,right_spd*spd_ad_u)
                time.sleep(moving_time)
                motor.motorStop()
                server2.colorWipe(strip, server2.Color(255,0,0))                   #LED red when idle 
            else:
                turn.ultra_turn(look_left_max)   #Ultrasonic point Left
                time.sleep(0.5)                  #Wait for sensor to get into position
                dis_front = checkdist(Ec)
                if dis_front > distance_stay:
                    moving_time = 1
                    print('Turning left')
                    led.both_off()
                    led.cyan()
                    turn.left()
                    server2.colorWipe(strip, server2.Color(0,0,0))                 #LED off when moving forward                     
                    motor.motor_left(status,backward,left_spd*spd_ad_u)
                    motor.motor_right(status,forward,right_spd*spd_ad_u)
                    time.sleep(moving_time)
                    motor.motorStop()
                    server2.colorWipe(strip, server2.Color(255,0,0))               #LED red when idle                      
                    turn.ahead()
                    turn.middle()
                    time.sleep(0.5)
                    dis_front = checkdist(Ec)
                    if dis_front > distance_stay :
                        moving_time = 1
                        print('mf')
                        led.both_off()
                        led.cyan()
                        server2.colorWipe(strip, server2.Color(0,0,0))             #LED off when moving forward                     
                        motor.motor_left(status,backward,left_spd*spd_ad_u)
                        motor.motor_right(status,forward,right_spd*spd_ad_u)
                        time.sleep(moving_time)
                        motor.motorStop()
                        server2.colorWipe(strip, server2.Color(255,0,0))           #LED red when idle    
                else:
                    turn.ultra_turn(look_right_max)   #Ultrasonic point right
                    time.sleep(1)                  #Wait for sensor to get into position
                    dis_front = checkdist(Ec)
                    if dis_front > distance_stay:
                        moving_time = 1
                        print('Turning right')
                        led.both_off()
                        led.cyan()
                        turn.right()
                        server2.colorWipe(strip, server2.Color(0,0,0))             #LED off when moving forward   
                        motor.motor_left(status,backward,left_spd*spd_ad_u)
                        motor.motor_right(status,forward,right_spd*spd_ad_u)
                        time.sleep(moving_time)
                        motor.motorStop()
                        server2.colorWipe(strip, server2.Color(255,0,0))           #LED red when idle 
                        turn.ahead()
                        turn.middle()
                        time.sleep(1)
                        dis_front = checkdist(Ec)
                        if dis_front > distance_stay :
                            moving_time = 1
                            print('mf')
                            led.both_off()
                            led.cyan()
                            server2.colorWipe(strip, server2.Color(0,0,0))             #LED off when moving forward   
                            motor.motor_left(status,backward,left_spd*spd_ad_u)
                            motor.motor_right(status,forward,right_spd*spd_ad_u)
                            time.sleep(moving_time)
                            motor.motorStop()
                            server2.colorWipe(strip, server2.Color(255,0,0))           #LED red when idle 
                    else:                
                        print('unavoidable')          
        else:                            #If the target is at distance, then the car stay still
            motor.motorStop()
            server2.colorWipe(strip, server2.Color(255,0,0))           #LED red when idle 
            led.both_off()
            led.yellow()
    else:
        motor.motorStop()
        server2.colorWipe(strip, server2.Color(255,0,0))           #LED red when idle 

try:
    pass
except KeyboardInterrupt:
    destroy()
