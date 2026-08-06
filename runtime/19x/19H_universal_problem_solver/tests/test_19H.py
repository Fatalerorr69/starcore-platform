"""Tests for 19H Universal Problem Solver"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest():
    d = json.loads((Path(__file__).parent.parent / "registry/manifest.json").read_text())
    assert d["layer"] == "19H"


def test_trivial_goal():
    from problem_solver import UniversalProblemSolver, ProblemState
    solver = UniversalProblemSolver()
    initial = ProblemState("start")
    result = solver.solve(initial,
                          is_goal=lambda s: s.state_id == "start",
                          expand=lambda s: [])
    assert result.found
    assert result.path == ["start"]


def test_path_finding():
    from problem_solver import UniversalProblemSolver, ProblemState
    solver = UniversalProblemSolver()

    def expand(s):
        if s.state_id == "A":
            return [ProblemState("B", cost=1.0)]
        if s.state_id == "B":
            return [ProblemState("C", cost=1.0)]
        return []

    result = solver.solve(ProblemState("A"),
                          is_goal=lambda s: s.state_id == "C",
                          expand=expand)
    assert result.found
    assert result.path == ["A", "B", "C"]


def test_no_solution():
    from problem_solver import UniversalProblemSolver, ProblemState
    solver = UniversalProblemSolver(max_iterations=10)
    result = solver.solve(ProblemState("X"),
                          is_goal=lambda s: s.state_id == "GOAL",
                          expand=lambda s: [])
    assert not result.found


def test_solver_stats():
    from problem_solver import UniversalProblemSolver
    solver = UniversalProblemSolver()
    stats = solver.solver_stats()
    assert "solves" in stats
    assert stats["solves"] == 0
