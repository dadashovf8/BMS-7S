# 8. Bill of materials

Full list: [hardware/BOM_revA.csv](../hardware/BOM_revA.csv), exported from Altium. 47 lines, 143 placements.

## 8.1 Active parts

| Ref | Part | Function | Why this part |
|---|---|---|---|
| U1 | TI LMR33630ADDAR | 5 V buck, 3 A, 400 kHz | 36 V input, 24 µA quiescent, power-good output, reference design for 5 V |
| U2 | TI INA239AIDGSR | Shunt monitor, SPI | 85 V common mode on the high side, 16-bit, ±5 µV offset, ALERT |
| U3 | AMS1117-3.3 | 3.3 V LDO | 5 V to 3.3 V, SOT-223 |
| U4 | TI BQ76200PWR | High-side N-FET driver | Charge pump for high-side N-FETs, separate CHG/DSG/PCHG drivers, switched pack monitor |
| U5 | ST STM32F103C8T6TR | MCU | Two SPI ports, USART bootloader, RTC, 12-bit ADC |
| U6 | ADI LTC6811HG-2 | Cell monitor | Up to 12 cells, 1.2 mV TME, addressable SPI, discharge timer, H grade |
| Q2, Q3, Q11, Q12, Q14, Q15 | Infineon BSC010N04LS | Charge/discharge switches | 1.0 mΩ in SuperSO8, 95 nC gate charge |
| Q1, Q13 | Diodes ZXMP10A13F | Precharge P-FET | −100 V, SOT-23 |
| Q4 – Q10 | Infineon BSS308PE | Balance P-FET | The transistor used in the LTC6811 datasheet's external balancing circuit |

## 8.2 Passives and protection

| Ref | Part | Function |
|---|---|---|
| R2 | Vishay WSL3921 1 mΩ 1 % 3 W | Current shunt, metal strip |
| R28, R29 | 300 kΩ / 11.3 kΩ thin film 0.1 % 25 ppm | Pack-voltage divider |
| R7, R14 | 1 kΩ 2512 1 W | Precharge current limit |
| R8, R9, R19, R55 | 10 MΩ 0603 | Gate-source hold-off |
| R6, R11, R12, R36, R43, R47, R51 | 50 Ω | Balance bleed |
| R38 – R40 | Murata NCP15XH103F03RC | 10 kΩ NTC, B 3380 K |
| L1 | Bourns SRR1260-8R2Y | 8.2 µH, 5.7 A shielded |
| D1 | SMCJ75A | 1.5 kW TVS on the battery input |
| D2 | ES3D | 200 V 3 A fast diode on PACK+ |
| D3 – D8 | MMSZ4701 | 14 V zeners, BQ76200 input clamps |
| C5, C7, C8, C9 | 10 nF 100 V X7R 0805 | Series-pair bypass across the switch and on PACK+ |
| C26 – C29 | 30 pF / 18 pF C0G | Crystal load capacitors |

## 8.3 Electromechanical

| Ref | Part | Function |
|---|---|---|
| CN1, CN2 | AMASS XT60PW-M | Battery and pack terminals |
| CN6 | JST B8B-XH-A | Balance lead, 7 cells |
| CN5 | JST B7B-XH-A | 7-pin cell connector |
| CN4 | JST B4B-XH-A | UART |
| CN3 | JST SM04B-SRSS-TB | SWD, 1 mm pitch |
| B1, B2 | C&K TL3365 | Reset, boot |
| X2 and 8 MHz | Epson FC-135 32.768 kHz, Abracon ABM3 8 MHz | Clocks |

## 8.4 Count by type

| Type | Lines | Placements |
|---|---|---|
| Capacitors | 10 | 40 |
| Resistors (incl. NTC and shunt) | 16 | 63 |
| Transistors | 3 | 15 |
| Diodes | 3 | 8 |
| ICs | 6 | 6 |
| Inductor | 1 | 1 |
| Crystals | 2 | 2 |
| Connectors | 5 | 6 |
| Buttons | 1 | 2 |
