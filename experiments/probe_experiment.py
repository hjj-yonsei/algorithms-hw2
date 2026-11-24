"""Fixed-capacity separate-chaining hash-table probe experiment."""

import csv
from pathlib import Path
import random
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.hash_table import HashTable


CAPACITY = 4093
TRIALS = 10
MISSING_PROBES_PER_TRIAL = 4093


def load_factors():
    return [index / 4.0 for index in range(1, 17)]


def random_url(rng, label):
    return (
        "https://"
        f"{rng.getrandbits(32):08x}-{rng.getrandbits(32):08x}."
        f"{rng.getrandbits(16):04x}/{label}"
    )


def run_experiment(trials=TRIALS):
    rng = random.Random(0xA106)
    rows = []

    for alpha in load_factors():
        item_count = int(round(alpha * CAPACITY))
        success_probe_totals = 0
        success_lookup_totals = 0
        failure_probe_totals = 0
        failure_lookup_totals = 0

        for trial in range(trials):
            table = HashTable(capacity=CAPACITY, max_load=None)
            success_urls = []
            for index in range(item_count):
                url = random_url(rng, f"insert-{trial}-{index}")
                table.put(url, index)
                success_urls.append(url)

            for url in success_urls:
                _, found, probes = table.get_with_probes(url)
                if found:
                    success_probe_totals += probes
                    success_lookup_totals += 1

            missing_urls = []
            for index in range(MISSING_PROBES_PER_TRIAL):
                url = random_url(rng, f"missing-{trial}-{index}")
                missing_urls.append(url)

            for url in missing_urls:
                _, found, probes = table.get_with_probes(url)
                if not found:
                    failure_probe_totals += probes
                    failure_lookup_totals += 1

        success_observed = success_probe_totals / success_lookup_totals
        failure_observed = failure_probe_totals / failure_lookup_totals
        success_theory = 1.0 + alpha / 2.0
        failure_theory = alpha

        rows.append(
            {
                "load_factor": alpha,
                "item_count": item_count,
                "success_observed": success_observed,
                "success_theory": success_theory,
                "success_difference": success_observed - success_theory,
                "failure_observed": failure_observed,
                "failure_theory": failure_theory,
                "failure_difference": failure_observed - failure_theory,
            }
        )

    return rows


def write_csv(rows, csv_path):
    csv_path = Path(csv_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "load_factor",
        "item_count",
        "success_observed",
        "success_theory",
        "success_difference",
        "failure_observed",
        "failure_theory",
        "failure_difference",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: (
                        f"{row[key]:.6f}"
                        if isinstance(row[key], float)
                        else row[key]
                    )
                    for key in fieldnames
                }
            )


def svg_polyline(points, width, height, left, top, x_max, y_max, color):
    mapped = []
    for x, y in points:
        px = left + (x / x_max) * width
        py = top + height - (y / y_max) * height
        mapped.append(f"{px:.2f},{py:.2f}")
    return (
        f'<polyline fill="none" stroke="{color}" stroke-width="3" '
        f'points="{" ".join(mapped)}"/>'
    )


def write_svg(rows, csv_path=None, svg_path=None):
    if svg_path is None:
        svg_path = ROOT / "experiments" / "probe_experiment.svg"
    svg_path = Path(svg_path)
    svg_path.parent.mkdir(parents=True, exist_ok=True)

    width = 1000
    height = 660
    left = 70
    right = 930
    panel_gap = 90
    success_top = 90
    success_height = 220
    failure_top = 410
    failure_height = 220
    plot_width = right - left

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        'viewBox="0 0 1000 660">',
        '<rect width="1000" height="660" fill="white"/>',
        '<text x="500" y="36" text-anchor="middle" font-size="22" '
        'font-family="sans-serif">개별 체이닝 탐색 노드 수 비교 (M=4093)</text>',
    ]

    for top, panel_height, title in (
        (success_top, success_height, "성공 탐색"),
        (failure_top, failure_height, "실패 탐색"),
    ):
        parts.append(
            f'<rect x="{left}" y="{top}" width="{plot_width}" '
            f'height="{panel_height}" fill="#fafafa" stroke="#cccccc"/>'
        )
        parts.append(
            f'<text x="{left}" y="{top - 12}" font-size="16" '
            f'font-family="sans-serif">{title}</text>'
        )

    success_points = [
        (row["load_factor"], row["success_observed"]) for row in rows
    ]
    success_theory = [
        (row["load_factor"], row["success_theory"]) for row in rows
    ]
    failure_points = [
        (row["load_factor"], row["failure_observed"]) for row in rows
    ]
    failure_theory = [
        (row["load_factor"], row["failure_theory"]) for row in rows
    ]

    parts.append(
        svg_polyline(
            success_points,
            plot_width,
            success_height,
            left,
            success_top,
            4.0,
            3.0,
            "#1565c0",
        )
    )
    parts.append(
        svg_polyline(
            success_theory,
            plot_width,
            success_height,
            left,
            success_top,
            4.0,
            3.0,
            "#d84315",
        )
    )
    parts.append(
        svg_polyline(
            failure_points,
            plot_width,
            failure_height,
            left,
            failure_top,
            4.0,
            4.0,
            "#1565c0",
        )
    )
    parts.append(
        svg_polyline(
            failure_theory,
            plot_width,
            failure_height,
            left,
            failure_top,
            4.0,
            4.0,
            "#d84315",
        )
    )

    for alpha in (0.25, 1.0, 2.0, 3.0, 4.0):
        x = left + (alpha / 4.0) * plot_width
        parts.append(
            f'<line x1="{x:.2f}" y1="{success_top}" x2="{x:.2f}" '
            f'y2="{success_top + success_height}" stroke="#dddddd"/>'
        )
        parts.append(
            f'<line x1="{x:.2f}" y1="{failure_top}" x2="{x:.2f}" '
            f'y2="{failure_top + failure_height}" stroke="#dddddd"/>'
        )
        parts.append(
            f'<text x="{x:.2f}" y="{success_top + success_height + 22}" '
            f'text-anchor="middle" font-size="12" font-family="sans-serif">{alpha:g}</text>'
        )
        parts.append(
            f'<text x="{x:.2f}" y="{failure_top + failure_height + 22}" '
            f'text-anchor="middle" font-size="12" font-family="sans-serif">{alpha:g}</text>'
        )

    parts.append(
        '<line x1="720" y1="55" x2="760" y2="55" '
        'stroke="#1565c0" stroke-width="3"/>'
        '<text x="768" y="60" font-size="13" font-family="sans-serif">실험 평균</text>'
        '<line x1="850" y1="55" x2="890" y2="55" '
        'stroke="#d84315" stroke-width="3"/>'
        '<text x="898" y="60" font-size="13" font-family="sans-serif">이론값</text>'
    )
    parts.append("</svg>")
    svg_path.write_text("\n".join(parts), encoding="utf-8")


def print_table(rows):
    print(
        "alpha   N       성공 실험  성공 이론  성공 차이  "
        "실패 실험  실패 이론  실패 차이"
    )
    print("-" * 83)
    for row in rows:
        print(
            f"{row['load_factor']:>5.2f} "
            f"{row['item_count']:>7d} "
            f"{row['success_observed']:>10.6f} "
            f"{row['success_theory']:>10.6f} "
            f"{row['success_difference']:>+10.6f} "
            f"{row['failure_observed']:>10.6f} "
            f"{row['failure_theory']:>10.6f} "
            f"{row['failure_difference']:>+10.6f}"
        )


def main():
    rows = run_experiment()
    print_table(rows)

    csv_path = ROOT / "experiments" / "results.csv"
    svg_path = ROOT / "experiments" / "results.svg"
    write_csv(rows, csv_path)
    write_svg(rows, csv_path=csv_path, svg_path=svg_path)
    print(f"\nCSV: {csv_path}")
    print(f"SVG: {svg_path}")


if __name__ == "__main__":
    main()
