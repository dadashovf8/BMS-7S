# 1. System overview

## 1.1 Scope

A single-board BMS for a 7-series battery stack. The board:

- Measures each cell voltage, three temperatures, the stack current, the battery voltage and the pack-terminal voltage.
- Switches the charge path and the discharge path on the high side. It also has a current-limited precharge path.
- Balances cells passively.
- Reports over UART.

All protection decisions are made in MCU firmware. The BQ76200 and LTC6811 measure and drive; they do not open the FETs on their own.

## 1.2 Ratings

| Parameter | Value | Basis |
|---|---|---|
| Cell count | 7 series | LTC6811 input wiring, CN6 |
| Stack voltage | 11 – 36 V | LTC6811 V+ minimum for specified accuracy, LMR33630 maximum input |
| Current measurement | ±40.96 A at 1.25 mA/LSB | INA239, ADCRANGE = 1 |
| Switch path resistance | 0.67 mΩ | 3 × back-to-back BSC010N04LS |
| Cell voltage measurement | 16-bit ΔΣ, 0 – 5 V per cell | LTC6811 |
| Balancing | Passive, 50 Ω per cell (80 mA at 4.0 V) | External P-FET |
| Temperature inputs | 3 × 10 kΩ NTC | LTC6811 GPIO1 – 3 |
| Power and load connectors | XT60 (battery, pack) | CN1, CN2 |
| Interfaces | UART (CN4), SWD (CN3) | |

## 1.3 Block diagram

```
                   CN6 balance (CELL0..CELL7)
                        │
                        ▼
                 ┌────────────┐  SPI2 (≤1 MHz)
                 │ LTC6811-2  │──────────────────────────┐
                 │ addr 15    │                          │
                 └────────────┘                          │
                                                         ▼
 CN1  BAT+ ── R2 1 mΩ ── VBAT ══ Q14/Q2/Q11 ══╦══ Q15/Q3/Q12 ══ PACK+ ── CN2
 (XT60)  │      │  │      │       (CHG, S=VBAT)║   (DSG, S=PACK+)        (XT60)
         │     IN+ IN-    │                    ╚═ Q1/Q13 + 2×1 kΩ ═ VBAT   (precharge)
         │    ┌──────┐    │          ▲  ▲  ▲
         └────│INA239│    │       CHG DSG PCHG
         VBUS └──────┘    │       ┌─────────┐   PACKDIV ─ 300k/11.3k ─► MCU
              SPI1 │      ├──────►│ BQ76200 │
              (≤10 MHz)   │       └─────────┘
                   │      │          ▲ CP_EN CHG_EN DSG_EN PCHG_EN PMON_EN
                   ▼      │          │
            ┌───────────────┐        │
            │ STM32F103C8T6 │────────┘
            └───────────────┘── USART1 (CN4), SWD (CN3)
                   ▲
   VBAT ─► LMR33630 (5.0 V) ─► AMS1117 (3.3 V)
                    └─► LTC6811 VREG
```

Battery negative, pack negative and board ground are one node. Because the switches are on the high side, the UART ground does not move relative to the pack terminals.

## 1.4 Sheets

| Sheet | Contents | Doc |
|---|---|---|
| 1. Power and Measurement | Buck, LDO, current sense, BQ76200, FETs, connectors | [2](02-power.md), [3](03-current-sense.md), [4](04-protection-switch.md) |
| 2. STM32 | MCU, clocks, reset, boot, SWD, UART | [6](06-mcu.md) |
| 3. Cell Monitoring | LTC6811-2, filters, balancing, NTCs, balance connector | [5](05-cell-monitor.md) |

## 1.5 Switch states

| State | CP_EN | DSG_EN | CHG_EN | PCHG_EN | Path |
|---|---|---|---|---|---|
| Off | 0 | 0 | 0 | 0 | Open both ways (body diodes oppose) |
| Standby | 1 | 0 | 0 | 0 | Open, charge pump running |
| Precharge | 1 | 0 | 0 | 1 | Charge through 500 Ω only |
| Normal | 1 | 1 | 1 | 0 | Closed both ways |
| Charge blocked | 1 | 1 | 0 | 0 | Discharge only (through the CHG body diode) |
| Discharge blocked | 1 | 0 | 1 | 0 | Charge only (through the DSG body diode) |

The two single-direction states let the system recover from a charge or discharge limit without disconnecting the pack terminal completely.

## 1.6 Power tree

All board supplies draw from the full stack (VBAT or BAT), not from individual cells. Board consumption therefore loads every cell equally and does not unbalance them.

```
VBAT ─┬─ LMR33630 ── 5 V ─┬─ AMS1117 ── 3.3 V ── STM32, INA239 VS, pull-ups
      │                   └─ R44 0 Ω ── LTC6811 VREG
      ├─ R42 100 Ω ── LTC6811 V+
      └─ R10 100 Ω ── BQ76200 BAT
BAT ──── INA239 VBUS
```
