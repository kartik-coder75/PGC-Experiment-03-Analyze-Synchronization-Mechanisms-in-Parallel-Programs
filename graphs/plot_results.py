import os
import matplotlib.pyplot as plt
import pandas as pd

script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "..", "data", "benchmark_data.csv")
df = pd.read_csv(csv_path)

plt.figure(figsize=(10, 6))

mechanisms = ["None", "Critical", "Atomic", "Lock"]
colors = {"None": "red", "Critical": "orange", "Atomic": "green", "Lock": "blue"}
markers = {"None": "x", "Critical": "s", "Atomic": "o", "Lock": "^"}

for mech in mechanisms:
    subset = df[df["Mechanism"] == mech]
    plt.plot(
        subset["Threads"],
        subset["Time_Seconds"],
        marker=markers[mech],
        color=colors[mech],
        linewidth=2,
        label=f"{mech} {'(Incorrect)' if mech == 'None' else '(Correct)'}"
    )

plt.title("Synchronization Mechanisms Execution Time vs. Thread Count", fontsize=14, fontweight="bold")
plt.xlabel("Number of Threads", fontsize=12)
plt.ylabel("Execution Time (seconds)", fontsize=12)
plt.xticks([1, 2, 4, 8])
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend(title="Mechanism", fontsize=10)
plt.tight_layout()

output_chart = os.path.join(script_dir, "execution_time_comparison.png")
plt.savefig(output_chart, dpi=300)
print(f"Chart saved to: {output_chart}")