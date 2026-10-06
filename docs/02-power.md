# 2. Power supply

Sheet 1, blocks "5V", "3V3", "5V decoupling caps", "3V3 decoupling caps".

## 2.1 5 V buck (U1, LMR33630ADDAR)

| Item | Value | Note |
|---|---|---|
| Input | VBAT | After the shunt, so the board's own current is part of the INA239 reading |
| Device | LMR33630A: 400 kHz, 3 A, HSOIC-8 | V_IN 3.8 – 36 V |
| Feedback | R1 = 100 kΩ, R3 = 24.9 kΩ | V_OUT = 1.0 V × (1 + 100/24.9) = **5.016 V**. Range 4.86 – 5.17 V over V_FB and resistor tolerance |
| Inductor | L1 SRR1260-8R2Y, 8.2 µH, 5.7 A | Ripple 0.89 A p-p at 12 V in, 1.32 A p-p at 36 V in |
| C_IN | C2 10 µF 50 V 1210 + C3 220 nF 0805 | C3 sits at the VIN/PGND pins |
| C_OUT | C10 – C13 4 × 22 µF 16 V 1210 + C14 10 µF | |
| Bootstrap | C4 100 nF | |
| VCC | C6 1 µF | Internal LDO |
| EN | Tied to VIN | Runs whenever the stack is connected |
| PG | R4 10 kΩ to 3.3 V, routed to PB1 | Open drain. The MCU reads 5 V rail status |

The feedback divider, output capacitance, input capacitance and inductor follow the 5 V / 400 kHz row of the LMR33630 reference design table (datasheet Table 9-3: 100 k / 24.9 k, 4 × 22 µF, 10 µF + 220 nF, 8 µH). The only change is the next standard inductor value, 8.2 µH.

The inductor peak is 3.66 A at 3 A out and 36 V in, which is inside the SRR1260's 5.7 A rating.

## 2.2 3.3 V LDO (U3, AMS1117-3.3)

| Item | Value |
|---|---|
| Input | 5.0 V, C15 10 µF |
| Output | 3.3 V, C22 22 µF 1210 |
| Headroom | 1.7 V (dropout ≤ 1.3 V) |
| Loads | STM32F103, INA239 VS, SPI and alert pull-ups |

Two-stage conversion keeps the linear regulator's drop small (1.7 V) while the buck absorbs the full stack range.

## 2.3 Decoupling

| Rail | Parts | Placement |
|---|---|---|
| 5 V | C10 – C13 22 µF, C14 10 µF | Buck output and 5 V loads |
| 3.3 V | C16 – C20 100 nF 0402, C21 10 µF | One 100 nF at each STM32 VDD pin (24, 36, 48) and at VDDA (9) |
| LTC6811 | C33 (VREG), C34 (VREF1) | At the pins |
| BQ76200 | C23 10 nF (BAT), C24 1 µF (VDDCP – BAT) | At the pins |
| INA239 | C1 100 nF (VS) | At the pin |

## 2.4 LTC6811 supply

The LTC6811 has two supplies. V+ is the high-voltage supply and comes from the stack through R42 (100 Ω). VREG is the 5 V logic and ADC supply and comes from the board 5 V rail through R44 (0 Ω).

VREG is specified for 4.5 – 5.5 V, and the buck output stays within 4.86 – 5.17 V. Because VREG is fed directly, the DRIVE pin, which only biases an optional external NPN regulator, is left open. R44 allows the VREG current to be measured during bring-up.
