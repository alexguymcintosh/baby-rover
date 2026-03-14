# **PID Implementation** 
**Date:** 26-03-05

## Open loop

### **Data:** linear x = 0.3 on floor boards 
[1772703248.496831720] [motor_controller]: enc_a=0 enc_b=0
[INFO] [1772703249.497409729] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772703249.498087891] [motor_controller]: enc_a=451 enc_b=474
[INFO] [1772703250.497187064] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772703250.498063057] [motor_controller]: enc_a=922 enc_b=979
[INFO] [1772703251.497159828] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772703251.498055858] [motor_controller]: enc_a=1398 enc_b=1479
[INFO] [1772703252.497167985] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772703252.497882739] [motor_controller]: enc_a=1849 enc_b=1954
[INFO] [1772703253.497162371] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772703253.497967420] [motor_controller]: enc_a=2290 enc_b=2416
[INFO] [1772703254.497275575] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772703254.497956033] [motor_controller]: enc_a=2727 enc_b=2867
[INFO] [1772703255.497653579] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772703255.498389500] [motor_controller]: enc_a=3215 enc_b=3386
[INFO] [1772703256.497116744] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772703256.497903682] [motor_controller]: enc_a=3680 enc_b=3876
[INFO] [1772703257.497126299] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772703257.497924108] [motor_controller]: enc_a=4158 enc_b=4386
[INFO] [1772703258.497201896] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772703258.497969742] [motor_controller]: enc_a=4618 enc_b=4869
[INFO] [1772703259.497207222] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772703259.497934679] [motor_controller]: enc_a=5076 enc_b=5346
[INFO] [1772703260.497259701] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772703260.497964548] [motor_controller]: enc_a=5517 enc_b=5802


### **Interpretation**

- encoder B is consistently %5.2 faster 
- the rotio is the same for each time stamp therefore it is systematic ideal for PID

### **Decision**
- using differencial drive we can reduce the drift with a real time feedback look (PID)


## Closed loop 

- P = 0.01 | I = 0.005 | D = 0 
- P reacts to the current error only 
- I adds the current error to a running total every loop, continues to improve until it hold the right value 

### **method**
- PID tunable paramters inisalised outside of the class 
- PID variables inicalised in ___INIT___
- realtime updating indide publish_odem
- a and b normalised to encoder count values
- error = a - b
- dt = 0.02 as the PI runs at 50Hz 
- inegral max = 50 
- correction is subtracted to right and added to left 


### **Data:** linear x = 0.3 on floor boards
[INFO] [1772708947.214460076] [motor_controller]: correction=0.0262 integral=1.2400 error=2
[INFO] [1772708947.404585696] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772708947.405193285] [motor_controller]: enc_a=10865 enc_b=10806
[INFO] [1772708947.714356018] [motor_controller]: correction=0.0056 integral=1.1200 error=0
[INFO] [1772708948.214500181] [motor_controller]: correction=0.0048 integral=0.9600 error=0
[INFO] [1772708948.404998502] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772708948.405805960] [motor_controller]: enc_a=11390 enc_b=11338
[INFO] [1772708948.714465048] [motor_controller]: correction=0.0048 integral=0.9600 error=0
[INFO] [1772708949.214378211] [motor_controller]: correction=0.0047 integral=0.9400 error=0
[INFO] [1772708949.404709515] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772708949.405564491] [motor_controller]: enc_a=11901 enc_b=11857
[INFO] [1772708949.714493577] [motor_controller]: correction=0.0045 integral=0.9000 error=0
[INFO] [1772708950.214336110] [motor_controller]: correction=-0.0159 integral=0.8200 error=-2
[INFO] [1772708950.404678913] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772708950.405375798] [motor_controller]: enc_a=12425 enc_b=12384
[INFO] [1772708950.714337142] [motor_controller]: correction=-0.0063 integral=0.7400 error=-1
[INFO] [1772708951.214327914] [motor_controller]: correction=-0.0066 integral=0.6800 error=-1
[INFO] [1772708951.404724180] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772708951.405514675] [motor_controller]: enc_a=12935 enc_b=12903
[INFO] [1772708951.714291650] [motor_controller]: correction=-0.0068 integral=0.6400 error=-1
[INFO] [1772708952.214411069] [motor_controller]: correction=0.0029 integral=0.5800 error=0
[INFO] [1772708952.404622650] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772708952.405158609] [motor_controller]: enc_a=13454 enc_b=13428
[INFO] [1772708952.714425858] [motor_controller]: correction=0.0235 integral=0.7000 error=2
[INFO] [1772708953.214342685] [motor_controller]: correction=0.0041 integral=0.8200 error=0
[INFO] [1772708953.404970004] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772708953.405658500] [motor_controller]: enc_a=13959 enc_b=13920
[INFO] [1772708953.714336437] [motor_controller]: correction=-0.0055 integral=0.9000 error=-1
[INFO] [1772708954.214521539] [motor_controller]: correction=0.0051 integral=1.0200 error=0
[INFO] [1772708954.404735323] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772708954.405324301] [motor_controller]: enc_a=14496 enc_b=14448
[INFO] [1772708954.714318458] [motor_controller]: correction=-0.0056 integral=0.8800 error=-1
[INFO] [1772708955.214474560] [motor_controller]: correction=-0.0059 integral=0.8200 error=-1
[INFO] [1772708955.404760418] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772708955.405452969] [motor_controller]: enc_a=15016 enc_b=14974
[INFO] [1772708955.714415755] [motor_controller]: correction=0.0042 integral=0.8400 error=0
[INFO] [1772708956.214405376] [motor_controller]: correction=0.0040 integral=0.8000 error=0
[INFO] [1772708956.404665159] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772708956.405348618] [motor_controller]: enc_a=15540 enc_b=15502
[INFO] [1772708956.714371681] [motor_controller]: correction=0.0038 integral=0.7600 error=0
[INFO] [1772708957.214429708] [motor_controller]: correction=-0.0062 integral=0.7600 error=-1
[INFO] [1772708957.404575565] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772708957.405238784] [motor_controller]: enc_a=16074 enc_b=16035
[INFO] [1772708957.714472716] [motor_controller]: correction=0.0337 integral=0.7400 error=3
[INFO] [1772708958.214303335] [motor_controller]: correction=-0.0054 integral=0.9200 error=-1
[INFO] [1772708958.405063467] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772708958.405759000] [motor_controller]: enc_a=16602 enc_b=16612
[INFO] [1772708958.714481971] [motor_controller]: correction=0.0476 integral=-0.4800 error=5
[INFO] [1772708959.214326998] [motor_controller]: correction=-0.0005 integral=-0.1000 error=0
[INFO] [1772708959.404736576] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772708959.405348424] [motor_controller]: enc_a=17131 enc_b=17126
[INFO] [1772708959.714337727] [motor_controller]: correction=0.0220 integral=0.4000 error=2
[INFO] [1772708960.214266067] [motor_controller]: correction=-0.0151 integral=0.9800 error=-2
[INFO] [1772708960.404787329] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772708960.405620490] [motor_controller]: enc_a=17729 enc_b=17668
[INFO] [1772708960.714500534] [motor_controller]: correction=-0.0133 integral=1.3400 error=-2
[INFO] [1772708961.214445095] [motor_controller]: correction=-0.0108 integral=1.8400 error=-2
[INFO] [1772708961.404785932] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772708961.405564372] [motor_controller]: enc_a=18318 enc_b=18223
[INFO] [1772708961.714462767] [motor_controller]: correction=0.0096 integral=1.9200 error=0
[INFO] [1772708962.214318995] [motor_controller]: correction=-0.0101 integral=1.9800 error=-2
[INFO] [1772708962.405171106] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772708962.405834528] [motor_controller]: enc_a=18881 enc_b=18777
[INFO] [1772708962.714372258] [motor_controller]: correction=0.0211 integral=2.2200 error=1
[INFO] [1772708963.214339800] [motor_controller]: correction=0.0412 integral=2.2400 error=3
[INFO] [1772708963.405110485] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772708963.405834740] [motor_controller]: enc_a=19430 enc_b=19318
[INFO] [1772708963.714393877] [motor_controller]: correction=0.0110 integral=2.2000 error=0
[INFO] [1772708964.214372195] [motor_controller]: correction=0.0002 integral=2.0400 error=-1
[INFO] [1772708964.404709568] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772708964.405406712] [motor_controller]: enc_a=19934 enc_b=19828
[INFO] [1772708964.714360735] [motor_controller]: correction=0.0005 integral=2.1000 error=-1
[INFO] [1772708965.214307127] [motor_controller]: correction=-0.0093 integral=2.1400 error=-2
[INFO] [1772708965.404715258] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772708965.405426532] [motor_controller]: enc_a=20419 enc_b=20309
[INFO] [1772708965.714344277] [motor_controller]: correction=0.0106 integral=2.1200 error=0
[INFO] [1772708966.214336093] [motor_controller]: correction=0.0506 integral=2.1200 error=4
[INFO] [1772708966.404817910] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772708966.405463498] [motor_controller]: enc_a=20843 enc_b=20729
[INFO] [1772708966.714363317] [motor_controller]: correction=0.0016 integral=2.3200 error=-1
[INFO] [1772708967.214326688] [motor_controller]: correction=0.0413 integral=2.2600 error=3
[INFO] [1772708967.404636431] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772708967.405180465] [motor_controller]: enc_a=21254 enc_b=21140
[INFO] [1772708967.714357522] [motor_controller]: correction=0.0011 integral=2.2200 error=-1
[INFO] [1772708968.214282819] [motor_controller]: correction=0.0099 integral=1.9800 error=0
[INFO] [1772708968.406176738] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772708968.406971400] [motor_controller]: enc_a=21602 enc_b=21505
[INFO] [1772708968.714327893] [motor_controller]: correction=-0.0199 integral=2.0200 error=-3
[INFO] [1772708969.214339096] [motor_controller]: correction=0.0496 integral=1.9200 error=4
[INFO] [1772708969.404799023] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772708969.405687906] [motor_controller]: enc_a=21956 enc_b=21859
[INFO] [1772708969.714495391] [motor_controller]: correction=0.0195 integral=1.9000 error=1
[INFO] [1772708970.214585222] [motor_controller]: correction=0.0498 integral=1.9600 error=4
[INFO] [1772708970.404862742] [motor_controller]: cmd_vel: linear=0.30 angular=0.00
[INFO] [1772708970.405477665] [motor_controller]: enc_a=22289 enc_b=22193
[INFO] [1772708970.714356222] [motor_controller]: correction=0.0498 integral=1.9600 error=4
[INFO] [1772708971.214416146] [motor_controller]: correction=0.0001 integral=2.0200 error=-1
[INFO] [1772708971.404663110] [motor_controller]: cmd_vel: linear=0.30 angular=0.00

### **Interpretation**

- t = 10 variance = 1.005 (a is faster)
- t = 15 variance = 1.002 (a is faster)
- t = 20 variance = 1.005 (a is faster)

- Open loop → 5.2% drift. Closed loop PID → 0.5% drift. 10x improvement.

- The integral stabilised around 0.8-2.2 (PWM value (0-100)) — it found the correction offset and held it after 10 - 15 seconds at linear x = 3 which is super slow 

