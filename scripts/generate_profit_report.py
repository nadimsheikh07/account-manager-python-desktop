"""CLI to generate a profit report from the database.

Usage:
  python scripts/generate_profit_report.py [--start YYYY-MM-DD] [--end YYYY-MM-DD]

Outputs totals and a per-product breakdown to stdout.
"""
import argparse
import sys
import os
from datetime import datetime

# ensure project root is on path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.services.profit_report import generate_profit_report


def parse_date(s: str):
    try:
        return datetime.fromisoformat(s)
    except Exception:
        raise argparse.ArgumentTypeError("Invalid date format, use ISO YYYY-MM-DD")


def main():
    parser = argparse.ArgumentParser(description="Generate profit report")
    parser.add_argument("--start", type=parse_date, help="Start date (inclusive) in YYYY-MM-DD")
    parser.add_argument("--end", type=parse_date, help="End date (inclusive) in YYYY-MM-DD")
    args = parser.parse_args()

    start = args.start.isoformat() if args.start else None
    end = args.end.isoformat() if args.end else None

    report = generate_profit_report(start, end)

    print("Profit Report")
    if start or end:
        print(f"Period: {start or 'beginning'} to {end or 'now'}")
    print("-")
    print(f"Total Revenue: {report['revenue']:.2f}")
    print(f"Total COGS:    {report['cogs']:.2f}")
    print(f"Gross Profit:  {report['gross_profit']:.2f}")
    print("\nBy product:")
    print(f"{'ID':>4} {'SKU':<12} {'Name':<30} {'Qty':>5} {'Revenue':>10} {'COGS':>10} {'Profit':>10}")
    for p in report["breakdown"]:
        print(
            f"{p['product_id']:>4} {p['sku'] or '':<12} {p['name'][:30]:<30} {p['quantity_sold']:>5} {p['revenue']:>10.2f} {p['cogs']:>10.2f} {p['profit']:>10.2f}"
        )


if __name__ == "__main__":
    main()
