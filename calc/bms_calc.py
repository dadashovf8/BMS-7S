"""Design calculations for the 7S BMS.

Every number quoted in docs/ comes from this script. Component values are
taken from the schematic and the datasheets listed in docs/references.md.
Run:

    python calc/bms_calc.py > calc/results.md
"""

import math

# Supported stack voltage, set by the electronics rather than by a cell type:
#   lower bound: LTC6811 V+ minimum for specified accuracy (11 V)
#   upper bound: LMR33630 recommended maximum input (36 V)
V_STACK_MIN = 11.0
V_STACK_MAX = 36.0
V_CELL_EXAMPLE = 4.0       # V, example cell voltage for balancing figures

rows = []


def row(section, name, value, unit, note=""):
    rows.append((section, name, value, unit, note))


row("Envelope", "Stack voltage, min (LTC6811 V+ for TME)", V_STACK_MIN, "V")
row("Envelope", "Stack voltage, max (LMR33630 V_IN recommended)", V_STACK_MAX, "V")

# ---------------------------------------------------------------- 5 V buck
VFB = 1.000                # V, LMR33630 VFB typ (0.985 .. 1.015)
R1, R3 = 100e3, 24.9e3     # RFBT, RFBB
F_SW = 400e3               # Hz, LMR33630A
L1 = 8.2e-6                # H, SRR1260-8R2Y

v5 = VFB * (1 + R1 / R3)
v5_min = 0.985 * (1 + R1 * 0.99 / (R3 * 1.01))
v5_max = 1.015 * (1 + R1 * 1.01 / (R3 * 0.99))
row("Buck", "Vout = VFB x (1 + R1/R3)", v5, "V")
row("Buck", "Vout range (VFB +-1.5 %, R +-1 %)", f"{v5_min:.2f} .. {v5_max:.2f}", "V")
for vin in (12.0, 24.0, V_STACK_MAX):
    d = v5 / vin
    ripple = v5 * (vin - v5) / (vin * L1 * F_SW)
    row("Buck", f"Duty / inductor ripple at Vin = {vin:.0f} V", f"{d:.3f} / {ripple:.2f}", "- / A p-p")
row("Buck", "Inductor peak at 3 A out, 36 V in", 3 + v5 * (V_STACK_MAX - v5) / (V_STACK_MAX * L1 * F_SW) / 2,
    "A", "SRR1260 rated 5.7 A")

# ---------------------------------------------------------------- current sense
R_SHUNT = 1e-3
P_SHUNT_RATED = 3.0        # W, WSL3921
row("Shunt", "Current at rated 3 W", math.sqrt(P_SHUNT_RATED / R_SHUNT), "A")
for i in (10, 20, 30):
    row("Shunt", f"Drop / dissipation at {i} A", f"{i * R_SHUNT * 1e3:.0f} mV / {i**2 * R_SHUNT:.2f} W", "")
for adcrange, fs, lsb in ((0, 163.84e-3, 5e-6), (1, 40.96e-3, 1.25e-6)):
    row("INA239", f"ADCRANGE={adcrange}: full scale / LSB",
        f"+-{fs / R_SHUNT:.2f} A / {lsb / R_SHUNT * 1e3:.2f} mA", "")
current_lsb = 1.25e-3      # A, >= 40 A / 2^15
assert current_lsb >= 40.0 / 2**15
row("INA239", "CURRENT_LSB (40 A / 2^15, rounded up)", current_lsb * 1e3, "mA")
row("INA239", "SHUNT_CAL (ADCRANGE=1)", 819.2e6 * current_lsb * R_SHUNT * 4, "-", "819.2e6 x LSB x R x 4")
row("INA239", "Offset 5 uV max as current", 5e-6 / R_SHUNT * 1e3, "mA")

# ---------------------------------------------------------------- switches
RDS_MAX = 1.0e-3           # ohm, BSC010N04LS max at 25 C
N_PAIRS = 3
r_path = 2 * RDS_MAX / N_PAIRS
row("FETs", "Path resistance, 2 in series x 3 parallel (25 C)", r_path * 1e3, "mohm")
for i in (10, 20, 30):
    row("FETs", f"Total / per-FET conduction loss at {i} A (25 C)",
        f"{i**2 * r_path:.2f} / {(i / N_PAIRS)**2 * RDS_MAX:.3f}", "W")
QG = 95e-9                 # C, BSC010N04LS 0..10 V
R_DSG_OFF = 1e3            # ohm, BQ76200 R(DSGFETOFF)
R_DSG_ON = 3.5e3           # ohm, BQ76200 R(DSGFETON)
V_DRIVE = 12.0             # V, BQ76200 gate drive typ
row("FETs", "DSG turn-off, first order (3 x Qg, 1 kohm)", N_PAIRS * QG / (V_DRIVE / R_DSG_OFF) * 1e6, "us")
row("FETs", "DSG turn-on, first order (3 x Qg, 3.5 kohm)", N_PAIRS * QG / (V_DRIVE / R_DSG_ON) * 1e6, "us")

# ---------------------------------------------------------------- precharge
R_PCHG = 1e3 / 2           # 2 x 1 kohm in parallel
for v_chg, v_bat in ((30.0, 20.0), (30.0, 25.0)):
    i = (v_chg - 0.7 - v_bat) / R_PCHG
    row("Precharge", f"Current, {v_chg:.0f} V at PACK+, {v_bat:.0f} V stack", i * 1e3, "mA",
        f"{(i / 2)**2 * 1e3 * 1e3:.0f} mW per resistor")
row("Precharge", "Per 1 kohm with 30 V across", 30.0**2 / 1e3, "W", "2512, rated 1 W")

# ---------------------------------------------------------------- pack divider
R28, R29 = 300e3, 11.3e3
R_PMON = (1.5e3, 2.5e3, 3.5e3)   # BQ76200 internal switch min / typ / max
k_ideal = (R28 + R29) / R29
row("PACKDIV", "Divider ratio (R28 + R29) / R29", k_ideal, "-")
for name, rp in zip(("min", "typ", "max"), R_PMON):
    k = (R28 + R29 + rp) / R29
    row("PACKDIV", f"Ratio incl. R_PMON {name} ({rp / 1e3:.1f} kohm)", k, "-",
        f"{(k / k_ideal - 1) * 100:+.2f} % vs resistor-only ratio")
row("PACKDIV", "Divider output at 36 V", V_STACK_MAX / k_ideal, "V")
row("PACKDIV", "Divider current at 36 V, PMON_EN = 1", V_STACK_MAX / (R28 + R29) * 1e6, "uA")

# ---------------------------------------------------------------- enable lines
R_SER_MCU, R_SER_BQ = 1e3, 24.9e3
row("Enable", "BQ76200 EN input current at 14 V zener clamp", 14 / R_SER_BQ * 1e3, "mA", "datasheet limit 5 mA")

# ---------------------------------------------------------------- cell monitor
R_F, C_F = 100.0, 100e-9
row("LTC6811", "Cell filter RC corner (single section)", 1 / (2 * math.pi * R_F * C_F) / 1e3, "kHz")
row("LTC6811", "Filter time constant", R_F * C_F * 1e6, "us")
row("LTC6811", "Settle time before all-cell ADCV (6 tau)", 6 * R_F * C_F * 1e6, "us")
R_BAL = 50.0
i_bal = V_CELL_EXAMPLE / R_BAL
row("Balance", f"Bleed current at {V_CELL_EXAMPLE:.1f} V", i_bal * 1e3, "mA")

VREF2 = 3.0
B = 3380.0
for t_c in (0, 25, 45, 60):
    r_ntc = 10e3 * math.exp(B * (1 / (t_c + 273.15) - 1 / 298.15))
    v = VREF2 * r_ntc / (r_ntc + 10e3)
    row("NTC", f"VTEMP at {t_c} C (B25/50 = 3380 K)", v, "V", f"R_NTC = {r_ntc / 1e3:.2f} kohm")
row("NTC", "VREF2 load, 3 dividers", 3 * VREF2 / 20e3 * 1e3, "mA")

# ---------------------------------------------------------------- clocks
for name, cl, c_fit in (("8 MHz (CL 18 pF)", 18e-12, 30e-12), ("32.768 kHz (CL 12.5 pF)", 12.5e-12, 18e-12)):
    row("Crystal", f"{name}: 2 x (CL - 3..5 pF stray)",
        f"{2 * (cl - 5e-12) * 1e12:.0f} .. {2 * (cl - 3e-12) * 1e12:.0f}", "pF", f"fitted {c_fit * 1e12:.0f} pF")


def fmt(v):
    if isinstance(v, str):
        return v
    if abs(v) >= 1000:
        return f"{v:.0f}"
    return f"{v:.4g}"


if __name__ == "__main__":
    print("# Calculation results\n")
    print("Generated by `calc/bms_calc.py`. Do not edit by hand.\n")
    section = None
    for sec, name, value, unit, note in rows:
        if sec != section:
            section = sec
            print(f"\n## {sec}\n")
            print("| Quantity | Value | Unit | Note |")
            print("|---|---|---|---|")
        print(f"| {name} | {fmt(value)} | {unit} | {note} |")
