import pytest
import subprocess
import sys
from pathlib import Path

def test_demo_script_help():
    """Verify that the demo script runs and displays help."""
    demo_path = Path(__file__).parent.parent / "examples" / "demo_battery_management.py"
    result = subprocess.run(
        [sys.executable, str(demo_path), "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "usage: demo_battery_management.py" in result.stdout

def test_demo_script_execution_steps():
    """Verify the demo script runs with a specific number of steps."""
    demo_path = Path(__file__).parent.parent / "examples" / "demo_battery_management.py"
    result = subprocess.run(
        [sys.executable, str(demo_path), "--steps", "5"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    # Check if we see 5 action rows (Charge, Hold, Discharge, Charge, Hold)
    assert "CHARGE" in result.stdout
    assert "DISCHARGE" in result.stdout
    assert "Final Charge" in result.stdout

def test_demo_script_invalid_args():
    """Verify the demo script rejects invalid argument combinations."""
    demo_path = Path(__file__).parent.parent / "examples" / "demo_battery_management.py"
    
    # Conflict: both steps and hours
    result = subprocess.run(
        [sys.executable, str(demo_path), "--steps", "10", "--hours", "2"],
        capture_output=True,
        text=True
    )
    assert result.returncode != 0
    assert "Error: Provide either --steps or --hours" in result.stderr

    # Negative hours
    result = subprocess.run(
        [sys.executable, str(demo_path), "--hours", "-1"],
        capture_output=True,
        text=True
    )
    assert result.returncode != 0
    assert "Error: --hours must be positive" in result.stderr

    # Zero PV
    result = subprocess.run(
        [sys.executable, str(demo_path), "--pv-kw", "0"],
        capture_output=True,
        text=True
    )
    assert result.returncode != 0
    assert "Error: --pv-kw must be positive" in result.stderr