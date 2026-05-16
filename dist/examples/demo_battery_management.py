import argparse
import sys
import time
from datetime import timedelta
from household_battery_management_env import (
    BatteryManagementEnvironment, 
    Battery, 
    EnvironmentConfiguration, 
    BatteryAction
)

def run_demo():
    parser = argparse.ArgumentParser(description="Demonstration script for Household Battery Management Environment.")
    parser.add_argument("--steps", type=int, help="Number of environment steps to run.")
    parser.add_argument("--hours", type=float, help="Simulation duration in hours.")
    parser.add_argument("--pv-kw", type=float, default=10.0, help="Peak PV system power in kW.")
    parser.add_argument("--mpl", "--matplotlib", action="store_true", dest="mpl", help="Enable Matplotlib rendering.")
    parser.add_argument("--showcase", action="store_true", help="Enable high-polish Pygame showcase rendering.")
    parser.add_argument("--delay", type=float, help="Delay between steps in seconds.")

    args = parser.parse_args()

    # 1. Validation
    if args.steps is not None and args.hours is not None:
        print("Error: Provide either --steps or --hours, but not both.", file=sys.stderr)
        sys.exit(1)
    
    if args.hours is not None and args.hours <= 0:
        print(f"Error: --hours must be positive. Received: {args.hours}", file=sys.stderr)
        sys.exit(1)

    if args.pv_kw <= 0:
        print(f"Error: --pv-kw must be positive. Received: {args.pv_kw}", file=sys.stderr)
        sys.exit(1)

    # Calculate steps
    max_steps = 24  # Default short demo
    if args.steps is not None:
        max_steps = args.steps
    elif args.hours is not None:
        max_steps = int(args.hours * 4)

    # Determine Render Mode
    render_mode = None
    if args.showcase:
        render_mode = "human"
    elif args.mpl:
        render_mode = "matplotlib"

    # Determine Delay
    step_delay = 0.0
    if args.delay is not None:
        step_delay = args.delay
    elif render_mode is not None:
        step_delay = 0.25

    # 2. Configuration
    battery = Battery(
        capacity_kwh=13.5,
        current_charge_kwh=5.0,
        min_charge_kwh=1.0,
        max_charge_kwh=13.0,
        charge_rate_kw=5.0,
        discharge_rate_kw=5.0
    )
    
    # Estimate days needed based on steps
    days_needed = max(1, (max_steps // 96) + 1)
    
    config = EnvironmentConfiguration(
        battery=battery,
        days=days_needed,
        pv_peak_kw=args.pv_kw,
        seed=42
    )

    # 3. Initialization
    env = BatteryManagementEnvironment(config=config, render_mode=render_mode)
    obs, info = env.reset()
    
    print(f"\n{'='*80}")
    print(f"Starting Battery Management Demo (Steps: {max_steps}, PV Peak: {args.pv_kw}kW)")
    print(f"{'='*80}")
    header = f"{'Time':<10} | {'Action':<10} | {'Charge':<10} | {'Cons':<8} | {'PV':<8} | {'Cost':<8} | {'Reward':<8}"
    print(header)
    print("-" * len(header))

    total_reward = 0.0
    total_cost = 0.0
    
    # Deterministic action sequence: Charge, Hold, Discharge cycle
    actions = [BatteryAction.CHARGE, BatteryAction.HOLD, BatteryAction.DISCHARGE]

    # 4. Simulation Loop
    try:
        for i in range(max_steps):
            action = actions[i % 3]
            
            # Extract values for table before step
            # obs: [charge, hour, consumption, pv, ...]
            current_hour = obs[1]
            current_time = str(timedelta(hours=float(current_hour)))[:-3]
            
            obs, reward, terminated, truncated, info = env.step(action)
            
            cost = info.get("cost", 0.0)
            total_reward += reward
            total_cost += cost
            
            # Print table row
            print(f"{current_time:<10} | {action.name:<10} | {obs[0]:>8.2f}kWh | {obs[2]:>6.2f} | {obs[3]:>6.2f} | {cost:>6.4f} | {reward:>6.2f}")
            
            if render_mode:
                env.render()
            
            if step_delay > 0:
                time.sleep(step_delay)
                
            if terminated:
                break
    except KeyboardInterrupt:
        print("\nDemo interrupted by user.")
    finally:
        env.close()

    # 5. Final Summary
    print("-" * len(header))
    print(f"Final Charge:   {obs[0]:.2f} kWh")
    print(f"Total Cost:     {total_cost:.4f} EUR")
    print(f"Total Reward:   {total_reward:.2f}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    run_demo()