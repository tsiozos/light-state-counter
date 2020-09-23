# Light state counter v1.00
# We measure the time in seconds a light source is emitting light.
# Learn (LS should be on):
# User presses A and program calculates mean and standard deviation of the brightness emitted by the LS.
# 

forever_stop = False

mea=0
std=0
total_time=0    #total time counting
time_on=0       #time the light source is on

#initialize hour count
# total_time % 3600 is the bin to add time_on.
# it's good for 240 hours = 10 days
hour=[0]
for i in range(240-1):
    hour.append(0)

setup()

def on_forever():
    global total_time, time_on, forever_stop, hour
    if not forever_stop:
        basic.pause(500)
        ll = get_data_point()
        led.unplot(1,1)
        basic.pause(500)
        total_time = total_time+1   # increase seconds
        if ll >= mea-3*std:      # If light level is above the mean - 3 stdev then consider it on
            #time_on = time_on + 1
            hour[total_time // 3600] += 1    # increase the appropriate bin by 1 sec
            led.plot(1,1)

basic.forever(on_forever)

def on_button_pressed_a():
    serial.write_string("mean light level="+str(mea)+"  stdev="+str(std)+"\n")
    serial.write_string("total time="+str(total_time)+" sec   time on="+time_on+"\n\n\n\n")

input.on_button_pressed(Button.A, on_button_pressed_a)

def on_button_pressed_ab():
    setup()

input.on_button_pressed(Button.AB, on_button_pressed_ab)

def on_button_pressed_b():
    global hour
    forever_stop = True
    serial.write_string("\n\n\nhourID, minsOn\n")
    for i in range(total_time // 3600 + 1):
        serial.write_string(str(i)+", "+str(hour[i])+"\n")
        basic.pause(100)

    serial.write_string("\n")
    serial.write_value("total_time", total_time)
    forever_stop = False

input.on_button_pressed(Button.B, on_button_pressed_b)

def setup():
    global mea, std, total_time, time_on, hour
    forever_stop = True
    mea=0
    std=0
    total_time=0    #total time counting
    time_on=0       #time the light source is on
    #hour=bytearray(240)
    for i in range(240):
        hour[i]=0
    ll=get_data_point()
    for i in range(10):
        basic.show_number(9-i)
    calc_stats(20, 250)    #calculate the statistics for light on
    serial.write_string("mean="+str(mea)+"  stdev="+str(std)+"\n")
    basic.show_icon(IconNames.YES)
    basic.pause(3000)
    basic.clear_screen()
    forever_stop = False

#calculate statistics for a number of readings
#returns mean, stdev - no long term storage needed
#param: cnt - how many measurements to calculate
#param: dly - milliseconds btw measurements
def calc_stats(cnt, dly):
    global mea, std
    # for the algo see https://en.wikipedia.org/wiki/Standard_deviation#Rapid_calculation_methods
    A = 0
    Q = 0
    k = 0 #running k value. It's k=t+1 since k starts from 0.
    n = cnt # number of items
    mean = 0
    for t in range(n):
        k=t+1
        Aprev = A
        thedata=get_data_point()   #get next data point
        A = A + (thedata-A)/k
        Q = Q + (thedata-Aprev)*(thedata-A)
        mean += thedata
        basic.pause(dly)
    stdev = Math.sqrt(Q/(n-1)) #sample standard deviation
    mean /= n
    mea = mean
    std = Math.ceil(stdev)

#to apply to a different sensor just change the input
def get_data_point():
    ll = input.light_level()
    #print(str(ll))
    return ll
