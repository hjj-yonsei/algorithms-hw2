"""최종 과제: 개별 체이닝과 선형 탐지의 탐색 비용 비교."""

import csv
import os
import random
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.hash_table import HashTable
from src.linear_probing import LinearProbingHashTable

TABLE_SIZE = 4093
LOAD_FACTORS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
QUERY_COUNT = 2000
TRIALS = 5


def generate_random_urls(count: int, rng: random.Random, prefix: str) -> list:
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
    urls = []
    for i in range(count):
        slug = "".join(rng.choice(alphabet) for _ in range(12))
        urls.append(f"https://example.com/{prefix}/{i}/{slug}")
    return urls


def run_comparison() -> list:
    rng = random.Random(2026)
    rows = []

    for alpha in LOAD_FACTORS:
        n_items = round(TABLE_SIZE * alpha)
        c_succ = c_fail = l_succ = l_fail = 0.0

        for trial in range(TRIALS):
            chain_ht = HashTable(capacity=TABLE_SIZE, max_load=None)
            linear_ht = LinearProbingHashTable(capacity=TABLE_SIZE, max_load=None)
            inserted = generate_random_urls(n_items, rng, f"cmp-in-{alpha}-{trial}")
            missing = generate_random_urls(QUERY_COUNT, rng, f"cmp-out-{alpha}-{trial}")

            for index, url in enumerate(inserted):
                chain_ht.put(url, str(index))
                linear_ht.put(url, str(index))

            sampled = [rng.choice(inserted) for _ in range(QUERY_COUNT)]
            for url in sampled:
                _, _, chain_probes = chain_ht.get_with_probes(url)
                _, _, linear_probes = linear_ht.get_with_probes(url)
                c_succ += chain_probes
                l_succ += linear_probes

            for url in missing:
                _, _, chain_probes = chain_ht.get_with_probes(url)
                _, _, linear_probes = linear_ht.get_with_probes(url)
                c_fail += chain_probes
                l_fail += linear_probes

        denominator = TRIALS * QUERY_COUNT
        actual_alpha = n_items / TABLE_SIZE
        rows.append(
            {
                "alpha": round(actual_alpha, 4),
                "chain_succ_exp": round(c_succ / denominator, 4),
                "chain_succ_theo": round(1.0 + actual_alpha / 2.0, 4),
                "chain_fail_exp": round(c_fail / denominator, 4),
                "chain_fail_theo": round(actual_alpha, 4),
                "linear_succ_exp": round(l_succ / denominator, 4),
                "linear_succ_theo": round(
                    0.5 * (1.0 + 1.0 / (1.0 - actual_alpha)), 4
                ),
                "linear_fail_exp": round(l_fail / denominator, 4),
                "linear_fail_theo": round(
                    0.5 * (1.0 + 1.0 / ((1.0 - actual_alpha) ** 2)), 4
                ),
            }
        )
    return rows


def save_csv(rows: list, filepath: str) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def save_svg(rows: list, filepath: str) -> None:
    width, height = 820, 500
    pad_l, pad_r, pad_t, pad_b = 70, 30, 45, 65
    plot_w = width - pad_l - pad_r
    plot_h = height - pad_t - pad_b
    max_x = 0.95
    max_y = max(row["linear_fail_exp"] for row in rows) * 1.08

    def sx(x: float) -> float:
        return pad_l + (x / max_x) * plot_w

    def sy(y: float) -> float:
        return pad_t + plot_h - (y / max_y) * plot_h

    def poly(key: str) -> str:
        return " ".join(
            f"{sx(row['alpha']):.1f},{sy(row[key]):.1f}" for row in rows
        )

    grid = []
    for gx in LOAD_FACTORS:
        x = sx(gx)
        grid.append(
            f"<line x1='{x:.1f}' y1='{pad_t}' x2='{x:.1f}' "
            f"y2='{pad_t + plot_h}' stroke='#eaeef2'/>"
        )
        grid.append(
            f"<text x='{x:.1f}' y='{pad_t + plot_h + 20}' "
            f"font-size='12' text-anchor='middle'>{gx}</text>"
        )
    for gy in range(0, int(max_y) + 5, 10):
        y = sy(gy)
        grid.append(
            f"<line x1='{pad_l}' y1='{y:.1f}' x2='{pad_l + plot_w}' "
            f"y2='{y:.1f}' stroke='#eaeef2'/>"
        )
        grid.append(
            f"<text x='{pad_l - 10}' y='{y + 4:.1f}' "
            f"font-size='12' text-anchor='end'>{gy}</text>"
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="#ffffff"/>
  <text x="{width / 2:.1f}" y="26" font-size="16" font-weight="bold" text-anchor="middle">개별 체이닝 vs 선형 탐지 탐색 비용 비교 (M = 4093, α = 0.1~0.9)</text>
  {''.join(grid)}
  <line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{pad_t + plot_h}" stroke="#24292f" stroke-width="1.5"/>
  <line x1="{pad_l}" y1="{pad_t + plot_h}" x2="{pad_l + plot_w}" y2="{pad_t + plot_h}" stroke="#24292f" stroke-width="1.5"/>
  <polyline fill="none" stroke="#cf222e" stroke-width="2.5" points="{poly('linear_fail_exp')}"/>
  <polyline fill="none" stroke="#ff8182" stroke-width="1.8" stroke-dasharray="5,4" points="{poly('linear_fail_theo')}"/>
  <polyline fill="none" stroke="#bf8700" stroke-width="2.5" points="{poly('linear_succ_exp')}"/>
  <polyline fill="none" stroke="#e3b341" stroke-width="1.8" stroke-dasharray="5,4" points="{poly('linear_succ_theo')}"/>
  <polyline fill="none" stroke="#0969da" stroke-width="2.5" points="{poly('chain_fail_exp')}"/>
  <polyline fill="none" stroke="#1a7f37" stroke-width="2.5" points="{poly('chain_succ_exp')}"/>
  <text x="{pad_l + plot_w / 2:.1f}" y="{height - 15}" font-size="13" font-weight="bold" text-anchor="middle">적재율 α = N / M</text>
  <text x="20" y="{pad_t + plot_h / 2:.1f}" font-size="13" font-weight="bold" text-anchor="middle" transform="rotate(-90 20 {pad_t + plot_h / 2:.1f})">평균 비교 노드 수 / 들여다본 칸 수</text>
  <g transform="translate({pad_l + 16}, {pad_t + 12})">
    <rect width="315" height="132" fill="#ffffff" stroke="#d0d7de" rx="6"/>
    <line x1="12" y1="20" x2="36" y2="20" stroke="#cf222e" stroke-width="2.5"/>
    <text x="44" y="24" font-size="12">선형 탐지 실패 (실선: 실험 / 점선: 이론)</text>
    <line x1="12" y1="42" x2="36" y2="42" stroke="#bf8700" stroke-width="2.5"/>
    <text x="44" y="46" font-size="12">선형 탐지 성공 (실선: 실험 / 점선: 이론)</text>
    <line x1="12" y1="64" x2="36" y2="64" stroke="#0969da" stroke-width="2.5"/>
    <text x="44" y="68" font-size="12">개별 체이닝 실패 (이론: α)</text>
    <line x1="12" y1="86" x2="36" y2="86" stroke="#1a7f37" stroke-width="2.5"/>
    <text x="44" y="90" font-size="12">개별 체이닝 성공 (이론: 1 + α/2)</text>
  </g>
</svg>"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as handle:
        handle.write(svg)


def main() -> None:
    rows = run_comparison()
    save_csv(rows, "experiments/comparison_results.csv")
    save_svg(rows, "experiments/comparison.svg")

    print(f"{'α':>4} | {'체이닝성공':>9} | {'체이닝실패':>9} | {'선형성공':>8} | {'선형실패':>8}")
    print("-" * 50)
    for row in rows:
        print(
            f"{row['alpha']:4.1f} | {row['chain_succ_exp']:9.2f} | "
            f"{row['chain_fail_exp']:9.2f} | {row['linear_succ_exp']:8.2f} | "
            f"{row['linear_fail_exp']:8.2f}"
        )


if __name__ == "__main__":
    main()
