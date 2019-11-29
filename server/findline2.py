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
import ultra2

def num_import_int(initial):        #Call this function to import data from '.txt' file
    with open("set.txt") as f:
        for line in f.readlines():
            if(line.find(initial) == 0):
                r=line
    begin=len(list(initial))
    snum=r[begin:]
    n=int(snum)
    return n

def replace_var(initial,new_num):   #Call this function to replace data in '.txt' file
    newline=""
    str_num=str(new_num)
    with open("Variables.txt","r") as f:
        for line in f.readlines():
            if(line.find(initial) == 0):
                line = initial+"%s" %(str_num+"\n")
            newline += line
    with open("Variables.txt","w") as f:
        f.writelines(newline)

def var_import_int(initial):        #Call this function to import data from '.txt' file
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

status_middle_old = var_import_int('status_middle:')
status_left_old   = var_import_int('status_left:')
status_right_old  = var_import_int('status_right:')

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

spd_ad_1 = 1
spd_ad_2 = 0.75

distance_front = 0.05
distance_back  = 0.4
Ec = 8
Ec_back = 7

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
    status_right = GPIO.input(line_pin_right)
    status_middle = GPIO.input(line_pin_middle)
    status_left = GPIO.input(line_pin_left)

    replace_var('status_middle:',status_middle)
    replace_var('status_left:',status_left)
    replace_var('status_right:',status_right)

    dis_front = ultra2.checkdist(Ec)
    dis_back = ultra2.checkdist(Ec_back)
#    if dis_front < distance_front:
#        print('Object in range')
#    else:
    print(status_left,status_middle,status_right)
    if status_middle == 1 and status_left == 1 and status_right ==1:
        turn.middle()
        led.both_off()
        led.yellow()
        motor.motor_left(status, forward,left_spd*spd_ad_1)
        motor.motor_right(status,backward,right_spd*spd_ad_1)
#        time.sleep(1)
#        turn.left()
#        if status_middle_old == 0 and status_left_old == 0:
#            motor.motor_right(status,forward,right_spd*spd_ad_1)
#            time.sleep(1.7)  
    elif status_left == 0:
        turn.left()
        led.both_off()
        led.side_on(left_R)
        motor.motor_left(status, backward,left_spd*spd_ad_2)
        motor.motor_right(status,forward,right_spd*spd_ad_2)
    elif status_right == 0:
        turn.right()
        led.both_off()
        led.side_on(right_R)
        motor.motor_left(status, backward,left_spd*spd_ad_2)
        motor.motor_right(status,forward,right_spd*spd_ad_2)
    elif status_middle == 1:
        turn.middle()
        led.both_off()
        led.yellow()
        motor.motor_left(status, forward,left_spd*spd_ad_1)
        motor.motor_right(status,backward,right_spd*spd_ad_1)     
    else:
        turn.middle()
        led.both_off()
        led.cyan()
        motor.motor_left(status, backward,left_spd)
        motor.motor_right(status,forward,right_spd)
    pass
try:
    pass
except KeyboardInterrupt:
    motor.motorStop()
