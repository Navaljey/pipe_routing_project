import argparse
import sys
import os
import time
import json
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.environment.instance_loader import InstanceLoader
from src.algorithms.low_level.minizinc_solver import MiniZincSolver
from src.algorithms.high_level.pbs import PBS

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--instance', type=str, default='small')
    parser.add_argument('--timeout', type=int, default=900)
    parser.add_argument('--max-bends', type=int, default=20)
    args = parser.parse_args()

    loader = InstanceLoader()
    environment, pipes = loader.load_instance(args.instance)

    print("\n" + "═"*70)
    print("  [SYSTEM] 3D Pipe Routing Solver (Conflict Diameter Enabled)")
    print("═"*70)

    solver = MiniZincSolver(environment)
    solver.max_bends = args.max_bends
    pbs = PBS(environment, solver)

    best_plan = None
    min_missing = len(pipes)
    start_time = time.time()

    print("\n▶ [STEP 1] 탐색 시작 (직경 기반 충돌 회피 활성)")
    for i in range(1, 101):
        elapsed = time.time() - start_time
        if elapsed > args.timeout: 
            break

        print(f"  [Round {i:03d}] 계산 중... ({int(elapsed)}초 경과)", end="\r")
        
        try:
            # [수정] PBS에 pipes 리스트를 넘겨 직경 정보를 활용하게 함
            current_plan = pbs.solve(pipes, timeout=60)
            if current_plan:
                missing = sum(1 for p in current_plan.values() if p is None)
                if missing < min_missing:
                    min_missing = missing
                    best_plan = current_plan
                    print(f"\n  => ★ Update! {len(pipes)-missing}/{len(pipes)}개 배치 성공 ({int(elapsed)}s)")
                if min_missing == 0: break
        except Exception as e:
            continue

    if best_plan:
        result_data = {str(k): v for k, v in best_plan.items() if v is not None}
        with open("routing_result.json", "w") as f:
            json.dump(result_data, f, indent=4)
        print(f"\n[저장] 경로 데이터가 'routing_result.json'으로 저장되었습니다.")

if __name__ == "__main__":
    main()