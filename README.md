# PlainBatteryGym

A [Gymnasium](https://gymnasium.farama.org/)-compatible training environment for deep reinforcement learning (DRL) algorithms that learn household battery management. The environment simulates a household with rooftop photovoltaics (PV), a controllable battery, grid connection, and the Slovenian 5-level electricity tariff system.

Built with [CodePlain](https://codeplain.ai) at the **CodePlain Hackathon** on 16 May 2026.

## Team

- **Gregor Cerar**
- **Jernej Hribar**

## Overview

The DRL agent controls a household battery through three discrete actions: **charge**, **discharge**, and **hold**. The reward signal is the negative household electricity cost, encouraging the agent to minimise energy expenses by shifting grid consumption and exploiting PV production.

Key features:

- Gymnasium-compatible `reset` / `step` / `render` API
- 15-minute simulation timestep (fixed)
- Deterministic dummy input model (consumption, PV, tariff, weather)
- Slovenian 5-level tariff system with agreed power, excess power, VAT, and fixed fees (EUR)
- Named daily weather conditions (clear, cloudy, rainy) affecting PV output
- Strict configuration validation with safe coercion
- Multiple render modes: CLI text table, Matplotlib plots (`--mpl`), Pygame showcase (`--showcase`)
- Fully deterministic for reproducible experiments

## Project Contents

```
battery_management_env.plain   CodePlain specification (source of truth)
config.yaml                    CodePlain build configuration
dist/                          Generated + built package (ready to install)
  household_battery_management_env/   Python package source
  examples/                           Demo scripts
  tests/                              Unit tests
test_scripts/                  Build and test runner scripts
  run_unittests_python.sh
  run_conformance_tests_python.sh
  prepare_environment_python.sh
  demo_python.sh
demo_project.py                Quick smoke-test demo (external)
```

## Quick Start

### Prerequisites

- [uv](https://docs.astral.sh/uv/) (manages Python 3.12 automatically)
- A terminal on Linux or macOS

### Install and run

```bash
# Create an isolated environment and install the package
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -e dist/

# Run the demo (CLI text table, no display needed)
.venv/bin/python dist/examples/demo_battery_management.py

# Run with Matplotlib live plots
.venv/bin/python dist/examples/demo_battery_management.py --mpl

# Run the Pygame showcase animation
.venv/bin/python dist/examples/demo_battery_management.py --showcase
```

### Demo flags

| Flag | Description |
|---|---|
| `--steps N` | Maximum number of environment steps |
| `--hours H` | Simulation duration in hours (mutually exclusive with `--steps`) |
| `--pv-kw P` | Peak PV power in kW (default: 10) |
| `--mpl` / `--matplotlib` | Enable Matplotlib live rendering |
| `--showcase` | Enable eye-catching Pygame showcase animation |
| `--delay S` | Override visual-mode delay in seconds (default: 0.25 for visual modes) |

### Run tests

```bash
# Unit tests with coverage
./test_scripts/run_unittests_python.sh plain_modules/battery_management_env

# Or use the wrapper demo script
./test_scripts/demo_python.sh --steps 16
```

## How It Works

### Environment

The agent observes battery charge, time of day, current consumption, current PV production, and a 4-step forecast of future consumption and PV. At each 15-minute timestep it picks one of three actions:

| Action | Effect |
|---|---|
| `charge` | Store available PV energy in the battery (subject to max charge and charge rate) |
| `discharge` | Serve household demand from the battery (subject to min charge and discharge rate) |
| `hold` | Leave battery charge unchanged |

Invalid actions (e.g. charging a full battery) are clipped to the nearest valid value and penalised.

### Cost Model

Household electricity cost per timestep is computed from:

- Grid import at buy price + network energy tariff + network power tariff
- Grid export credit at sell price
- Excess power penalty when import exceeds agreed power for the active tariff block
- VAT applied to the total
- Daily allocation of monthly fixed fees

The reward is the negative of this cost.

### Dummy Input Model

The built-in dummy model generates deterministic daily patterns:

- **Consumption**: 25-35 kWh/day following typical household behaviour (morning and evening peaks)
- **PV production**: daylight bell curve peaking near solar noon, scaled by a daily weather factor
- **Weather**: repeating clear/cloudy/rainy cycle
- **Tariff blocks**: mapped from time of day and season (higher: Nov-Feb, lower: Mar-Oct)

### Render Modes

- **CLI (default)**: text table printed to the terminal
- **Matplotlib** (`--mpl`): simple live charts of energy flows, battery charge, and reward
- **Showcase** (`--showcase`): Pygame-based animated household scene with particle energy flows, weather visuals, battery fill gauge, event callouts, and keyboard controls (pause/resume, speed up/down)

## Development with CodePlain

The project was authored as a `***plain` specification and rendered into Python code by the CodePlain AI renderer. The `.plain` file is the source of truth; generated code under `plain_modules/` and `dist/` is read-only.

```bash
# Dry-run (validate specs without generating code)
codeplain battery_management_env.plain --dry-run

# Full render
codeplain battery_management_env.plain
```

## License

MIT
