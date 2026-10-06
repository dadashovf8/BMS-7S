# 3. Current measurement

Sheet 1, block "Current sense".

## 3.1 Circuit

| Ref | Part | Function |
|---|---|---|
| R2 | Vishay WSL3921, 1 mΩ 1 % 3 W | High-side shunt between BAT (CN1) and VBAT |
| U2 | TI INA239AIDGSR | 85 V, 16-bit SPI current, voltage, power and temperature monitor |
| C1 | 100 nF | VS bypass (3.3 V) |
| R5 | 10 kΩ to 3.3 V | ALERT pull-up (open drain, active low), routed to PB0 |
| R13 | 10 kΩ to 3.3 V | CS pull-up on PA4, keeps the device deselected while the MCU is in reset |

IN+ connects to BAT and IN− to VBAT. Discharge current reads positive, and charge current reads negative. VBUS sits on BAT, so the INA239 reports the battery voltage directly at the connector side of the shunt.

High-side sensing keeps the ground continuous between battery, board and pack. It also puts the board's own supply current (taken from VBAT) inside the measurement.

## 3.2 Range and resolution

| ADCRANGE | Shunt full scale | Current full scale | Shunt LSB | Current LSB |
|---|---|---|---|---|
| 0 | ±163.84 mV | ±163.8 A | 5 µV | 5 mA |
| 1 | ±40.96 mV | ±40.96 A | 1.25 µV | 1.25 mA |

Settings used with ADCRANGE = 1:

- CURRENT_LSB = 1.25 mA (≥ 40 A / 2^15)
- SHUNT_CAL = 819.2 × 10^6 × 1.25 × 10^-3 × 0.001 × 4 = **4096**

Error terms (INA239 maximums at 25 °C):

| Source | Value | As current |
|---|---|---|
| Offset | ±5 µV | ±5 mA |
| Gain | ±0.1 % | ±30 mA at 30 A |
| Shunt tolerance | ±1 % | ±300 mA at 30 A |

The shunt tolerance is the largest term. A one-point calibration against a reference meter takes it out.

## 3.3 Shunt

- At its 3 W rating the shunt carries 54.8 A continuous. At 30 A it dissipates 0.9 W.
- Copper in series with the shunt is not part of the measurement, provided the IN+ and IN− traces leave from the inner edges of the shunt pads as a Kelvin pair. With 1 oz copper at about 0.5 mΩ per square, a centimetre of 5 mm trace is already comparable to the shunt itself.
- VBUS input impedance is 1 MΩ in active mode.

## 3.4 Charge counting

The INA239 provides current, bus voltage, power and die temperature. Charge is integrated by the MCU:

```
Q[n] = Q[n-1] + I[n] · Δt
```

The RTC crystal (X2, 32.768 kHz) provides the time base.

## 3.5 ALERT

ALERT is configured on the shunt over-voltage (SOVL) and under-voltage (SUVL) thresholds:

- SOVL catches discharge overcurrent.
- SUVL catches charge overcurrent, because charge current makes the shunt voltage negative.

ALERT goes to an EXTI input, so the MCU reacts without polling. The fastest shunt conversion is 50 µs.
