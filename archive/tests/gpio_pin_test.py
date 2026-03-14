#!/usr/bin/env python3
import time
import lgpio

CHIP = 4           # you already use gpiochip4 for main GPIO
OUT_GPIO = 18      # pick a free GPIO
FREQ_HZ = 50       # start low
DUTY = 50          # percent

h = lgpio.gpiochip_open(CHIP)
try:
    lgpio.gpio_claim_output(h, OUT_GPIO, 0)
    lgpio.tx_pwm(h, OUT_GPIO, FREQ_HZ, DUTY)
    print(f"Square wave on GPIO{OUT_GPIO}: {FREQ_HZ} Hz, {DUTY}% duty. Ctrl+C to stop.")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    lgpio.tx_pwm(h, OUT_GPIO, 0, 0)  # stop PWM
    lgpio.gpio_write(h, OUT_GPIO, 0)
    lgpio.gpiochip_close(h)
