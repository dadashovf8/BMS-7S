# 5. Cell monitoring

Sheet 3.

## 5.1 U6 LTC6811HG-2

Analog Devices LTC6811-2: 12-channel stack monitor, addressable SPI variant, H grade (−40 to 125 °C), SSOP-48. It provides a 16-bit ΔΣ ADC per multiplexer and 1.2 mV maximum total measurement error.

| Pin | Connection | Function |
|---|---|---|
| V+ (1) | VBAT through R42 100 Ω | High-voltage supply from the stack (11 – 55 V) |
| V− (30, 31) | GND | Stack bottom |
| VREG (37) | 5 V through R44 0 Ω, C33 | 5 V logic and ADC supply |
| VREF1 (35) | C34 | ADC reference |
| VREF2 (34) | NTC dividers | 3.0 V buffered reference for the thermistors |
| DRIVE (38) | open | Not used, VREG is supplied externally |
| DTEN (36) | VREG | Discharge timer enabled |
| ISOMD (40) | GND | 4-wire SPI mode |
| WDT (39) | open | |
| A0 – A3 (45 – 48) | R49/R53/R56/R60 10 kΩ to VREG | Device address 15 |
| CSB, SCK, SDI (41 – 43) | SPI2 | V_IH 2.3 V, driven directly from 3.3 V logic |
| SDO (44) | SPI2, R31 10 kΩ to 3.3 V | Open drain; the 3.3 V pull-up sets the logic level seen by the MCU |
| GPIO1 – 3 (27 – 29) | VTEMP1 – 3 | Thermistor inputs |
| GPIO4, 5 (32, 33) | open | Spare |

The LTC6811 runs from 5 V, while the MCU uses 3.3 V. No level shifter is needed: the SPI inputs accept 3.3 V levels, and SDO is open drain with its pull-up on the 3.3 V rail.

## 5.2 Cell input assignment

Inside the LTC6811, the 12 channels are measured by two multiplexers of six channels each. With seven cells, the unused inputs are split between the top of each multiplexer, as the datasheet describes for fewer than 12 cells. The lower multiplexer measures four cells and the upper one measures three.

| LTC6811 input | Net | Reads |
|---|---|---|
| C0 | CELL0 = GND | Stack bottom |
| C1 – C4 | CELL1 – CELL4 | Cells 1 – 4 |
| C5, C6 | tied to C4 | 0 V, unused |
| C7, C8, C9 | CELL5, CELL6, CELL7 | Cells 5 – 7 |
| C10 – C12 | tied to C9 | 0 V, unused |

Splitting the cells this way lets both ADCs work in parallel on similar cell counts, so both halves of the stack are sampled at nearly the same instant.

## 5.3 Input filter and balancing (per cell, ×7)

```
CELLn ──┬────── R 100 Ω ────┬──── Cn
        │                   C 100 nF (to C(n-1), differential)
        S  ┌────────┐
     Q BSS308PE     │
        D──R 50 Ω───┴── CELL(n-1)
        G── R 1 kΩ ── Sn
```

| Cell | Series R | Filter C | Balance FET | Gate R | Bleed R | S pin |
|---|---|---|---|---|---|---|
| 7 | R32 | C31 | Q4 | R37 | R6 | S9 |
| 6 | R41 | C32 | Q5 | R45 | R11 | S8 |
| 5 | R46 | C35 | Q6 | R48 | R12 | S7 |
| 4 | R50 | C36 | Q7 | R52 | R36 | S4 |
| 3 | R54 | C37 | Q8 | R57 | R43 | S3 |
| 2 | R58 | C38 | Q9 | R61 | R47 | S2 |
| 1 | R62 | C39 | Q10 | R64 | R51 | S1 |
| C0 | R65 | C40 (to GND) | - | - | - | - |

**Filter.** 100 Ω in series with each input, with 100 nF between adjacent inputs (τ = 10 µs). In the differential arrangement each capacitor sees only one cell voltage, and transient energy is spread evenly across the IC inputs. The bleed path does not go through the 100 Ω, so balancing does not disturb the filter.

**Balancing.** This is the external-transistor scheme from the LTC6811 datasheet (Fig. 41b), built around the same BSS308PE P-FET. Internally, each S pin has a PMOS pull-up with a 1 kΩ series resistor to C(n), and an NMOS to C(n−1).

- Bit clear: S is held at C(n), and the P-FET is off. No external gate-source resistor is needed.
- Bit set: S is pulled toward C(n−1), and the P-FET sees V_GS ≈ −V_cell.

The bleed current is V_cell / 50 Ω, about 80 mA at 4.0 V. Moving the dissipation out of the IC allows several times the 60 mA limit of the internal discharge switches.

**DCP bit.** With DCP = 0, the LTC6811 releases the S outputs while the corresponding cell is being converted, so the reading is taken without bleed current.

## 5.4 Temperature

| Ref | Part | Note |
|---|---|---|
| R33 – R35 | 10 kΩ 1 % 0402 | Pull-ups from VREF2 (3.0 V) |
| R38 – R40 | Murata NCP15XH103F03RC | 10 kΩ 1 % NTC, B25/50 = 3380 K, 0402 |

```
V_TEMP = 3.0 × R_NTC / (R_NTC + 10 kΩ)

R = 10k · V / (3.0 − V)
T = 1 / (1/298.15 + ln(R / 10k) / 3380) − 273.15
```

| T | R_NTC | V_TEMP |
|---|---|---|
| 0 °C | 28.2 kΩ | 2.22 V |
| 25 °C | 10.0 kΩ | 1.50 V |
| 45 °C | 4.90 kΩ | 0.99 V |
| 60 °C | 3.04 kΩ | 0.70 V |

The ADC reads the dividers with VREF2 as their supply, so the measurement is ratiometric: reference drift cancels out. The dividers only draw current (0.45 mA total) while the reference is on.

## 5.5 Connectors

| Ref | Part | Pins |
|---|---|---|
| CN6 | JST B8B-XH-A | CELL0 – CELL7, balance lead |
| CN5 | JST B7B-XH-A | CELL0 – CELL6 |

## 5.6 Watchdog and discharge timer

If the LTC6811 receives no valid command for 2 s, it resets its configuration registers. With DTEN tied to VREG, the discharge timer keeps the selected S outputs on for the programmed DCTO time and then turns them off. Balancing therefore always ends by itself, even if the host stops communicating.
