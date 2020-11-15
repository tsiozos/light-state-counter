# Light state counter v1.00
# We measure the time in seconds a light source is emitting light.
# Learn (LS should be on):
# User presses A and program calculates mean and standard deviation of the brightness emitted by the LS.
# 

radio.set_group(77)
radio.set_transmit_power(7)

forever_stop = False

mea=0
std=0
total_time=0    #total time counting
time_on=0       #time the light source is on

#initialize hour count
# total_time % 240 is the bin to add time_on.
# it's good for 3000*4/1440 hours = 8 days
quad=bytearray(3000)    #every quad represents 240 seconds.

setup()

def on_forever():
    global total_time, time_on, forever_stop, quad
    if not forever_stop:
        basic.pause(100)
        led.unplot(1,1)
        basic.pause(900)
        ll = get_data_point()
        total_time = total_time+1   # increase seconds
        #if ll >= mea-3*std:      # If light level is above the mean - 3 stdev then consider it on
            #time_on = time_on + 1
        if ll >= 0.7 * mea:     # if light level is above 70% of mean
            quad[total_time // 240] += 1    # increase the appropriate bin by 1 sec max secs per cell is 240=4min
            led.plot(1,1)

basic.forever(on_forever)

def on_button_pressed_a():
    serial.write_string("mean light level="+str(mea)+"  stdev="+str(std)+serial.NEW_LINE)
    serial.write_string("total time="+str(total_time)+" sec   time on="+quad[total_time // 240]+serial.NEW_LINE)

input.on_button_pressed(Button.A, on_button_pressed_a)

def on_button_pressed_ab():
    setup()

input.on_button_pressed(Button.AB, on_button_pressed_ab)

def on_button_pressed_b():
    global quad
    forever_stop = True
    serial.write_string(serial.NEW_LINE+serial.NEW_LINE+"hourID, minsOn"+serial.NEW_LINE)
    radio.send_string("hourID, minsOn")
    for i in range(total_time // 240 + 1):
        s = str(i)+", "+str(quad[i])+serial.NEW_LINE
        serial.write_string(s)
        radio.send_string(s)
        basic.pause(100)

    serial.write_string(serial.NEW_LINE)
    serial.write_value("total_time", total_time)
    forever_stop = False

input.on_button_pressed(Button.B, on_button_pressed_b)

def setup():
    global mea, std, total_time, time_on, quad
    forever_stop = True
    mea=0
    std=0
    total_time=0    #total time counting
    time_on=0       #time the light source is on
    #hour=bytearray(240)
    for i in range(3000):
        quad[i]=0
    ll=get_data_point()
    #ll=get_data_point()
    for i in range(6):
        basic.show_number(5-i)
    basic.clear_screen()
    #input.light_level()
    calc_stats(40, 200)    #calculate the statistics for light on. 8 seconds
    if std < 1: std = 1
    serial.write_string("mean="+str(mea)+"  stdev="+str(std)+"\n")
    basic.show_icon(IconNames.YES)
    basic.pause(2000)
    basic.clear_screen()
    #input.light_level()
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
