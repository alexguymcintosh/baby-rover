# Encoder Hardware/Software Interface

## Description
Mapping the encoder signal chain from physical pulse to software variable using 
three validation layers: PulseView (hardware ground truth), VSCode debugger 
(software state inspection), and printf (live runtime behaviour).
Goal: establish ground truth of what the software sees at each layer before 
writing any control logic on top of it.

## Standard Test Conditions
- Rover elevated off ground, wheels free-spinning, no load
- cmd_vel: linear=0.3, angular=0.0, continuous publish
- Motors at operating temperature (allow 10s warmup before recording)
- Minimum sample duration: 20 samples (~10 seconds at 500ms print interval)
- All tests use single-channel rising edge only (1x resolution baseline)
- Validation layers used noted per test

---

## Test 1: watchEncoder — Thread Independence
**Goal:** Confirm each encoder runs on an independent kernel thread and cannot
be triggered by the other motor.

**Validation layers:** VSCode debugger

**Method:** Breakpoint on `count++` in `watchEncoder()`. Spin motor A and 
motor B independently by hand.

**Result:**
- Thread 7988 → motor A (GPIO 21) exclusively
- Thread 7989 → motor B (GPIO 24) exclusively
- Zero cross-triggers observed

**Conclusion:** Encoder interrupts are fully independent at the kernel level.
Each thread blocks on its own file descriptor and only wakes on its own GPIO event.

---

## Test 2: Cumulative Count — Both Motors, Velocity Estimation
**Goal:** Confirm both enc_a and enc_b accumulate correctly and extract 
first real velocity data for each motor independently.

**Validation layers:** printf

**Conditions:** Standard. Print interval 500ms (25 ticks × 20ms).

**Code:**
```cpp
RCLCPP_INFO(get_logger(), "enc_a=%d enc_b=%d", 
            enc_a_count_.load(), enc_b_count_.load());
```

**Raw data (22 samples, ~11 seconds):**

| Sample | Time (s) | enc_a | enc_b | delta_a | delta_b | persample
|--------|----------|-------|-------|---------|---------|
| 1      | 0.0      | 1     | 1     | —       | —       |
| 2      | 0.5      | 168   | 172   | 167     | 171     |
| 3      | 1.0      | 506   | 518   | 338     | 346     |
| 4      | 1.5      | 844   | 864   | 338     | 346     |
| 5      | 2.0      | 1182  | 1211  | 338     | 347     |
| 6      | 2.5      | 1520  | 1558  | 338     | 347     |
| 7      | 3.0      | 1857  | 1904  | 337     | 346     |
| 8      | 3.5      | 2195  | 2249  | 338     | 345     |
| 9      | 4.0      | 2532  | 2595  | 337     | 346     |
| 10     | 4.5      | 2869  | 2941  | 337     | 346     |
| 11     | 5.0      | 3207  | 3287  | 338     | 346     |
| 12     | 5.5      | 3544  | 3633  | 337     | 346     |
| 13     | 6.0      | 3880  | 3978  | 336     | 345     |
| 14     | 6.5      | 4217  | 4324  | 337     | 346     |
| 15     | 7.0      | 4554  | 4670  | 337     | 346     |
| 16     | 7.5      | 4891  | 5016  | 337     | 346     |
| 17     | 8.0      | 5226  | 5361  | 335     | 345     |
| 18     | 8.5      | 5562  | 5706  | 336     | 345     |
| 19     | 9.0      | 5897  | 6051  | 335     | 345     |
| 20     | 9.5      | 6232  | 6397  | 335     | 346     |

**Analysis:**
- enc_a average delta per 500ms: 336 pulses
- enc_b average delta per 500ms: 346 pulses
- enc_b runs 2.9% faster than enc_a open loop
- enc_a velocity: 336/500ms = 672 pulses/s → 0.64 rev/s → 0.088 m/s
- enc_b velocity: 346/500ms = 692 pulses/s → 0.659 rev/s → 0.091 m/s

**Key finding:** Motor B runs consistently 2.9% faster than motor A at 
identical PWM input. This is the systematic bias the I-term must correct.
Consistent across all 22 samples — not noise, physical motor variance.

**Pending validation:** Software count vs PulseView pulse count not yet 
compared. Do not treat velocity numbers as ground truth until validated.

---

## Test 3: Delta Per Tick — Control Loop Resolution
**Goal:** See exactly what the PID receives every 20ms — pulses per tick
for each motor independently at constant speed.

**Validation layers:** printf

**Conditions:** Standard. Print interval 500ms (25 ticks × 20ms).
Note: each printed delta is the sum of 25 ticks, not a single tick.

**Code:**
```cpp
RCLCPP_INFO(get_logger(), "delta_a=%d delta_b=%d", delta_a, delta_b);
```

**Raw data (20 samples, ~10 seconds):**

| Sample | Time (s) | delta_a | delta_b |
|--------|----------|---------|---------|
| 1      | 0.0      | 0       | 0       |
| 2      | 0.5      | 13      | 14      |
| 3      | 1.0      | 13      | 13      |
| 4      | 1.5      | 14      | 14      |
| 5      | 2.0      | 13      | 13      |
| 6      | 2.5      | 14      | 14      |
| 7      | 3.0      | 14      | 14      |
| 8      | 3.5      | 13      | 14      |
| 9      | 4.0      | 13      | 14      |
| 10     | 4.5      | 13      | 14      |
| 11     | 5.0      | 14      | 13      |
| 12     | 5.5      | 14      | 14      |
| 13     | 6.0      | 13      | 14      |
| 14     | 6.5      | 13      | 14      |
| 15     | 7.0      | 13      | 14      |
| 16     | 7.5      | 13      | 14      |
| 17     | 8.0      | 14      | 14      |
| 18     | 8.5      | 14      | 13      |
| 19     | 9.0      | 13      | 14      |
| 20     | 9.5      | 13      | 13      |

**Analysis:**
- delta_a: 13-14 pulses per 500ms print, ~0.52-0.56 pulses per tick
- delta_b: 13-14 pulses per 500ms print, ~0.52-0.56 pulses per tick
- Motors appear matched at this print resolution

**Key finding:** Print interval is 500ms = 25 ticks. Each printed delta
is accumulated over 25 ticks, not one. At this speed the PID sees
approximately 0-1 pulse per individual 20ms tick — at the resolution
limit of single-channel counting. This is why 4x quadrature resolution
matters — it would give 2-4 pulses per tick instead of 0-1, giving
the PID meaningful feedback every tick instead of mostly zeros.

**Debugger validation:**
Breakpoint on line after delta_a assignment. Motors disconnected, wheel 
spun by hand. Observed: delta_a=0 at rest, delta_a=16 during spin momentum, 
delta_a=0 when stopped. Confirms delta_a correctly measures pulses per 
20ms tick. Zero noise at rest — no phantom counts.

**Single tick validation (% 1):**
Printed every 20ms tick. Result: delta_a=13-14, delta_b=13-14 per tick 
consistently. Confirms each individual 20ms tick produces 13-14 pulses 
at linear=0.3 — not an accumulated value. Timer firing at exactly 20ms 
confirmed by timestamp spacing (~20ms between lines).

**Pending:** 
- Validate against PulseView
- Compare to Test 2 cumulative numbers for consistency

## Test 4: PWM Duty Cycle
**Goal:** Confirm the duty cycle value sent to hardware matches the 
expected scaling from cmd_vel.

**Validation layers:** printf, debugger

**Conditions:** Standard. Print inside driveMotorA() before lgTxPwm() call.

**Code:**
```cpp
RCLCPP_INFO(get_logger(), "duty_a=%.2f", duty);
```

**Result:**
- linear=0.3 → duty=30.0
- linear=0.1 → duty=10.0
- Formula confirmed: duty = speed × MAX_SPEED (100)

**Conclusion:** PWM scaling is linear and correct. Hardware receives 
exact duty cycle calculated from cmd_vel.

---

## Test 5: Direction Pins — TB6612 Truth Table
**Goal:** Confirm AIN1/AIN2 logic matches TB6612 forward/backward truth table.

**Validation layers:** printf

**Code:**
```cpp
RCLCPP_INFO(get_logger(), "AIN1=%d AIN2=%d duty=%.1f",
    lgGpioRead(chip_, AIN1), lgGpioRead(chip_, AIN2), duty);
```

**Result:**

| Direction | AIN1 | AIN2 | duty |
|-----------|------|------|------|
| Forward   | 1    | 0    | 10.0 |
| Backward  | 0    | 1    | 10.0 |

**Conclusion:** Direction pin logic confirmed correct. Matches TB6612 
truth table exactly. AIN1/AIN2 set direction, PWM pin sets speed — 
fully independent as designed.


## Encoder Software — Hardware Interface
- Each encoder runs on independent kernel thread blocking on its own GPIO file descriptor
- Thread wakes only when kernel delivers interrupt on its specific pin — zero CPU when idle
- `enc_a_count_` is atomic — CPU-level instruction guarantees no corrupt reads between threads
- `delta_a` = pulses in last 20ms tick = what the PID sees every cycle
- At linear=0.3: delta_a=13-14 per tick → ~0.088 m/s per motor
- Motor B runs 2.9% faster than motor A open loop — confirmed systematic bias, not noise

## PWM and Direction — Hardware Interface  
- PWM frequency fixed at 1000Hz. Duty cycle = % of time signal is ON
- linear=0.3 → duty=30% → motor feels 30% of supply voltage
- Formula: duty = speed × MAX_SPEED (100)
- lgTxPwm() programs Pi hardware PWM peripheral — runs in silicon independently of code
- AIN1=1, AIN2=0 → forward. AIN1=0, AIN2=1 → backward — confirmed against TB6612 truth table
- Direction and speed are independent: AIN pins set direction, PWM pin sets magnitude
