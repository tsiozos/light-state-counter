#
# Button A: print mean total time
# Button B: print statistics
# total time counting

# to apply to a different sensor just change the input
def get_data_point():
    global ll3
    ll3 = input.light_level()
    # print(str(ll))
    return ll3

def on_button_pressed_ab():
    setup()
input.on_button_pressed(Button.AB, on_button_pressed_ab)

def on_button_pressed_a():
    serial.write_string("mean light level=" + ("" + str(mea)) + "  stdev=" + ("" + str(std)) + serial.NEW_LINE)
    serial.write_string("total time=" + ("" + str(total_time)) + " sec   time on=" + str(quad[Math.idiv(total_time, 240)]) + serial.NEW_LINE)
input.on_button_pressed(Button.A, on_button_pressed_a)

def on_button_pressed_b():
    global forever_stop2
    forever_stop2 = True
    serial.write_string("" + serial.NEW_LINE + serial.NEW_LINE + "hourID, minsOn" + serial.NEW_LINE)
    radio.send_string("hourID, secOn")
    i = 0
    while i <= Math.idiv(total_time, 240) + 1 - 1:
        s = "" + str(i) + ", " + ("" + str(quad[i])) + serial.NEW_LINE
        serial.write_string(s)
        radio.send_string(s)
        basic.pause(randint(100,130))
        i += 1
    serial.write_string("" + (serial.NEW_LINE))
    serial.write_value("total_time", total_time)
    radio.send_string("total_time="+total_time)
    basic.pause(randint(200,300))
    radio.send_string("total_time="+total_time)
    forever_stop2 = False
input.on_button_pressed(Button.B, on_button_pressed_b)

def setup():
    global forever_stop3, mea, std, total_time, time_on, ll2
    forever_stop3 = True
    mea = 0
    std = 0
    total_time = 0
    # total time counting
    time_on = 0
    j = 0
    while j < 3000:
        quad[j] = 0
        j += 1
    ll2 = get_data_point()
    j = 0
    while j < 6:
        basic.show_number(5 - j)
        j += 1
    basic.clear_screen()
    # input.light_level()
    calc_stats(40, 200)
    # calculate the statistics for light on. 8 seconds
    if std < 1:
        std = 1
    serial.write_string("mean=" + ("" + str(mea)) + "  stdev=" + ("" + str(std)) + "\n")
    basic.show_icon(IconNames.YES)
    basic.pause(2000)
    basic.clear_screen()
    # input.light_level()
    forever_stop3 = False
# calculate statistics for a number of readings
# returns mean, stdev - no long term storage needed
# param: cnt - how many measurements to calculate
# param: dly - milliseconds btw measurements
# for the algo see https://en.wikipedia.org/wiki/Standard_deviation#Rapid_calculation_methods
# number of items
def calc_stats(cnt: number, dly: number):
    global n, k, A, Q, mean, stdev, mea, std
    # running k value. It's k=t+1 since k starts from 0.
    n = cnt
    t = 0
    while t <= n - 1:
        k = t + 1
        Aprev = A
        thedata = get_data_point()
        # get next data point
        A = A + (thedata - A) / k
        Q = Q + (thedata - Aprev) * (thedata - A)
        mean += thedata
        basic.pause(dly)
        t += 1
    stdev = Math.sqrt(Q / (n - 1))
    mean /= n
    mea = mean
    std = Math.ceil(stdev)
stdev = 0
Q = 0
A = 0
k = 0
n = 0
ll2 = 0
time_on = 0
forever_stop3 = False
forever_stop2 = False
std = 0
mea = 0
ll3 = 0
total_time = 0
mean = 0

# Light state counter v1.00
# We measure the time in seconds a light source is emitting light.
# Learn (LS should be on):
# User presses A and program calculates mean and standard deviation of the brightness emitted by the LS.
radio.set_group(77)
radio.set_transmit_power(7)
quad = bytearray(3000)
# every quad represents 240 seconds.
setup()

def on_forever():
    global total_time
    forever_stop = 0
    if not (forever_stop):
        basic.pause(100)
        led.unplot(1, 1)
        basic.pause(900)
        ll = get_data_point()
        total_time = total_time + 1
        # increase seconds
        # if ll >= mea-3*std:      # If light level is above the mean - 3 stdev then consider it on
        # time_on = time_on + 1
        if ll >= mea - std*3:
            quad[Math.idiv(total_time, 240)] += 1
            # increase the appropriate bin by 1 sec max secs per cell is 240=4min
            led.plot(1, 1)
        
        #every 600 seconds send radio data
        if total_time % 600 == 0:
            on_button_pressed_b()   #pretend we pressed the B button
basic.forever(on_forever)
