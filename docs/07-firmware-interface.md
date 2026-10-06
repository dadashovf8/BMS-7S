# 7. Hardware / firmware interface

These are the hardware facts the firmware depends on: bus settings, device configuration and start-up order. The firmware itself was written by the software team.

## 7.1 Buses

| Bus | Device | Mode | Max clock | Frame |
|---|---|---|---|---|
| SPI1 | INA239 | Mode 1 (CPOL 0, CPHA 1). MOSI sampled on SCLK falling, MISO shifted on SCLK rising | 10 MHz | 6-bit address, '0', R/W (1 = read), then 16 or 24 data bits, MSB first |
| SPI2 | LTC6811-2 | Mode 3 (CPOL 1, CPHA 1). SDI latched on SCK rising, SDO valid after SCK falling | 1 MHz (t_CLK ≥ 1 µs) | 2-byte command + PEC15, data in 6-byte groups + PEC15 |
| USART1 | Host | 8N1 | - | - |

## 7.2 INA239 configuration

| Register | Addr | Setting | Reason |
|---|---|---|---|
| CONFIG | 0x00 | ADCRANGE = 1 | ±40.96 mV shunt range |
| ADC_CONFIG | 0x01 | Continuous shunt, bus and temperature conversion | Conversion time and averaging trade ALERT latency against noise |
| SHUNT_CAL | 0x02 | 4096 (0x1000) | CURRENT_LSB = 1.25 mA, R_SHUNT = 1 mΩ, ×4 for ADCRANGE = 1 |
| DIAG_ALRT | 0x0B | Alert latch on | Keeps an event until it is read |
| SOVL | 0x0C | Discharge current limit | ALERT on PB0 |
| SUVL | 0x0D | Charge current limit (negative shunt voltage) | ALERT on PB0 |
| MANUFACTURER_ID, DEVICE_ID | 0x3E, 0x3F | Read at boot | Bus check |

Scaling:

```
Current [A] = CURRENT × 1.25e-3
Power [W]   = POWER × 0.2 × 1.25e-3
Bus [V]     = VBUS × 3.125e-3
```

## 7.3 LTC6811-2 configuration

- **Address.** A0 – A3 are high, so the address is 15. Address commands set CMD0[7] = 1 and carry the address in CMD0[6:3]. Broadcast commands also reach the single device.
- **Wake-up.** Pulse CSB low and wait for the core to reach STANDBY before the first command.
- **Watchdog.** If no valid command arrives for 2 s, the configuration registers reset, so the configuration is rewritten every measurement cycle.
- **Cell mapping.** Cells 1 – 4 are C1V – C4V, and cells 5 – 7 are C7V – C9V. C5V, C6V and C10V – C12V read 0 V and are skipped.
- **Balance mapping.** Cells 1 – 4 are DCC1 – DCC4, and cells 5 – 7 are DCC7 – DCC9. DCTO sets the discharge timer.
- **Measurement sequence.** ADCV on C1/C7 only, wait 60 µs (6 × the 10 µs input filter constant), then ADCV on all cells, then RDCVA – RDCVD. DCP = 0.
- **Temperatures.** ADAX on GPIO1 – 3, then RDAUXA. The reference is VREF2 (3.0 V).

## 7.4 Start-up order

```
clock init
AFIO_MAPR.SWJ_CFG = 010                # SWD kept, PB3/PB4 released as GPIO
CHG_EN = DSG_EN = PCHG_EN = PMON_EN = 0
read INA239 IDs, write and read back LTC6811 config      # both buses alive
first measurement: cells, temperatures, current, stack voltage
CP_EN = 1
wait for charge pump (100 ms at 470 nF; C24 is 1 µF, allow 200 ms)
limits OK  -> DSG_EN = 1, CHG_EN = 1
otherwise  -> stay open, or PCHG_EN = 1 for precharge
```

Pack-terminal voltage, on demand:

```
PMON_EN = 1 -> settle -> ADC on PACKDIV -> PMON_EN = 0
V_PACK = V_ADC × 27.55   (×27.77 including R_PMON typ, or a calibrated factor)
```

## 7.5 Independent watchdog

Enable the IWDG early. It is clocked from the LSI, independent of the main clock. If the firmware stops, the MCU resets and runs the start-up order again, and that order opens all switches before anything else.
