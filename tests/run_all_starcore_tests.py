#!/usr/bin/env python3
"""Master test runner for STARCORE runtime layers 17x, 18x, 19x."""
from __future__ import annotations
import importlib.util
import os
import sys
import time
import traceback
from dataclasses import dataclass, field

RUNTIME_BASE = os.path.join(os.path.dirname(__file__), "..", "runtime")
GENERATIONS = ["17x", "18x", "19x"]


@dataclass
class TestResult:
    generation: str
    layer: str
    file: str
    name: str
    passed: bool
    duration_ms: float
    error: str = ""


@dataclass
class LayerSummary:
    generation: str
    layer: str
    passed: int = 0
    failed: int = 0
    results: list[TestResult] = field(default_factory=list)


def discover_and_run(generation: str, base: str) -> list[LayerSummary]:
    gen_path = os.path.join(base, generation)
    if not os.path.isdir(gen_path):
        return []

    summaries: list[LayerSummary] = []

    for layer_dir in sorted(os.listdir(gen_path)):
        layer_path = os.path.join(gen_path, layer_dir)
        if not os.path.isdir(layer_path):
            continue
        test_dir = os.path.join(layer_path, "tests")
        core_dir = os.path.join(layer_path, "core")
        if not os.path.isdir(test_dir):
            continue

        summary = LayerSummary(generation=generation, layer=layer_dir)

        if core_dir not in sys.path:
            sys.path.insert(0, core_dir)

        for fname in sorted(os.listdir(test_dir)):
            if not fname.startswith("test_") or not fname.endswith(".py"):
                continue
            fpath = os.path.join(test_dir, fname)
            spec = importlib.util.spec_from_file_location(
                f"{generation}.{layer_dir}.{fname[:-3]}", fpath
            )
            mod = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(mod)
            except Exception as e:
                result = TestResult(
                    generation=generation,
                    layer=layer_dir,
                    file=fname,
                    name="<load>",
                    passed=False,
                    duration_ms=0.0,
                    error=str(e),
                )
                summary.failed += 1
                summary.results.append(result)
                continue

            for name in sorted(dir(mod)):
                if not name.startswith("test_"):
                    continue
                fn = getattr(mod, name)
                if not callable(fn):
                    continue
                t0 = time.perf_counter()
                try:
                    fn()
                    ms = (time.perf_counter() - t0) * 1000
                    result = TestResult(
                        generation=generation,
                        layer=layer_dir,
                        file=fname,
                        name=name,
                        passed=True,
                        duration_ms=ms,
                    )
                    summary.passed += 1
                except Exception as e:
                    ms = (time.perf_counter() - t0) * 1000
                    result = TestResult(
                        generation=generation,
                        layer=layer_dir,
                        file=fname,
                        name=name,
                        passed=False,
                        duration_ms=ms,
                        error=str(e),
                    )
                    summary.failed += 1
                summary.results.append(result)

        summaries.append(summary)
    return summaries


def print_report(all_summaries: list[LayerSummary]) -> int:
    total_passed = total_failed = 0
    gen_stats: dict[str, tuple[int, int]] = {}

    for summary in all_summaries:
        gen = summary.generation
        p, f = gen_stats.get(gen, (0, 0))
        gen_stats[gen] = (p + summary.passed, f + summary.failed)
        total_passed += summary.passed
        total_failed += summary.failed

        for r in summary.results:
            status = "PASS" if r.passed else "FAIL"
            label = f"{r.layer}/{r.file}::{r.name}"
            timing = f"({r.duration_ms:.1f}ms)"
            if r.passed:
                print(f"  {status}  {label} {timing}")
            else:
                print(f"  {status}  {label} {timing}")
                if r.error:
                    print(f"         └─ {r.error}")

    print()
    print("=" * 60)
    print("STARCORE MASTER TEST SUITE — RESULTS BY GENERATION")
    print("=" * 60)
    for gen in GENERATIONS:
        if gen in gen_stats:
            p, f = gen_stats[gen]
            mark = "✓" if f == 0 else "✗"
            print(f"  {mark}  {gen}: {p} passed, {f} failed")
    print("-" * 60)
    mark = "✓" if total_failed == 0 else "✗"
    print(f"  {mark}  TOTAL: {total_passed} passed, {total_failed} failed")
    print("=" * 60)

    return 0 if total_failed == 0 else 1


def main() -> int:
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    all_summaries: list[LayerSummary] = []

    for gen in GENERATIONS:
        summaries = discover_and_run(gen, RUNTIME_BASE)
        all_summaries.extend(summaries)

    return print_report(all_summaries)


if __name__ == "__main__":
    sys.exit(main())
