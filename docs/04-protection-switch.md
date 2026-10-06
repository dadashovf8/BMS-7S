# 4. Protection switch

Sheet 1, blocks "Charging and Load mode switching", "Charging and Load connections", and the BQ76200 block.

## 4.1 Topology

```
VBAT ─┬─[Q14 S D]─┬─[D Q15 S]─┬─ PACK+
      ├─[Q2  S D]─┤─[D Q3  S]─┤
      └─[Q11 S D]─┴─[D Q12 S]─┘
        CHG gates   │   DSG gates
        (R8 10 MΩ   │   (R9 10 MΩ
         to VBAT)   │    to PACK+)
                    │
  VBAT ─ R7 1 kΩ ─ Q1 ─┤   (precharge, PCHG gate, R19 10 MΩ to common node)
  VBAT ─ R14 1 kΩ ─ Q13 ┘  (R55 10 MΩ)
```

- **Three parallel back-to-back pairs** of Infineon BSC010N04LS: 40 V, R_DS(on) ≤ 1.0 mΩ, Q_g 95 nC, C_iss 6.8 nF, SuperSO8.
- **Common drain.** CHG sources are on VBAT and DSG sources are on PACK+. The BQ76200 references its CHG drive to BAT and its DSG drive to PACK, which is why this orientation is used.
- **Body diodes.** The CHG FET diode conducts VBAT → PACK, so the pack can still discharge with CHG off. The DSG FET diode conducts PACK → VBAT, so the pack can still charge with DSG off.
- **Gate-source resistors.** R8 and R9 (10 MΩ) hold each gate group off whenever the driver output is high-impedance.

Path resistance is 2 × 1.0 mΩ / 3 = **0.67 mΩ** at 25 °C:

| Current | Total conduction loss | Per FET |
|---|---|---|
| 10 A | 0.07 W | 0.011 W |
| 20 A | 0.27 W | 0.044 W |
| 30 A | 0.60 W | 0.100 W |

## 4.2 Driver (U4, BQ76200PWR)

The BQ76200 is a high-side N-FET driver with an integrated charge pump, rated to 100 V absolute maximum.

| Pin | Connection | Note |
|---|---|---|
| BAT (2) | VBAT through R10 100 Ω, C23 10 nF to GND | Supply filter, 159 kHz corner |
| VDDCP (1) | C24 1 µF to BAT | Charge pump reservoir. Datasheet minimum 470 nF; 1 µF is sized for six gates |
| CHG (16) | 3 CHG gates | 9 – 14 V above BAT. R_on 1.1 kΩ, R_off 0.3 kΩ |
| DSG (12) | 3 DSG gates | 9 – 14 V above PACK. R_on 3.5 kΩ, R_off 1 kΩ |
| PCHG (14) | Q1/Q13 gates | 5 – 14 V below PACK |
| PACK (11) | PACK+ through R15 100 Ω, C25 10 nF | PACK sense and DSG reference |
| PACKDIV (10) | R28 300 kΩ / R29 11.3 kΩ to GND, D3 to GND | Internal switch to PACK while PMON_EN = 1 |
| VSS (9) | GND | |
| NC (3, 13, 15) | open | |

**Enable inputs** (CHG_EN, DSG_EN, PCHG_EN, PMON_EN, CP_EN):

```
STM32 ── 1 kΩ (R17/R20/R22/R24/R26) ──┬── 24.9 kΩ (R18/R21/R23/R25/R27) ── BQ76200 xx_EN
                                      │
                               D4..D8 MMSZ4701 (14 V) to GND
```

- The EN inputs are rated 15 V absolute maximum, and their current has to stay below 5 mA. The 14 V zener clamps the node, and 24.9 kΩ limits the input current to 0.56 mA at the clamp. The 1 kΩ on the MCU side limits current into the zener.
- V_IH is 1.2 V, so 3.3 V logic drives the inputs directly.
- Each input has a 0.6 – 4 MΩ internal pull-down, so an undriven input reads low and its output stays off.

**Charge pump.** CP_EN starts the pump, and so do CHG_EN or DSG_EN, which are ORed with it internally. CP_EN has its own MCU pin (PB5), so the pump is started once at power-up and left running. The 100 ms start-up time (at 470 nF) is then paid once instead of being added to every FET turn-on.

## 4.3 Switching times

Each driver output sees three gates, about 3 × 6.8 nF of C_iss plus Miller charge. First-order estimates from Q_g:

| Edge | Estimate |
|---|---|
| DSG off (1 kΩ) | ≈ 24 µs |
| DSG on (3.5 kΩ) | ≈ 83 µs |

The edges are slow on purpose. A protection switch that operates rarely does not need fast edges, and slow edges keep EMI and ringing low on the paralleled FETs.

## 4.4 Precharge (Q1, Q13, R7, R14)

- Q1 and Q13 are Diodes Inc. ZXMP10A13F: P-channel, −100 V, V_GS ±20 V, V_GS(th) −2 to −4 V.
- R7 and R14 are 1 kΩ 2512 1 W (Panasonic ERJ-1T), 500 Ω in parallel.
- With CHG and DSG both off, charge current flows PACK+ → DSG body diodes → common drain node → Q1/Q13 → R7/R14 → VBAT. This limits charge current into a deeply discharged stack.

| Case | Current | Per resistor |
|---|---|---|
| 30 V at PACK+, stack at 20 V | 18.6 mA | 86 mW |
| 30 V at PACK+, stack at 25 V | 8.6 mA | 18 mW |
| 30 V across one resistor | 30 mA | 0.9 W (rated 1 W) |

The resistors are rated for the full charger voltage across them. PCHG gate drive is specified for V_PACK above 17 V.

## 4.5 Pack-terminal voltage (PACKDIV)

```
V_ADC = V_PACK × R29 / (R28 + R29 + R_PMON)
```

- The resistor ratio is 27.55, so 36 V at the pack gives 1.31 V at the MCU.
- R_PMON is the BQ76200's internal switch (1.5 – 3.5 kΩ). It shifts the ratio to 27.68 – 27.86. With 0.1 % thin-film resistors for R28/R29, a single calibration point against a meter brings the reading to the resistor tolerance.
- The divider only conducts while PMON_EN = 1 (116 µA at 36 V), so it costs nothing while idle.
- The PACK+ reading tells the MCU whether a charger or a load is present while the switches are open.

## 4.6 Terminals and transients

| Ref | Part | Function |
|---|---|---|
| CN1 | XT60 (AMASS XT60PW-M) | Battery: pin 2 BAT+, pin 1 GND, pins 3/4 mounting tabs to GND |
| CN2 | XT60 | Pack: pin 2 PACK+, pin 1 GND |
| D1 | SMCJ75A | 1.5 kW unidirectional TVS, BAT to GND |
| D2 | ES3D (200 V 3 A, fast recovery) | Cathode PACK+, anode GND. Freewheels inductive load current when DSG opens, and clamps PACK+ against negative voltage |
| C7 + C8 | 2 × 10 nF 100 V in series | BAT to PACK+, high-frequency bypass across the switch |
| C5 + C9 | 2 × 10 nF 100 V in series | PACK+ to GND |

The bypass capacitors come in series pairs. One MLCC that fails short (for example from a flex crack) across the FETs would bypass the protection switch permanently; with two in series, two independent failures are needed.
