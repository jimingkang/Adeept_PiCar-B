#!/usr/bin/python3
# File name   : findline.py
# Description : line tracking 
# Website     : www.adeept.com
# E-mail      : support@adeept.com
# Author      : William
# Date        : 2018/10/12
import RPi.GPIO as GPIO
import time
import motor
import turn
import led

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

line_pin_right = 19
line_pin_middle = 16
line_pin_left = 20

left_R = 22
left_G = 23
left_B = 24

right_R = 10
right_G = 9
right_B = 25

on  = GPIO.LOW
off = GPIO.HIGH

spd_ad_1 = 0.6
spd_ad_2 = 0.8
spd_ad_3 = 1

def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(line_pin_right,GPIO.IN)
    GPIO.setup(line_pin_middle,GPIO.IN)
    GPIO.setup(line_pin_left,GPIO.IN)
    try:
        motor.setup()
    except:
        pass

def run():
    #Read previous infrared inputs
    status_middle_old = var_import_int('status_middle:')
    status_left_old   = var_import_int('status_left:')
    status_right_old  = var_import_int('status_right:')

    status_right = GPIO.input(line_pin_right)
    status_middle = GPIO.input(line_pin_middle)
    status_left = GPIO.input(line_pin_left)
    #Update infrared readings
    replace_var('status_middle:',status_middle)
    replace_var('status_left:',status_left)
    replace_var('status_right:',status_right)

    print(status_left,status_middle,status_right)

    #Respond to sensor readings
    if status_middle == 1: #Line is lost
        turn.middle()
        led.both_off()
        led.yellow()
        motor.motor_right(status,backward,right_spd*spd_ad_3)
        time.sleep(0.05)
        if status_left_old == 0 and status_middle_old == 0:
            turn.left()
            led.both_off()
            led.side_on(left_R)
            motor.motor_right(status,forward,right_spd*spd_ad_2)
            time.sleep(0.5)
            turn.right()
            led.both_off()
            led.side_on(right_R)
            motor.motor_right(status,backward,right_spd*spd_ad_2)  
            time.sleep(0.5)
            turn.left()
            led.both_off()
            led.side_on(left_R)
            motor.motor_right(status,forward,right_spd*spd_ad_2)          
    elif status_left== 0:
        turn.left()
        led.both_off()
        led.side_on(left_R)
        motor.motor_right(status,forward,right_spd*spd_ad_2)
    elif status_right == 0:
        turn.right()
        led.both_off()
        led.side_on(right_R)
        motor.motor_right(status,forward,right_spd*spd_ad_2)
    else:
        turn.middle()
        led.both_off()
        led.cyan()
        motor.motor_right(status,forward,right_spd*spd_ad_1)
    pass

try:
    pass
except KeyboardInterrupt:
    motor.motorStop()
