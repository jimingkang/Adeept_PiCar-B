#!/usr/bin/python3
# File name   : findline2.py
# Description : line tracking 
# Author      : William
# Date        : 2018/10/12
# Modified by : Thomas Mauldin
# Modified on : 2019/11/30
import RPi.GPIO as GPIO
import time
import motor
import turn
import led
import ultra2
import Adafruit_PCA9685

pwm = Adafruit_PCA9685.PCA9685()    #Horn Control

def num_import_int(initial):        #Call this function to import data from '.txt' file
    with open("set.txt") as f:
        for line in f.readlines():
            if(line.find(initial) == 0):
                r=line
    begin=len(list(initial))
    snum=r[begin:]
    n=int(snum)
    return n

def replace_var(initial,new_num):   #Call this function to replace data in 'Variable.txt' file
    newline=""
    str_num=str(new_num)
    with open("Variables.txt","r") as f:
        for line in f.readlines():
            if(line.find(initial) == 0):
                line = initial+"%s" %(str_num+"\n")
            newline += line
    with open("Variables.txt","w") as f:
        f.writelines(newline)

def var_import_int(initial):        #Call this function to import data from 'Variable.txt' file
    with open("Variables.txt") as f:
        for line in f.readlines():
            if(line.find(initial) == 0):
                r=line
    begin=len(list(initial))
    snum=r[begin:]
    n=int(snum)
    return n

status     = 1          #Motor rotation
forward    = 0          #Motor forward
backward   = 1          #Motor backward

left_spd   = num_import_int('E_M1:')         #Speed of the car
right_spd  = num_import_int('E_M2:')         #Speed of the car
left       = num_import_int('E_T1:')         #Motor Left
right      = num_import_int('E_T2:')         #Motor Right

#GPIO pins for infrared sensors
line_pin_rr = 19
line_pin_r = 26
line_pin_middle = 16
line_pin_l = 21
line_pin_ll = 20

#Set GPIO for front LEDs
left_R = 22
left_G = 23
left_B = 24
right_R = 10
right_G = 9
right_B = 25

#Digital Logic
on  = GPIO.LOW
off = GPIO.HIGH

#Speeds (1 max)
spd_ad_1 = 0.8
spd_ad_2 = 0.85
spd_ad_3 = 1

#Ultrasound
#distance thresholds (m)
distance_front = 0.4
distance_back  = 0.4
#pins
Ec = 8
Ec_back = 7

def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(line_pin_rr,GPIO.IN)
    GPIO.setup(line_pin_r,GPIO.IN)
    GPIO.setup(line_pin_middle,GPIO.IN)
    GPIO.setup(line_pin_l,GPIO.IN)
    GPIO.setup(line_pin_ll,GPIO.IN)
    try:
        motor.setup()
    except:
        pass

def run(dist_front,dist_front_old):
    #Read previous infrared inputs
    status_middle_old = var_import_int('status_middle:')
    status_l_old   = var_import_int('status_l:')
    status_ll_old   = var_import_int('status_ll:')
    status_r_old  = var_import_int('status_r:')

    #Get new infrared inputs  
    status_rr = GPIO.input(line_pin_rr)
    status_r = GPIO.input(line_pin_r)               #Not functioning
    status_middle = GPIO.input(line_pin_middle)
    status_l = GPIO.input(line_pin_l)
    status_ll = GPIO.input(line_pin_ll)
    #Update infrared readings  
    replace_var('status_middle:',status_middle)
    replace_var('status_ll:',status_ll)
    replace_var('status_l:',status_l)
    replace_var('status_r:',status_rr)

    print(status_ll,status_l,status_middle,status_r,status_rr,' ',dist_front,dist_front_old)

    #Respond to sensor readings
    if dist_front < distance_front and dist_front_old < distance_front:
        pwm.set_pwm(12, 0, 4095)                                                #Honk horn
        return 1
    elif status_middle == 1 and status_rr == 1 and status_ll == 1 and status_l == 1:  #Line is lost
#        pwm.set_pwm(12, 0, 4095)                                                #Alarm motorists that the car is backing up
        turn.middle()
        led.both_off()
        led.yellow()
        motor.motor_right(status,backward,right_spd*spd_ad_3)
        time.sleep(0.1)
        return 0
    elif status_middle== 0 and status_ll == 0:                                      #       
        pwm.set_pwm(12, 0, 0)                                                       #Turn backup alarm off        
        turn.left()
        led.both_off()
        led.side_on(left_R)
        motor.motor_right(status,forward,right_spd*spd_ad_2)
        time.sleep(0.3)
        turn.right()
        led.both_off()
        led.side_on(right_R)
        motor.motor_right(status,backward,right_spd*spd_ad_3)  
        time.sleep(0.15)
        return 0
    elif status_middle== 0 and status_rr == 0:    
        pwm.set_pwm(12, 0, 0)           #Turn backup alarm off        
        turn.right()
        led.both_off()
        led.side_on(left_R)
        motor.motor_right(status,forward,right_spd*spd_ad_2)
        time.sleep(0.3)
        turn.left()
        led.both_off()
        led.side_on(right_R)
        motor.motor_right(status,backward,right_spd*spd_ad_3)  
        time.sleep(0.15)                 
        return 0
    elif status_rr == 0:    
        pwm.set_pwm(12, 0, 0)           #Turn backup alarm off        
        turn.right()
        led.both_off()
        led.side_on(left_R)
        motor.motor_right(status,forward,right_spd*spd_ad_2)
    elif status_ll == 0:
        backup_cnt = 0                  #Reset safety counter        
        pwm.set_pwm(12, 0, 0)           #Turn backup alarm off        
        turn.left()
        led.both_off()
        led.side_on(right_R)
        motor.motor_right(status,forward,right_spd*spd_ad_2)
        return 0
    else:      
        pwm.set_pwm(12, 0, 0)           #Turn backup alarm off        
        turn.middle()
        led.both_off()
        led.cyan()
        motor.motor_right(status,forward,right_spd*spd_ad_1)
        return 0
    pass

try:
    pass
except KeyboardInterrupt:
    motor.motorStop()
