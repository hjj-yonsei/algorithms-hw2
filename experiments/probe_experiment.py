"""6단계: M=4093 고정 개별 체이닝 해시 테이블의 적재율별 평균 비교 노드 수 측정."""

import csv
import os
import random
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.hash_table import HashTable

TABLE_SIZE = 4093
LOAD_FACTORS = [0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
QUERY_COUNT = 2000
TRIALS = 5


def load_factors() -> list:
    return [index / 4.0 for index in range(1, 17)]


def generate_random_urls(count: int, rng: random.Random, prefix: str) -> list:
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
    urls = []
    for i in range(count):
        slug = "".join(rng.choice(alphabet) for _ in range(12))
        urls.append(f"https://example.com/{prefix}/{i}/{slug}")
    return urls


def run_experiment(trials: int = TRIALS) -> list:
    rng = random.Random(42)
    rows = []

    for alpha in load_factors():
        n_items = round(TABLE_SIZE * alpha)
        succ_total = 0.0
        fail_total = 0.0

        for t in range(trials):
            ht = HashTable(capacity=TABLE_SIZE, max_load=None)
            inserted_urls = generate_random_urls(n_items, rng, f"in-{alpha}-{t}")
            missing_urls = generate_random_urls(QUERY_COUNT, rng, f"out-{alpha}-{t}")

            for idx, u in enumerate(inserted_urls):
                ht.put(u, str(idx))

            sample_existing = [rng.choice(inserted_urls) for _ in range(QUERY_COUNT)]
            for u in sample_existing:
                _, _, probes = ht.get_with_probes(u)
                succ_total += probes

            for u in missing_urls:
                _, _, probes = ht.get_with_probes(u)
                fail_total += probes

        denom = trials * QUERY_COUNT
        exp_succ = succ_total / denom
        exp_fail = fail_total / denom
        actual_alpha = n_items / TABLE_SIZE
        theo_succ = 1.0 + actual_alpha / 2.0
        theo_fail = actual_alpha

        rows.append(
            {
                "load_factor": actual_alpha,
                "item_count": n_items,
                "success_observed": exp_succ,
                "success_theory": theo_succ,
                "success_difference": exp_succ - theo_succ,
                "failure_observed": exp_fail,
                "failure_theory": theo_fail,
                "failure_difference": exp_fail - theo_fail,
                "alpha": round(actual_alpha, 4),
                "n_items": n_items,
                "exp_success": round(exp_succ, 4),
                "theo_success": round(theo_succ, 4),
                "exp_fail": round(exp_fail, 4),
                "theo_fail": round(theo_fail, 4),
            }
        )
    return rows


def save_csv(rows: list, filepath: str) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["alpha", "n_items", "exp_success", "theo_success", "exp_fail", "theo_fail"],
        )
        writer.writeheader()
        writer.writerows(rows)


def save_svg(rows: list, filepath: str) -> None:
    width, height = 760, 460
    pad_l, pad_r, pad_t, pad_b = 70, 30, 45, 65
    plot_w = width - pad_l - pad_r
    plot_h = height - pad_t - pad_b

    max_x = 4.0
    max_y = 4.5

    def sx(x: float) -> float:
        return pad_l + (x / max_x) * plot_w

    def sy(y: float) -> float:
        return pad_t + plot_h - (y / max_y) * plot_h

    def polyline(points: list) -> str:
        return " ".join(f"{sx(x):.1f},{sy(y):.1f}" for x, y in points)

    p_exp_s = [(r["alpha"], r["exp_success"]) for r in rows]
    p_theo_s = [(r["alpha"], r["theo_success"]) for r in rows]
    p_exp_f = [(r["alpha"], r["exp_fail"]) for r in rows]
    p_theo_f = [(r["alpha"], r["theo_fail"]) for r in rows]

    grid_lines = []
    for gx in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]:
        x = sx(gx)
        grid_lines.append(f"<line x1='{x:.1f}' y1='{pad_t}' x2='{x:.1f}' y2='{pad_t + plot_h}' stroke='#eaeef2'/>")
        grid_lines.append(f"<text x='{x:.1f}' y='{pad_t + plot_h + 20}' font-size='12' text-anchor='middle'>{gx}</text>")
    for gy in [0, 1, 2, 3, 4]:
        y = sy(gy)
        grid_lines.append(f"<line x1='{pad_l}' y1='{y:.1f}' x2='{pad_l + plot_w}' y2='{y:.1f}' stroke='#eaeef2'/>")
        grid_lines.append(f"<text x='{pad_l - 10}' y='{y + 4:.1f}' font-size='12' text-anchor='end'>{gy}</text>")

    dots = []
    for x, y in p_exp_s:
        dots.append(f"<circle cx='{sx(x):.1f}' cy='{sy(y):.1f}' r='4' fill='#0969da'/>")
    for x, y in p_exp_f:
        dots.append(f"<circle cx='{sx(x):.1f}' cy='{sy(y):.1f}' r='4' fill='#cf222e'/>")

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="#ffffff"/>
  <text x="{width / 2:.1f}" y="26" font-size="16" font-weight="bold" text-anchor="middle">개별 체이닝 적재율(α)별 평균 비교 노드 수 (M = 4093)</text>
  {''.join(grid_lines)}
  <line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{pad_t + plot_h}" stroke="#24292f" stroke-width="1.5"/>
  <line x1="{pad_l}" y1="{pad_t + plot_h}" x2="{pad_l + plot_w}" y2="{pad_t + plot_h}" stroke="#24292f" stroke-width="1.5"/>
  <polyline fill="none" stroke="#0969da" stroke-width="2.5" points="{polyline(p_exp_s)}"/>
  <polyline fill="none" stroke="#54aeff" stroke-width="2" stroke-dasharray="6,4" points="{polyline(p_theo_s)}"/>
  <polyline fill="none" stroke="#cf222e" stroke-width="2.5" points="{polyline(p_exp_f)}"/>
  <polyline fill="none" stroke="#ff8182" stroke-width="2" stroke-dasharray="6,4" points="{polyline(p_theo_f)}"/>
  {''.join(dots)}
  <text x="{pad_l + plot_w / 2:.1f}" y="{height - 15}" font-size="13" font-weight="bold" text-anchor="middle">적재율 α = N / M</text>
  <text x="20" y="{pad_t + plot_h / 2:.1f}" font-size="13" font-weight="bold" text-anchor="middle" transform="rotate(-90 20 {pad_t + plot_h / 2:.1f})">평균 비교 노드 수</text>
  <g transform="translate({pad_l + 16}, {pad_t + 12})">
    <rect width="235" height="92" fill="#ffffff" stroke="#d0d7de" rx="6"/>
    <line x1="12" y1="20" x2="36" y2="20" stroke="#0969da" stroke-width="2.5"/>
    <text x="44" y="24" font-size="12">성공 탐색 (실험)</text>
    <line x1="12" y1="40" x2="36" y2="40" stroke="#54aeff" stroke-width="2" stroke-dasharray="6,4"/>
    <text x="44" y="44" font-size="12">성공 탐색 (이론: 1 + α/2)</text>
    <line x1="12" y1="60" x2="36" y2="60" stroke="#cf222e" stroke-width="2.5"/>
    <text x="44" y="64" font-size="12">실패 탐색 (실험)</text>
    <line x1="12" y1="80" x2="36" y2="80" stroke="#ff8182" stroke-width="2" stroke-dasharray="6,4"/>
    <text x="44" y="84" font-size="12">실패 탐색 (이론: α)</text>
  </g>
</svg>"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg)


def write_csv(rows: list, filepath) -> None:
    filepath = os.fspath(filepath)
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
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
    with open(filepath, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: f"{row[key]:.6f}" if isinstance(row[key], float) else row[key]
                    for key in fieldnames
                }
            )


def write_svg(rows: list, csv_path=None, svg_path=None) -> None:
    svg_path = os.fspath(svg_path or "experiments/results.svg")
    os.makedirs(os.path.dirname(svg_path) or ".", exist_ok=True)
    success_rows = [
        (row["load_factor"], row["success_observed"], row["success_theory"])
        for row in rows
    ]
    failure_rows = [
        (row["load_factor"], row["failure_observed"], row["failure_theory"])
        for row in rows
    ]

    width, height = 900, 520
    left, right, top, bottom = 80, 860, 50, 480
    plot_height = 170

    def point(alpha: float, value: float, y_top: float, y_max: float) -> tuple:
        x = left + (alpha / 4.0) * (right - left)
        y = y_top + plot_height - (value / y_max) * plot_height
        return x, y

    def polyline(values: list, y_top: float, y_max: float, observed: bool) -> str:
        points = " ".join(
            f"{point(alpha, value, y_top, y_max)[0]:.1f},"
            f"{point(alpha, value, y_top, y_max)[1]:.1f}"
            for alpha, observed_value, theory_value in values
            for value in [observed_value if observed else theory_value]
        )
        return points

    success_top = 90
    failure_top = 300
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="#ffffff"/>
  <text x="450" y="28" font-size="18" text-anchor="middle">개별 체이닝 탐색 노드 수 비교 (M=4093)</text>
  <text x="{left}" y="{success_top - 12}" font-size="14">성공 탐색</text>
  <rect x="{left}" y="{success_top}" width="{right-left}" height="{plot_height}" fill="#fafafa" stroke="#cccccc"/>
  <polyline fill="none" stroke="#0969da" stroke-width="3" points="{polyline(success_rows, success_top, 3.0, True)}"/>
  <polyline fill="none" stroke="#d84315" stroke-width="2" stroke-dasharray="6,4" points="{polyline(success_rows, success_top, 3.0, False)}"/>
  <text x="{left}" y="{failure_top - 12}" font-size="14">실패 탐색</text>
  <rect x="{left}" y="{failure_top}" width="{right-left}" height="{plot_height}" fill="#fafafa" stroke="#cccccc"/>
  <polyline fill="none" stroke="#0969da" stroke-width="3" points="{polyline(failure_rows, failure_top, 4.0, True)}"/>
  <polyline fill="none" stroke="#d84315" stroke-width="2" stroke-dasharray="6,4" points="{polyline(failure_rows, failure_top, 4.0, False)}"/>
</svg>"""
    with open(svg_path, "w", encoding="utf-8") as handle:
        handle.write(svg)


def main() -> None:
    rows = run_experiment()
    save_csv(rows, "experiments/results.csv")
    save_svg(rows, "experiments/probe_results.svg")

    print(f"{'적재율':>6} | {'성공(실험)':>10} | {'성공(이론)':>10} | {'실패(실험)':>10} | {'실패(이론)':>10}")
    print("-" * 58)
    for r in rows:
        print(
            f"{r['alpha']:6.2f} | {r['exp_success']:10.2f} | {r['theo_success']:10.2f} | "
            f"{r['exp_fail']:10.2f} | {r['theo_fail']:10.2f}"
        )


if __name__ == "__main__":
    main()
