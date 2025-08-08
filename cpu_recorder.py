"""Record CPU usage periodically.

This script logs the system's overall CPU percentage at regular intervals.
It works on Linux by reading from /proc/stat.
"""

import argparse
import csv
from datetime import datetime
from pathlib import Path
import sys
import time
from typing import List


def _read_cpu_times() -> List[int]:
    with open("/proc/stat", "r", encoding="utf-8") as f:
        parts = f.readline().strip().split()[1:]
    return [int(p) for p in parts]


def _cpu_percent(interval: float) -> float:
    prev = _read_cpu_times()
    time.sleep(interval)
    curr = _read_cpu_times()
    idle_prev = prev[3] + prev[4]
    idle_curr = curr[3] + curr[4]
    total_prev = sum(prev)
    total_curr = sum(curr)
    total_delta = total_curr - total_prev
    idle_delta = idle_curr - idle_prev
    if total_delta == 0:
        return 0.0
    return 100.0 * (total_delta - idle_delta) / total_delta


def record_cpu(interval: float, iterations: int, output_file: str) -> None:
    """Record CPU percentage at a fixed interval.

    Args:
        interval: Seconds between samples.
        iterations: Number of samples to record; 0 means run indefinitely.
        output_file: File path for the CSV log, or '-' for stdout.
    """
    if output_file == "-":
        file_obj = sys.stdout
        header_needed = True
    else:
        file_path = Path(output_file)
        header_needed = not file_path.exists()
        file_obj = file_path.open("a", newline="")

    with file_obj:
        writer = csv.writer(file_obj)
        if header_needed:
            writer.writerow(["timestamp", "cpu_percent"])
        count = 0
        while iterations == 0 or count < iterations:
            cpu = _cpu_percent(interval)
            writer.writerow([datetime.now().isoformat(), cpu])
            file_obj.flush()
            count += 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interval", type=float, default=1.0,
                        help="Seconds between samples")
    parser.add_argument("--iterations", type=int, default=0,
                        help="Number of samples to record; 0 runs forever")
    parser.add_argument("--output", default="cpu_usage.log",
                        help="Output CSV file or '-' for stdout")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    record_cpu(args.interval, args.iterations, args.output)
