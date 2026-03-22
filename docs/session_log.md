# Session Log

## 2026-02-23-20-00 - Alex

### What I worked on
- Installed ROS 2 Jazzy on ThinkPad (Ubuntu 24.04)
- Flashed Ubuntu 24.04 server onto Crucial BX500 SSD for Pi 5
- SSH confirmed working ThinkPad → Pi 5
- Installed ROS 2 Jazzy on Pi 5
- Confirmed talker/listener demo working on both machines
- Confirmed cross-machine ROS 2 communication working over WiFi via DDS
- Created baby-rover repo structure and pushed to GitHub
- Installed Claude Code, ROS, GitLens, Python extensions in Cursor

### What broke
- librealsense2-dkms failed on kernel 6.17 on ThinkPad — removed for now, not needed yet
- Network dropped mid apt upgrade — fixed with --fix-missing flag
- SSH host key conflict after reflash — fixed with ssh-keygen -R

### What's next
- Get IMU publishing to /imu/data on Pi 5
- Get motors responding to /cmd_vel via keyboard teleop
- Get encoders publishing to /odom

## 2026-02-24-09-35 - Alex 

### What was done
- Confirmed wiring from memory and documented in hardware.md
- Identified 10kΩ pulldowns on motor control pins as suspected curve cause
- Deferred motor curve troubleshooting to dedicated session

### Decisions made
- Motor A = Right, Motor B = Left
- Pulldowns to be removed before PID tuning begins

### Blockers / open issues
- hardware.md wiring not yet committed to group repo

### Next session
- Write motor_controller node

## 2026-02-24-10-20 - Alex 

### Updated README

## 2026-02-24-15-14 - Alex

### What was done
- Confirmed Cursor SSH workflow — editing files directly on Pi
- Installed lgpio on Pi 5
- Discovered Pi 5 uses gpiochip4 not gpiochip0
- Wrote motor_controller node — open loop, subscribes to /cmd_vel
- Confirmed ROS 2 pub/sub pipeline working
- Motors responding to /cmd_vel — both wheels spinning correct direction
- Measured wheel diameter = 44mm
- Encoder resolution: 7PPR × 150 gear ratio = 1050 PPR, 1 pulse = 0.1316mm
- Encoder callbacks broken in lgpio 0.2.0.0 on Pi 5 — switched to 100Hz polling via ROS 2 timer
- /odom publishing and incrementing correctly with wheel movement


### Decisions made
- Running nodes directly with Python for now — no colcon package yet
- nodes/ directory on Pi for scripts
- No sudo required — babyrover already in gpio, i2c, spi groups
- Encoder polling at 100Hz instead of interrupt-driven callbacks — lgpio bug, revisit on university rover

### Deferred
- 10kΩ pulldown troubleshooting — suspected curve cause, dedicated session
- colcon workspace setup — after all nodes working
- /odom accuracy tuning — y drift and angular.z oscillation confirm wheel mismatch, do not tune until pulldowns resolved

### Next session
- IMU node — MPU-6050 publishing to /imu/data

## 2026-02-24-17-00 - Alex

### What was done 
- Wired MPU-6050 via I2C — GPIO 2 (SDA), GPIO 3 (SCL)
- Confirmed i2cdetect shows 0x68
- Wrote imu_driver node — publishes to /imu/data at 100Hz
- Installed i2c-tools, mpu6050-raspberrypi, python3-smbus on Pi
- Created updated dependencies.md
- Updated hardware.md with motor/encoder specs for measuring movement
- Updated hardare.md with IMU wiring 

## 2026-02-24-17-43 - Alex 
- Updated disisions.md - ADR-001-(encoder reading polling vs interrupt-driven callbacks)
- README.md is compete and up to date

## 2026-02-24-19-25 - Alex

### What was done
- Built librealsense2 2.57.6 from source on Pi 5 ARM64
- Installed ros-jazzy-realsense2-camera ROS 2 wrapper
- RealSense D415 confirmed publishing on Pi 5 via USB 3.2
- Confirmed all 4 topics publishing simultaneously:
  - /odom ✅
  - /imu/data ✅
  - /camera/camera/depth/image_rect_raw ✅
  - /camera/camera/color/image_raw ✅
- Confirmed depth stream publishing at 29Hz via `ros2 topic hz`
- Milestone 2 complete
- Updated README
- Added milestones.md

### Decisions made
- RealSense uses realsense2_camera wrapper directly — no custom node needed
- Topic names have /camera/camera/ double prefix — wrapper default, documented in interface contract

### Deferred
- RealSense firmware update to 5.17.0.10 — not critical
- State machine — Milestone 3

### Milestone 2 status
- /cmd_vel → motors ✅
- /odom publishing ✅
- /imu/data publishing ✅
- /camera/depth publishing ✅

## 2026-03-03-21-50 - Alex

### what was done 
- drove the motro with teleop-twist-keyboard
- calculated 5% drift to the right
- measured wheel to wheel weidth 340mm from centre of track mark (tape measure)
- updated wheel base motor_contorller.py
- tested 100hz poll rate was too slow, increased to 1000hz could count slow hand turning but failed at practical speed
- installed gpiod-2.4.0 with  pip3 install gpiod --break-system-packages
- installed pulseview on ThinkPad -> for DIGISHUO 24Hz - 8 channel logic analyzer -> run with pulseview
- sudo apt install sigrok-firmware-fx2lafw for logic analyzer 
- Abandened polling - not sufficent for high frequencey encoder pulses
- implemented kernal interupts method - enc_b is accuracte, enc_a is 2.5 times larger consitently
- encoder_dianostic.md was created refer to for test procedure and truth 
- problem solved wires were carrying EMF spike from motor A, problem fixed with wire separation 


### observations
- wheel contact dirt mark curve around the wheel -> wheel needs alignment

### known problem 
- motor A produces EMF spikes - solution capacitor accorss motor power - and + and add a low pass filter. 
- motor B did not produce EMF 

### short term solution seperated the wires (worked)

## 2026-03-05-22-50 Alex

### what was done:
- implented added PID
- open loop 5% variance 
- closed loop -> P = 0.01 | I = 0.005 | Variance = 0.5% after 10 seconds - (linear x = 0.3)

## 2026-03-06-20-20 Alex

### Problem
Stalling noise when linear x = 0.0 on node startup.

### Explanation
`publish_odom` runs at 50Hz from the moment the node starts. Before any `cmd_vel` arrives `self.linear = 0.0` so it commands zero speed 50 times per second. The TB6612 in active brake mode holds both direction pins LOW with PWM at 0%, shorting the motor terminals together through the driver. The 1000Hz PWM carrier is still running at 0% duty cycle — motor coils are energised and de-energised at 1000Hz with zero net torque. That's the stalling noise.

### Solution
- Added `self.active = False` to `__init__`
- Added `self.active = True` to `cmd_vel_callback`
- Wrapped motor drive calls in `publish_odom` with:
```python
  if self.active and self.linear != 0.0:
      self.drive_motor_a(right)
      self.drive_motor_b(left)
  else:
      self.stop_motors()
```
Motors are now silent until the first `cmd_vel` arrives.

## 2026-03-08-21-10 Alex

### What was done
Ported the motor controller from Python to C++ and got it compiling and running as a proper ROS 2 colcon package.

The Python node (`nodes/motor_controller.py`) is retained and still functional. The C++ node is the new parallel implementation under `rover_control/src/motor_controller.cpp`. Both can be run independently — Python via `python3 nodes/motor_controller.py`, C++ via `ros2 run rover_control motor_controller`.

### Why C++
The C++ rewrite is intentional and for learning purposes. PID is a well-understood, bounded problem — it makes a good first C++ implementation because the logic is simple enough that the language itself is the challenge. The goal is to build programming fundamentals from the hardware side up, not abstract theory down. The `computePID()` function is deliberately left as a stub to be implemented by hand tomorrow after working through the control theory.

### Package structure created
A proper ROS 2 colcon package `rover_control` was created inside the repo:
```
baby-rover/
  rover_control/
    src/
      motor_controller.cpp   ← C++ node
    CMakeLists.txt
    package.xml
  nodes/
    motor_controller.py      ← Python node (retained)
```

### Problems encountered and fixed

**Problem 1 — broken dpkg**
`python3-colcon-ros` was in a broken state due to missing `python3-catkin-pkg` dependency. Fixed by removing the broken package and installing colcon via pip:
```bash
sudo dpkg --remove --force-depends python3-colcon-ros
pip3 install colcon-common-extensions --break-system-packages
```

**Problem 2 — gpiod API version mismatch**
The C++ file was written using the gpiod v2 C++ API (`gpiod::line_settings`, `request_lines`, `wait_edge_events`). The system only has gpiod v1.6.3 installed (`libgpiod-dev`). v2 is not available in the Ubuntu 24.04 apt repos.

Fixed by rewriting the encoder section to use the gpiod v1 C API:
- `gpiod_chip_open()` to open the chip
- `gpiod_chip_get_line()` to get line handles
- `gpiod_line_request_rising_edge_events()` to configure interrupt detection
- `gpiod_line_event_wait()` / `gpiod_line_event_read()` in background threads

**Problem 3 — wrong destructor call**
`lgpio_close()` does not exist in lgpio. Correct function is `lgGpiochipClose()`. Fixed with sed.

### Current state
- C++ node compiles clean (two warnings on empty `computePID()` stub — expected and intentional)
- Node runs and subscribes to `/cmd_vel`, publishes to `/odom`
- PID gains are all 0.0 — node runs open-loop until `computePID()` is implemented
- Motors respond to `ros2 topic pub /cmd_vel` commands
- Encoder counting confirmed working via background threads

### Next session
Implement `computePID()` in C++. The function signature, struct, and comments are already in place — only the three PID terms need to be written. Set gains to the known-working Python values (KP=0.01, KI=0.005, KD=0) once implemented and verify closed-loop behaviour matches the Python node.

## 2026-03-10-15-20 - Alex - VSCode Debugger Setup for C++ ROS 2 Node

### Directory changes
- created new file structure containing project_management directory for all arcitecture and dicision based documents


### Goal
Get VSCode's C++ debugger working for `motor_controller.cpp` running on the Pi 5 via Remote-SSH, so breakpoints and variable inspection work during hardware testing.

### Context
- Development machine: ThinkPad running Ubuntu 24.04
- Target machine: Raspberry Pi 5 (babyrover@10.0.0.76)
- VSCode connected to Pi via Remote-SSH extension
- C++ node built with colcon inside `~/baby-rover/rover_control/`

---

### What was broken and why

**Problem 1 — wrong build system**
VSCode auto-generated a `tasks.json` that used `g++ build active file` — plain g++ with no knowledge of ROS 2 headers or dependencies. This produced:
```
fatal error: rclcpp/rclcpp.hpp: No such file or directory
```
Plain g++ cannot build a ROS 2 node. Colcon must be used.

**Problem 2 — no debug symbols**
The default colcon build does not include debug symbols. Without them the debugger cannot map the running binary back to source code lines, so breakpoints show:
```
Module containing this breakpoint has not yet been loaded
```

**Problem 3 — wrong binary path in launch.json**
The initial `launch.json` pointed at `install/rover_control/lib/rover_control/motor_controller` — the colcon install path. Once CMake build was configured instead, the binary moved to `build/motor_controller`. Mismatched path = debugger attaches to nothing.

**Problem 4 — ninja not installed**
CMake tried to use ninja as its build backend and failed silently. Fixed with `sudo apt install ninja-build`.

---

### The fix — step by step

**Step 1 — Install dependencies on Pi**
```bash
sudo apt install gdb
sudo apt install ninja-build
```

**Step 2 — Configure CMake in VSCode**
`Ctrl+Shift+P` → `CMake: Select a Kit` → select `GCC aarch64-linux-gnu`

This tells CMake which compiler to use and configures the build for the Pi's architecture. CMake then configures automatically and writes build files to `~/baby-rover/build/`.

**Step 3 — Add debug symbols to CMakeLists.txt**
In `~/baby-rover/rover_control/CMakeLists.txt`, add after `project(rover_control)`:
```cmake
set(CMAKE_BUILD_TYPE Debug)
```
This tells the compiler to include debug symbols in the binary. Without this, breakpoints do not work.

**Step 4 — Replace tasks.json**
Location: `~/baby-rover/.vscode/tasks.json`

Replace the auto-generated g++ task with a colcon build task:
```json
{
    "tasks": [
        {
            "label": "colcon build rover_control",
            "type": "shell",
            "command": "cd ~/baby-rover && colcon build --packages-select rover_control",
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "problemMatcher": []
        }
    ],
    "version": "2.0.0"
}
```

Note: CMake build (`Ctrl+Shift+P` → `CMake: Build`) is used for the debug binary because it puts the binary at `~/baby-rover/build/motor_controller` with debug symbols. Colcon build is kept in tasks.json for deployment builds via `ros2 run`.

**Step 5 — Create launch.json**
Location: `~/baby-rover/.vscode/launch.json`

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug motor_controller",
            "type": "cppdbg",
            "request": "launch",
            "program": "/home/babyrover/baby-rover/build/motor_controller",
            "args": [],
            "stopAtEntry": false,
            "cwd": "/home/babyrover/baby-rover",
            "environment": [],
            "externalConsole": false,
            "MIMode": "gdb",
            "setupCommands": [
                {
                    "description": "Enable pretty printing",
                    "text": "-enable-pretty-printing"
                }
            ]
        }
    ]
}
```

**Step 6 — Build and launch**
1. `Ctrl+Shift+P` → `CMake: Build` — builds with debug symbols into `build/`
2. Open Run and Debug panel (left sidebar, bug+play icon)
3. Select "Debug motor_controller" from dropdown
4. Click green play button
5. Set breakpoints by clicking left margin next to any line — red dot appears
6. Breakpoint will halt execution and show all variables in the left panel

---

### Two build paths — understand the difference

| | CMake Build | Colcon Build |
|---|---|---|
| Command | `CMake: Build` in VSCode | `colcon build --packages-select rover_control` |
| Output location | `~/baby-rover/build/motor_controller` | `~/baby-rover/install/rover_control/lib/rover_control/motor_controller` |
| Debug symbols | Yes (CMAKE_BUILD_TYPE=Debug) | No by default |
| Used for | Debugging in VSCode | Running with `ros2 run` |
| ROS 2 environment | Not needed | Needs `source install/setup.bash` |

Use CMake build when debugging. Use colcon build when deploying and running as a ROS 2 node.

---

### IntelliSense squiggles (cosmetic only)
Red underlines on `#include <rclcpp/rclcpp.hpp>` in VSCode are IntelliSense failing to find headers — not a real error. Fixed by creating `.vscode/c_cpp_properties.json`:
```json
{
    "configurations": [
        {
            "name": "Linux",
            "includePath": [
                "${workspaceFolder}/**",
                "/opt/ros/jazzy/include/**"
            ],
            "compilerPath": "/usr/bin/g++",
            "cppStandard": "c++17"
        }
    ],
    "version": 4
}
```
This does not affect building or running — purely cosmetic fix for IDE experience.

## 2026-03-10-18-45 - Alex - moved logic analyzer x4 traces data to python enviroment on thinkpad


### Creating Python analzer Pipeline data transfer system
- use 4 channels to record enocoder signal at 100kHz
- removed row 1 from data
- added time stamp 1/100000 seconds per pulseview reading
- added gitignore:
analysis/data/
*.csv
*.bag

### How to use
- record data using logic analzer file on parent server (ThinkPad) 
- sync Pi and ThinkPad using: rsync -av babyrover@10.0.0.76:~/baby-rover/ ~/01_projects/baby-rover/
- analyis data on ThinkPad 
- commit or sync back to Pi any changes use: rsync -av --exclude='analysis/data/' ~/01_projects/baby-rover/ babyrover@10.0.0.76:~/baby-rover/
- Note make sure not to send large data files to Pi refer above 

### Dependencies:
- pip3 install pandas --break-system-packages
- sudo apt install python3-pip

## 2026-03-12-23-00     Alex - Encoder Hardware/Software Interface Ground Truth 

### Refer:
- hardware_software_interface/encoder.md

### Description
Mapping the encoder signal chain from physical pulse to software variable using 
three validation layers: PulseView (hardware ground truth), VSCode debugger 
(software state inspection), and printf (live runtime behaviour).
Goal: establish ground truth of what the software sees at each layer before 
writing any control logic on top of it.


### Test 1: watchEncoder — Thread Independence
**Goal:** Confirm each encoder runs on an independent kernel thread and cannot
be triggered by the other motor.

### Test 2: Cumulative Count — Both Motors, Velocity Estimation
**Goal:** Confirm both enc_a and enc_b accumulate correctly and extract 
first real velocity data for each motor independently.

### Test 3: Delta Per Tick — Control Loop Resolution
**Goal:** See exactly what the PID receives every 20ms — pulses per tick
for each motor independently at constant speed.

### Test 4: PWM Duty Cycle
**Goal:** Confirm the duty cycle value sent to hardware matches the 
expected scaling from cmd_vel.

## Test 5: Direction Pins — TB6612 Truth Table
**Goal:** Confirm AIN1/AIN2 logic matches TB6612 forward/backward truth table.

### What I learnt

#### Encoder Software — Hardware Interface
- Each encoder runs on independent kernel thread blocking on its own GPIO file descriptor
- Thread wakes only when kernel delivers interrupt on its specific pin — zero CPU when idle
- `enc_a_count_` is atomic — CPU-level instruction guarantees no corrupt reads between threads
- `delta_a` = pulses in last 20ms tick = what the PID sees every cycle
- At linear=0.3: delta_a=13-14 per tick → ~0.088 m/s per motor
- Motor B runs 2.9% faster than motor A open loop — confirmed systematic bias, not noise

#### PWM and Direction — Hardware Interface  
- PWM frequency fixed at 1000Hz. Duty cycle = % of time signal is ON
- linear=0.3 → duty=30% → motor feels 30% of supply voltage
- Formula: duty = speed × MAX_SPEED (100)
- lgTxPwm() programs Pi hardware PWM peripheral — runs in silicon independently of code
- AIN1=1, AIN2=0 → forward. AIN1=0, AIN2=1 → backward — confirmed against TB6612 truth table
- Direction and speed are independent: AIN pins set direction, PWM pin sets magnitude

2026-03-13- Alex PulesView tests

## 2026-03-14-18-27 Alex (Claude)

### What was done
- Created `analysis/pulseview_edge_count.py`
  - Loads a PulseView CSV from a command line argument path
  - Skips first row (header: "logic, logic, logic, logic")
  - Names columns: enA_trA, enA_trB, enB_trA, enB_trB
  - Counts rising edges (0→1 transitions) on enA_trA
  - Prints total count only — no plotting, no extra output

### Usage
```
python3 analysis/pulseview_edge_count.py path/to/export.csv
```

### What's next
- Run against PulseView exports to validate encoder pulse counts against hardware ground truth in `docs/hardware_software_interface/encoder.md`

## 2026-03-14-17-40 Alex (Claude)

### What was done
- Full project directory inventory: every file and directory catalogued with purpose, active status, and ROS 2 build-required status
- Reorganised project directory structure:
  - Created `archive/` at root level
  - Moved inactive/stub directories into `archive/`: `brainstorm/`, `config/`, `launch/`, `tests/`, `docs/project_management/`, `docs/features_implmentation/`, `nodes/`
  - Renamed `docs/debugging_diagnoses/` → `docs/diagnostics/`
  - Deleted stale duplicate: `nodes/motor_controller.cpp`
  - Deleted lgpio OS pipe artefact: `.lgd-nfy0`
  - Deleted build log artefacts: `log/`
- `rover_control/` left completely untouched — colcon build unaffected

### Decisions made
- `nodes/` archived rather than deleted — `imu_driver.py` and `motor_controller.py` retained as reference
- `build/` and `install/` left in place (regenerated by colcon, not worth deleting)
- `log/` deleted (50+ build logs, fully regenerable, no reference value)

### What's next
- Implement launch file (`archive/launch/baby_rover.launch.py` → promote when ready)
- Tune PID in `rover_control/src/motor_controller.cpp` (computePID() currently returns 0.0)
- Port `nodes/imu_driver.py` into the ament_cmake package

## 2026-03-18-20-00 Alex — PulseView Validation Tests (Claude)

### What was done
- Ran PV Test 1: software count vs hardware pulse count for both motors
- Built `analysis/pulseview_edge_count.py` — counts rising edges on all 4 traces
- Validated at linear=1.0 at 100kHz and 1MHz sample rates
- Motor B: exact match at both rates. Motor A: 0.2% error at 100kHz, 0.08% at 1MHz
- At operating speed linear=0.3 counts were spot on — software counting confirmed accurate
- PV Test 2 (direction) closed — refer encoder hardware analysis, confirmed in Google Docs
- Saved PulseView sessions as .sr + .csv to: `/home/mantis/01_projects/analysis/baby-rover/encoders/edge_count/`

### Pending
- PV Test 3: delta per tick vs hardware pulse spacing — not yet done, not blocking

### What's next
- computePID() implementation

## 2026-03-21-13-53 — Alex (Claude)

### What was done
- Implemented computePID() — P, I, D terms with windup clamp
- Restructured timerCallback() for independent per-motor PID
- Error computed in pulse count units — no unit mismatch
- Motor B trim applied: MOTOR_B_TRIM = 0.971
- Validated open loop baseline: err stable ~36/34, pwm locked at 0.2952/0.2867
- Validated closed loop alive: KP=0.001, pwm responding to error, jumped to ~0.331
- Refer: docs/hardware_software_interface/pid.md

### What's next
- Python analysis

## 2026-03-22-11-00 — Alex (Claude)

### What was done
- Built analysis/plot_pid_response.py — loads ROS bag, plots motor A and B 
  velocity independently vs cmd_vel, error subplot
- Fixed unit mismatch: cmd_vel converted from PWM to m/s (× 0.2933)
- Individual motor velocities extracted from /odom using wheel base geometry
- Captured step response at KP=0.001, KI=KD=0.0 — closed loop confirmed clean
- Refer: docs/hardware_software_interface/pid_velocity_response.md

### What's next
- simulation plant

## 2026-03-23-10-54 — Alex (Claude)

### What was done
- Built analysis/plot_pid_response.py — ROS bag loader, plots motor A and B
  velocity vs cmd_vel, error subplot. Fixed unit mismatch, added individual
  motor extraction from odom using wheel base geometry
- Built analysis/identify_plant.py — scipy curve fit for first order transfer
  function. Abandoned — motor too fast for 50Hz odom to capture transient
- Fixed odom drift at startup — last_enc reset on first cmd_vel in cmdVelCallback
- Tuned PID to KP=0.001, KI=0.0005, KD=0.0
- Validated: steady state error ±0.010 m/s, no bias, motors matched
- Refer: docs/hardware_software_interface/pid_velocity_response.md

### Decisions
- MATLAB abandoned for Linux — use Python scipy only
- Plant ID abandoned — empirical tuning faster and sufficient for this system
- PID declared done — good enough for rover platform, move to drone