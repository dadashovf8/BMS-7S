# 6. MCU

Sheet 2. U5 is an STM32F103C8T6TR: Cortex-M3, 72 MHz, 64 KB flash, 20 KB RAM, LQFP48.

## 6.1 Pin map

| Pin | Port | Net | Connected to |
|---|---|---|---|
| 14 | PA4 | SPI1_NSS | INA239 CS, R13 10 kΩ pull-up |
| 15 | PA5 | SPI1_SCK | INA239 SCLK |
| 16 | PA6 | SPI1_MISO | INA239 MISO |
| 17 | PA7 | SPI1_MOSI | INA239 MOSI |
| 25 | PB12 | SPI2_NSS | LTC6811 CSB, R16 10 kΩ pull-up |
| 26 | PB13 | SPI2_SCK | LTC6811 SCK |
| 27 | PB14 | SPI2_MOSI | LTC6811 SDI |
| 28 | PB15 | SPI2_MISO | LTC6811 SDO, R31 10 kΩ pull-up |
| 18 | PB0 | ALERT | INA239 ALERT |
| 19 | PB1 | PG | LMR33630 power good |
| 39 | PB3 | PACKDIV | BQ76200 pack-voltage divider |
| 40 | PB4 | CHG_EN | BQ76200 |
| 41 | PB5 | CP_EN | BQ76200 |
| 42 | PB6 | DSG_EN | BQ76200 |
| 43 | PB7 | PMON_EN | BQ76200 |
| 45 | PB8 | PCHG_EN | BQ76200 |
| 30 | PA9 | USART1_TX | CN4 |
| 31 | PA10 | USART1_RX | CN4 |
| 34 | PA13 | SWDIO | CN3 |
| 37 | PA14 | SWCLK | CN3 |
| 3, 4 | PC14, PC15 | OSC32_IN/OUT | X2, 32.768 kHz |
| 5, 6 | PD0, PD1 | OSC_IN/OUT | 8 MHz crystal |
| 7 | NRST | NRST | Reset button, C30 |
| 44 | BOOT0 | BOOT0 | R30 to GND, boot button to 3.3 V |

Spare: PA0 – PA3, PA8, PA11, PA12, PA15, PB9 – PB11, PC13.

The two SPI buses are separate: the current monitor (SPI1, up to 10 MHz) and the cell monitor (SPI2, up to 1 MHz) can run at their own clock rates and modes without reconfiguring a shared bus.

PB3 and PB4 are JTAG pins after reset (JTDO, NJTRST). Firmware releases them by setting AFIO_MAPR.SWJ_CFG = 010, which keeps SWD and frees the JTAG-only pins.

## 6.2 Supply pins

| Pin | Net | Decoupling |
|---|---|---|
| VDD_1/2/3 (24, 36, 48) | 3.3 V | 100 nF each (C16 – C20) + C21 10 µF |
| VDDA (9) | 3.3 V | 100 nF |
| VSSA, VSS_1/2/3 | GND | |
| VBAT (1) | 3.3 V | |

On the 48-pin package, VREF+ is tied internally to VDDA. VREFINT (ADC channel 17) gives a run-time measurement of the actual reference.

## 6.3 Clocks

| Ref | Part | CL | Load caps |
|---|---|---|---|
| 8 MHz | Abracon ABM3-8.000MHZ-D2Y-T | 18 pF | C26/C27 30 pF C0G |
| X2 | Epson FC-135, 32.768 kHz | 12.5 pF | C28/C29 18 pF C0G |

The load capacitors follow C = 2 × (CL − C_stray): 26 – 30 pF for the 8 MHz part and 15 – 19 pF for the 32 kHz part, with 3 – 5 pF of stray capacitance.

The 8 MHz crystal feeds the PLL (×9) for 72 MHz. The 32.768 kHz crystal runs the RTC, which time-stamps events and provides Δt for charge counting.

## 6.4 Reset, boot, debug

| Block | Parts | Behaviour |
|---|---|---|
| Reset | Push button (TL3365) to GND, C30 100 nF | With the ~40 kΩ internal pull-up, τ ≈ 4 ms, so the button is debounced and the reset is held at power-up |
| Boot | R30 10 kΩ BOOT0 to GND, push button (TL3365) to 3.3 V | Hold the button at reset to start the ROM bootloader. On USART1 it is reachable through CN4 |
| SWD | CN3 JST SH 4-pin: 1 = 3.3 V, 2 = SWDIO, 3 = SWCLK, 4 = GND | ST-LINK programming and debug |
| UART | CN4 JST XH 4-pin: 1 = GND, 2 = TX, 3 = RX, 4 = 3.3 V | Telemetry and bootloader |

The board can be programmed two ways: over SWD, or with no debugger at all, over UART using the ROM bootloader.
