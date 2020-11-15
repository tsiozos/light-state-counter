//  Light state counter v1.00
//  We measure the time in seconds a light source is emitting light.
//  Learn (LS should be on):
//  User presses A and program calculates mean and standard deviation of the brightness emitted by the LS.
//  
radio.setGroup(77)
radio.setTransmitPower(7)
let forever_stop = false
let mea = 0
let std = 0
let total_time = 0
// total time counting
let time_on = 0
// time the light source is on
// initialize hour count
//  total_time % 240 is the bin to add time_on.
//  it's good for 3000*4/1440 hours = 8 days
let quad = control.createBuffer(3000)
// every quad represents 240 seconds.
setup()
basic.forever(function on_forever() {
    let ll: number;
    
    if (!forever_stop) {
        basic.pause(100)
        led.unplot(1, 1)
        basic.pause(900)
        ll = get_data_point()
        total_time = total_time + 1
        //  increase seconds
        // if ll >= mea-3*std:      # If light level is above the mean - 3 stdev then consider it on
        // time_on = time_on + 1
        if (ll >= 0.7 * mea) {
            //  if light level is above 70% of mean
            quad[Math.idiv(total_time, 240)] += 1
            //  increase the appropriate bin by 1 sec max secs per cell is 240=4min
            led.plot(1, 1)
        }
        
    }
    
})
input.onButtonPressed(Button.A, function on_button_pressed_a() {
    serial.writeString("mean light level=" + ("" + mea) + "  stdev=" + ("" + std) + serial.NEW_LINE)
    serial.writeString("total time=" + ("" + total_time) + " sec   time on=" + quad[Math.idiv(total_time, 240)] + serial.NEW_LINE)
})
input.onButtonPressed(Button.AB, function on_button_pressed_ab() {
    setup()
})
input.onButtonPressed(Button.B, function on_button_pressed_b() {
    let s: string;
    
    let forever_stop = true
    serial.writeString(serial.NEW_LINE + serial.NEW_LINE + "hourID, minsOn" + serial.NEW_LINE)
    radio.sendString("hourID, minsOn")
    for (let i = 0; i < Math.idiv(total_time, 240) + 1; i++) {
        s = "" + i + ", " + ("" + quad[i]) + serial.NEW_LINE
        serial.writeString(s)
        radio.sendString(s)
        basic.pause(100)
    }
    serial.writeString(serial.NEW_LINE)
    serial.writeValue("total_time", total_time)
    forever_stop = false
})
function setup() {
    let i: number;
    
    let forever_stop = true
    mea = 0
    std = 0
    total_time = 0
    // total time counting
    time_on = 0
    // time the light source is on
    // hour=bytearray(240)
    for (i = 0; i < 3000; i++) {
        quad[i] = 0
    }
    let ll = get_data_point()
    // ll=get_data_point()
    for (i = 0; i < 6; i++) {
        basic.showNumber(5 - i)
    }
    basic.clearScreen()
    // input.light_level()
    calc_stats(40, 200)
    // calculate the statistics for light on. 8 seconds
    if (std < 1) {
        std = 1
    }
    
    serial.writeString("mean=" + ("" + mea) + "  stdev=" + ("" + std) + "\n")
    basic.showIcon(IconNames.Yes)
    basic.pause(2000)
    basic.clearScreen()
    // input.light_level()
    forever_stop = false
}

// calculate statistics for a number of readings
// returns mean, stdev - no long term storage needed
// param: cnt - how many measurements to calculate
// param: dly - milliseconds btw measurements
function calc_stats(cnt: number, dly: number) {
    let Aprev: number;
    let thedata: number;
    
    //  for the algo see https://en.wikipedia.org/wiki/Standard_deviation#Rapid_calculation_methods
    let A = 0
    let Q = 0
    let k = 0
    // running k value. It's k=t+1 since k starts from 0.
    let n = cnt
    //  number of items
    let mean = 0
    for (let t = 0; t < n; t++) {
        k = t + 1
        Aprev = A
        thedata = get_data_point()
        // get next data point
        A = A + (thedata - A) / k
        Q = Q + (thedata - Aprev) * (thedata - A)
        mean += thedata
        basic.pause(dly)
    }
    let stdev = Math.sqrt(Q / (n - 1))
    // sample standard deviation
    mean /= n
    mea = mean
    std = Math.ceil(stdev)
}

// to apply to a different sensor just change the input
function get_data_point(): number {
    let ll = input.lightLevel()
    // print(str(ll))
    return ll
}

