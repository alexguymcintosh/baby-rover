# Encoder Diagnostic Tests
## Baby Rover — Encoder A Triple Count Investigation

**Problem:** Encoder A reads ~3x more pulses than Encoder B at the Pi despite both wheels travelling the same distance.

**Known facts:**
- Code is symmetrical — not the software
- Physical motor and encoder units swapped — problem persisted — not the hardware unit
- Rover drives physically straight — both wheels turning correctly

**Goal:** Isolate exactly where in the signal chain the triple counting is introduced.

**Signal chain:**
```
Encoder hardware → wire → Pi GPIO pin → gpiod kernel driver → Python count
```

---

## Test 1 — Raw Encoder Signal at Hardware Level

**Date: 26-03-03**

**What we tested:** Both encoder units outputting raw signal directly to logic analyzer. No Pi. No software. Motor power off. Hand spun each output wheel one full revolution.

**Result:** Both encoders confirmed 1050 PPR ✅

**Conclusion:** Encoder hardware is not the problem.

## Test 2 - Disconnected Channel B, only Channel A

**Date: 26-03-03**

**Result:** Problem persists - inaccuracy is exactly 2.5 consistently

**Conculsion:** This is not noice this systemic, the PI is reading the wrong count at the GPIO pin 

## Test 3 - PI GPIO pins test input readings

**Date: 26-03-03**

**Test:** read gpio directly to the terminal 

**Results:** inputs are both 1 and 0 

## Test 4 - measuring encoder count while odem is cmd_ve is running

**Date: 26-03-03**

**Test:** run cmd_ve with linear x = 0, there for motor power = 0

**Result:** encoder reads results correctly

## Test 5 - measuring encoder pulse when with logic analyzer while motor is running

**Date: 26-03-03**

**Test:**  measure encoder pulse count using logic analzyer while with motor power

**Result:** pulse count is correct 

## Test 6 - adding debounder 0.5 microseconds 

**Date: 26-03-03**

**Test:**  tested debounder limit by reducing it until while hand spining i got 1050 pulse per rev, at 0.6 is was 150 at 0.5 it was 1050

**Result:** exact same results. if it is noise spikes could be last longer than 0.5 micro seconds, debounding wont fix it if it is the problem. 

### **data:** 

[INFO] [1772507990.931279049] [motor_controller]: Motor controller starting...
[INFO] [1772507990.936473698] [motor_controller]: Motor controller ready.
[INFO] [1772507991.419894292] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772507991.420517769] [motor_controller]: enc_a=0 enc_b=0
[INFO] [1772507992.419828079] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772507992.420643055] [motor_controller]: enc_a=60 enc_b=192
[INFO] [1772507993.419731940] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772507993.420262491] [motor_controller]: enc_a=119 enc_b=370
[INFO] [1772507994.419730429] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772507994.420407664] [motor_controller]: enc_a=183 enc_b=566
[INFO] [1772507995.419667658] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772507995.420193728] [motor_controller]: enc_a=256 enc_b=771
[INFO] [1772507996.419746738] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772507996.420391066] [motor_controller]: enc_a=331 enc_b=990
[INFO] [1772507997.419677873] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772507997.420346757] [motor_controller]: enc_a=410 enc_b=1189
[INFO] [1772507998.419715971] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772507998.420356318] [motor_controller]: enc_a=477 enc_b=1392
[INFO] [1772507999.419720475] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772507999.420395248] [motor_controller]: enc_a=549 enc_b=1582
^CTraceback (most recent call last): 

## Test 7 testing encoder output with on 1 motor running vs both

### **data:** This data is both motors 

[INFO] [1772510036.048337610] [motor_controller]: cmd_vel: linear=0.10 angular=0.00

[INFO] [1772510036.048981772] [motor_controller]: enc_a=0 enc_b=0

[INFO] [1772510037.048383801] [motor_controller]: cmd_vel: linear=0.10 angular=0.00

[INFO] [1772510037.049061647] [motor_controller]: enc_a=554 enc_b=230

[INFO] [1772510038.048326196] [motor_controller]: cmd_vel: linear=0.10 angular=0.00

[INFO] [1772510038.048995098] [motor_controller]: enc_a=1119 enc_b=469

[INFO] [1772510039.048550293] [motor_controller]: cmd_vel: linear=0.10 angular=0.00

[INFO] [1772510039.049225454] [motor_controller]: enc_a=1682 enc_b=704

[INFO] [1772510040.048388226] [motor_controller]: cmd_vel: linear=0.10 angular=0.00

[INFO] [1772510040.049073332] [motor_controller]: enc_a=2233 enc_b=941

[INFO] [1772510041.048391751] [motor_controller]: cmd_vel: linear=0.10 angular=0.00

[INFO] [1772510041.049063820] [motor_controller]: enc_a=2795 enc_b=1177

[INFO] [1772510042.048464905] [motor_controller]: cmd_vel: linear=0.10 angular=0.00

[INFO] [1772510042.049309361] [motor_controller]: enc_a=3361 enc_b=1416

[INFO] [1772510043.048346468] [motor_controller]: cmd_vel: linear=0.10 angular=0.00

[INFO] [1772510043.049074555] [motor_controller]: enc_a=3928 enc_b=1651

[INFO] [1772510044.048680083] [motor_controller]: cmd_vel: linear=0.10 angular=0.00

[INFO] [1772510044.049395151] [motor_controller]: enc_a=4492 enc_b=1892

[INFO] [1772510045.048397610] [motor_controller]: cmd_vel: linear=0.10 angular=0.00

[INFO] [1772510045.049116938] [motor_controller]: enc_a=5062 enc_b=2129



this is just motor A
[INFO] [1772509992.048376269] [motor_controller]: cmd_vel: linear=0.10 angular=0.00

[INFO] [1772509992.048914005] [motor_controller]: enc_a=0 enc_b=0

[INFO] [1772509993.048397028] [motor_controller]: cmd_vel: linear=0.10 angular=0.00

[INFO] [1772509993.049034319] [motor_controller]: enc_a=644 enc_b=0

[INFO] [1772509994.048475288] [motor_controller]: cmd_vel: linear=0.10 angular=0.00

[INFO] [1772509994.049107986] [motor_controller]: enc_a=1285 enc_b=0

[INFO] [1772509995.048298197] [motor_controller]: cmd_vel: linear=0.10 angular=0.00

[INFO] [1772509995.048925229] [motor_controller]: enc_a=1940 enc_b=0

[INFO] [1772509996.048385253] [motor_controller]: cmd_vel: linear=0.10 angular=0.00

[INFO] [1772509996.049045359] [motor_controller]: enc_a=2584 enc_b=0

[INFO] [1772509997.048399458] [motor_controller]: cmd_vel: linear=0.10 angular=0.00

[INFO] [1772509997.049028619] [motor_controller]: enc_a=3235 enc_b=0

[INFO] [1772509998.048376570] [motor_controller]: cmd_vel: linear=0.10 angular=0.00

[INFO] [1772509998.049026639] [motor_controller]: enc_a=3880 enc_b=0

[INFO] [1772509999.048395756] [motor_controller]: cmd_vel: linear=0.10 angular=0.00

[INFO] [1772509999.049055362] [motor_controller]: enc_a=4527 enc_b=0

[INFO] [1772510000.048388554] [motor_controller]: cmd_vel: linear=0.10 angular=0.00

[INFO] [1772510000.049025105] [motor_controller]: enc_a=5172 enc_b=0

^CTraceback (most recent call last):

  File "/h
  



## Test 8 writing 50hz frequency to encoder A gpio pin 

**test:** produce a 50hz frequency with gpio 18, validated 50 hz requency with pulseview logic analzer ( tested, motor power off and on same result )

**result:** gpio pin successfully read the input

### **data:** 
[INFO] [1772516478.497331618] [motor_controller]: enc_a=20 enc_b=0
[INFO] [1772516479.496732193] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772516479.497373758] [motor_controller]: enc_a=70 enc_b=0
[INFO] [1772516480.496667901] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772516480.497298725] [motor_controller]: enc_a=120 enc_b=0
[INFO] [1772516481.496609453] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772516481.497247963] [motor_controller]: enc_a=170 enc_b=0
[INFO] [1772516482.496557183] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772516482.497090842] [motor_controller]: enc_a=220 enc_b=0
[INFO] [1772516483.496602256] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772516483.497227358] [motor_controller]: enc_a=270 enc_b=0
^CTraceback (most recent call last):

## Test 9 logic analyzer vs PI channel B encoder a and b 

**test** start logic analyzer count channel b for encoder a and b, start motor_controller.py - motor starts then compare the output of what pi sees vs what the logic controller sees.

**data:** motor_controller out put every 1 second so thats the range of error: pi a = 4269 b = 1387, logic counter a = 2318, b = 1450

**interpreation:** encoder b readings are constistent, the variation could be attributed to the motor controller time stamp range of 1 second. encoder a however logic view and pi do not see the same readings logic view is operating at 24Mhz this could be too slow and the pi is faster

## Test 10 low pass filter 1kohms and 100nF

**test** low pass filter on encoder a

### **data** 

linear x = 0.1

[INFO] [1772523689.743812847] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772523689.744436898] [motor_controller]: enc_a=0 enc_b=0
[INFO] [1772523690.743852865] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772523690.744462064] [motor_controller]: enc_a=249 enc_b=225
[INFO] [1772523691.743788363] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772523691.744271675] [motor_controller]: enc_a=519 enc_b=461
[INFO] [1772523692.743716620] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772523692.744527467] [motor_controller]: enc_a=782 enc_b=693
[INFO] [1772523693.743990466] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772523693.744644554] [motor_controller]: enc_a=1040 enc_b=927
[INFO] [1772523694.743825962] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772523694.744457328] [motor_controller]: enc_a=1302 enc_b=1161
[INFO] [1772523695.743830381] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772523695.744458303] [motor_controller]: enc_a=1566 enc_b=1393
[INFO] [1772523696.743729411] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772523696.744354184] [motor_controller]: enc_a=1824 enc_b=1627
[INFO] [1772523697.743779068] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772523697.744568618] [motor_controller]: enc_a=2075 enc_b=1858
[INFO] [1772523698.743737780] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772523698.744357313] [motor_controller]: enc_a=2338 enc_b=2091
[INFO] [1772523699.743901341] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772523699.744514596] [motor_controller]: enc_a=2590 enc_b=2323
[INFO] [1772523700.744068049] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772523700.744716767] [motor_controller]: enc_a=2848 enc_b=2555

linear x = 0.3

babyrover@babyrover:~/baby-rover$ python3 ~/baby-rover/nodes/motor_controller.py
[INFO] [1772523841.519766246] [motor_controller]: Motor controller starting...
[INFO] [1772523841.525059117] [motor_controller]: Motor controller ready.
[INFO] [1772523841.832641724] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772523841.833236923] [motor_controller]: enc_a=0 enc_b=0
[INFO] [1772523842.832715553] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772523842.833514363] [motor_controller]: enc_a=965 enc_b=710
[INFO] [1772523843.832572032] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772523843.833446544] [motor_controller]: enc_a=1951 enc_b=1443
[INFO] [1772523844.832626359] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772523844.833544168] [motor_controller]: enc_a=2917 enc_b=2167
[INFO] [1772523845.832475225] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772523845.833141720] [motor_controller]: enc_a=3905 enc_b=2897
[INFO] [1772523846.832814845] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772523846.833562803] [motor_controller]: enc_a=4870 enc_b=3623
[INFO] [1772523847.832640079] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772523847.833427444] [motor_controller]: enc_a=5893 enc_b=4353
[INFO] [1772523848.832650144] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772523848.833289066] [motor_controller]: enc_a=6885 enc_b=5082
[INFO] [1772523849.832562450] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772523849.833319074] [motor_controller]: enc_a=7853 enc_b=5813
[INFO] [1772523850.832624327] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772523850.833225286] [motor_controller]: enc_a=8833 enc_b=6538


### **interpretation**

linear x = 0.1 gap is almost closed 1.1 variation 
linear x = 0.3 gap is 1.35 this is probably because the noise increase as current increases. 

## test 11 low pass filter logic analzer channel a before and after resistor 

**results** before noise 1230 after 800 same sample time 

## test 12 low pass filter logic analzer channel a after resisitor, channel b no resistor

**results** channel a 2400 channel b 1300 same sample time 

## test 13 problem found wiring is noisy - rewired encoders away from motor power and problem solved 

### **data**
[INFO] [1772526622.569145510] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772526622.569789913] [motor_controller]: enc_a=0 enc_b=1
[INFO] [1772526623.569163473] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772526623.569814821] [motor_controller]: enc_a=213 enc_b=226
[INFO] [1772526624.569226970] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772526624.569897965] [motor_controller]: enc_a=437 enc_b=463
[INFO] [1772526625.569129927] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772526625.569900922] [motor_controller]: enc_a=652 enc_b=690
[INFO] [1772526626.569128695] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772526626.569777043] [motor_controller]: enc_a=875 enc_b=927
[INFO] [1772526627.569130867] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772526627.569908807] [motor_controller]: enc_a=1108 enc_b=1175
[INFO] [1772526628.569131407] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772526628.569773977] [motor_controller]: enc_a=1332 enc_b=1412
[INFO] [1772526629.569099795] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772526629.569741865] [motor_controller]: enc_a=1551 enc_b=1645
[INFO] [1772526630.569121494] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772526630.569764897] [motor_controller]: enc_a=1770 enc_b=1878
[INFO] [1772526631.569199912] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772526631.569843574] [motor_controller]: enc_a=1989 enc_b=2111
[INFO] [1772526632.569111142] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772526632.569768564] [motor_controller]: enc_a=2212 enc_b=2348
[INFO] [1772526633.569206831] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772526633.569858308] [motor_controller]: enc_a=2432 enc_b=2582
[INFO] [1772526634.569180980] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772526634.569828828] [motor_controller]: enc_a=2656 enc_b=2819
[INFO] [1772526635.569098756] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772526635.569752012] [motor_controller]: enc_a=2874 enc_b=3051
[INFO] [1772526636.569200898] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772526636.569888228] [motor_controller]: enc_a=3094 enc_b=3286

### **Interpretation** raio is 0.94 typical motor variance 

## test 14 does motor B produce EMF 

**test** holding the wired together does not change anything, and at no point i saw noice on pulse view for encoder b

## validation and rewiring 

### **data** 

wires seperated: 

[INFO] [1772532401.572496000] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772532401.573124851] [motor_controller]: enc_a=0 enc_b=1
[INFO] [1772532402.572762067] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772532402.573440009] [motor_controller]: enc_a=31 enc_b=34
[INFO] [1772532403.572577055] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772532403.573215964] [motor_controller]: enc_a=253 enc_b=271
[INFO] [1772532404.572657393] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772532404.573369595] [motor_controller]: enc_a=476 enc_b=510
[INFO] [1772532405.572487006] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772532405.573127898] [motor_controller]: enc_a=693 enc_b=742
[INFO] [1772532406.572586836] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772532406.573355111] [motor_controller]: enc_a=915 enc_b=980
[INFO] [1772532407.572498156] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772532407.573138309] [motor_controller]: enc_a=1137 enc_b=1216
[INFO] [1772532408.572481330] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772532408.573115835] [motor_controller]: enc_a=1362 enc_b=1456
[INFO] [1772532409.572806054] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772532409.573471763] [motor_controller]: enc_a=1582 enc_b=1691
[INFO] [1772532410.572616992] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772532410.573349069] [motor_controller]: enc_a=1808 enc_b=1931
[INFO] [1772532411.572536508] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772532411.573381007] [motor_controller]: enc_a=2025 enc_b=2164
[INFO] [1772532412.572489078] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772532412.573121403] [motor_controller]: enc_a=2251 enc_b=2405
[INFO] [1772532413.572477006] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772532413.573200457] [motor_controller]: enc_a=2473 enc_b=2641
[INFO] [1772532414.572556799] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772532414.573234142] [motor_controller]: enc_a=2698 enc_b=2881
[INFO] [1772532415.572468198] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772532415.573113524] [motor_controller]: enc_a=2915 enc_b=3113

wired together [INFO] [1772532493.390143003] [motor_controller]: Motor controller ready.
[INFO] [1772532493.572612995] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772532493.573244037] [motor_controller]: enc_a=0 enc_b=1
[INFO] [1772532494.572818102] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772532494.573505498] [motor_controller]: enc_a=694 enc_b=224
[INFO] [1772532495.572548525] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772532495.573343408] [motor_controller]: enc_a=1402 enc_b=457
[INFO] [1772532496.572631402] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772532496.573467602] [motor_controller]: enc_a=2112 enc_b=689
[INFO] [1772532497.572608525] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772532497.573402168] [motor_controller]: enc_a=2815 enc_b=921
[INFO] [1772532498.572553317] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772532498.573305996] [motor_controller]: enc_a=3523 enc_b=1152
[INFO] [1772532499.572661335] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772532499.573431052] [motor_controller]: enc_a=4228 enc_b=1385
[INFO] [1772532500.572627822] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772532500.573297090] [motor_controller]: enc_a=4940 enc_b=1616
[INFO] [1772532501.572768914] [motor_controller]: cmd_vel: linear=0.10 angular=0.00
[INFO] [1772532501.573422127] [motor_controller]: enc_a=5646 enc_b=1847
[INFO] [1772532502.572673163] [motor_controller]: cmd_vel: linear=0.10 angular=0.00


### **results:** Wires together x3 varience speperated 0.95 varience 

