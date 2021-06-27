// 
//  Button A: print mean total time
//  Button B: print statistics
//  total time counting
//  to apply to a different sensor just change the input
function get_data_point(): number {
    
    ll3 = input.lightLevel()
    //  print(str(ll))
    return ll3
}

input.onButtonPressed(Button.AB, function on_button_pressed_ab() {
    setup()
})
input.onButtonPressed(Button.A, function on_button_pressed_a() {
    serial.writeString("mean light level=" + ("" + ("" + mea)) + "  stdev=" + ("" + ("" + std)) + serial.NEW_LINE)
    serial.writeString("total time=" + ("" + ("" + total_time)) + " sec   time on=" + ("" + quad[Math.idiv(total_time, 240)]) + serial.NEW_LINE)
})
input.onButtonPressed(Button.B, function on_button_pressed_b() {
    let s: string;
    
    forever_stop2 = true
    serial.writeString("" + serial.NEW_LINE + serial.NEW_LINE + "hourID, minsOn" + serial.NEW_LINE)
    radio.sendString("hourID, minsOn")
    let i = 0
    while (i <= Math.idiv(total_time, 240) + 1 - 1) {
        s = "" + ("" + i) + ", " + ("" + ("" + quad[i])) + serial.NEW_LINE
        serial.writeString(s)
        radio.sendString(s)
        basic.pause(100)
        i += 1
    }
    serial.writeString("" + serial.NEW_LINE)
    serial.writeValue("total_time", total_time)
    forever_stop2 = false
})
function setup() {
    
    forever_stop3 = true
    mea = 0
    std = 0
    total_time = 0
    //  total time counting
    time_on = 0
    let j = 0
    while (j < 3000) {
        quad[j] = 0
        j += 1
    }
    ll2 = get_data_point()
    j = 0
    while (j < 6) {
        basic.showNumber(5 - j)
        j += 1
    }
    basic.clearScreen()
    //  input.light_level()
    calc_stats(40, 200)
    //  calculate the statistics for light on. 8 seconds
    if (std < 1) {
        std = 1
    }
    
    serial.writeString("mean=" + ("" + ("" + mea)) + "  stdev=" + ("" + ("" + std)) + "\n")
    basic.showIcon(IconNames.Yes)
    basic.pause(2000)
    basic.clearScreen()
    //  input.light_level()
    forever_stop3 = false
}

//  calculate statistics for a number of readings
//  returns mean, stdev - no long term storage needed
//  param: cnt - how many measurements to calculate
//  param: dly - milliseconds btw measurements
//  for the algo see https://en.wikipedia.org/wiki/Standard_deviation#Rapid_calculation_methods
//  number of items
function calc_stats(cnt: number, dly: number) {
    let Aprev: number;
    let thedata: number;
    
    //  running k value. It's k=t+1 since k starts from 0.
    n = cnt
    let t = 0
    while (t <= n - 1) {
        k = t + 1
        Aprev = A
        thedata = get_data_point()
        //  get next data point
        A = A + (thedata - A) / k
        Q = Q + (thedata - Aprev) * (thedata - A)
        mean += thedata
        basic.pause(dly)
        t += 1
    }
    stdev = Math.sqrt(Q / (n - 1))
    mean /= n
    mea = mean
    std = Math.ceil(stdev)
}

let stdev = 0
let Q = 0
let A = 0
let k = 0
let n = 0
let ll2 = 0
let time_on = 0
let forever_stop3 = false
let forever_stop2 = false
let std = 0
let mea = 0
let ll3 = 0
let total_time = 0
let mean = 0
//  Light state counter v1.00
//  We measure the time in seconds a light source is emitting light.
//  Learn (LS should be on):
//  User presses A and program calculates mean and standard deviation of the brightness emitted by the LS.
radio.setGroup(77)
radio.setTransmitPower(7)
let quad = control.createBuffer(3000)
//  every quad represents 240 seconds.
setup()
basic.forever(function on_forever() {
    let ll: number;
    
    let forever_stop = 0
    if (!forever_stop) {
        basic.pause(100)
        led.unplot(1, 1)
        basic.pause(900)
        ll = get_data_point()
        total_time = total_time + 1
        //  increase seconds
        //  if ll >= mea-3*std:      # If light level is above the mean - 3 stdev then consider it on
        //  time_on = time_on + 1
        if (ll >= 0.7 * mea) {
            quad[Math.idiv(total_time, 240)] += 1
            //  increase the appropriate bin by 1 sec max secs per cell is 240=4min
            led.plot(1, 1)
        }
        
    }
    
})
