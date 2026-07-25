# Optimus Thermal – LPTN Motor Thermal Modeling

## Overview
This module implements **Lumped Parameter Thermal Network (LPTN)** modeling
for electric motor actuators, targeting the Tesla Optimus thermal design role.

It models the transient and steady-state thermal behavior of a motor across
6 nodes: **Winding, Stator, Rotor, Housing, Coolant, Ambient**.

## Files
| File | Description |
|------|-------------|
| `python/lptn_model.py` | Transient RC thermal network, validation vs FEA reference |
| `octave/thermal_network.m` | Same model in Octave/MATLAB syntax |

## Outputs
All results saved to `results/optimus_thermal/`:
| Type | File |
|------|------|
| Transient CSV | `lptn_thermal_transient.csv` |
| Steady-state CSV | `lptn_steady_state.csv` |
| Transient plot | `lptn_transient.png` |
| Steady-state bar chart | `lptn_steady_state.png` |

## Physics
The LPTN solves the system:

```
C * dT/dt = Q - G * T
```

Where:
- `C` = thermal capacitance vector [J/K]
- `G` = conductance matrix built from resistances R [K/W]
- `Q` = heat generation per node [W]
- `T` = node temperatures [°C]

Integration: **Euler forward**, dt=0.5s, t_end=300s

## Validation
The Python script compares LPTN steady-state temperatures against
FEA reference values for Winding, Stator, and Rotor nodes,
printing absolute error per node.

## How to Run

**Python:**
```bash
cd MotorDesignSuite
source venv/bin/activate
python python/scripts/phase3/optimus_thermal/python/lptn_model.py
```

**Octave:**
```bash
octave --silent python/scripts/phase3/optimus_thermal/octave/thermal_network.m
```

## Relevance to Tesla Optimus Role
| Job Requirement | Coverage |
|----------------|----------|
| LPTN modeling of motor actuators | ✅ Core of this module |
| Alignment with experimental data | ✅ Validation section in lptn_model.py |
| Alignment with high-fidelity FEA | ✅ FEA reference comparison |
| Heat Transfer & Thermodynamics | ✅ RC network, transient analysis |
| MATLAB/Octave programming | ✅ thermal_network.m |
