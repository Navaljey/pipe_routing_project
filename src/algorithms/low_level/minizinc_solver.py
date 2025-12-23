"""
MiniZinc 기반 파이프 경로 탐색 솔버 (최종 수정본)
문법 오류 수정 및 안정성 강화
"""

import os
import time
import sys
from datetime import timedelta
from pathlib import Path
from .base_solver import BaseSolver

try:
    import minizinc
    from minizinc import Instance, Model, Solver
    MINIZINC_AVAILABLE = True
except ImportError:
    MINIZINC_AVAILABLE = False


class MiniZincSolver(BaseSolver):
    def __init__(self, environment, solver_name="cbc", debug=True):
        self.debug = debug
        self.solver_name = solver_name
        self.timeout = 180
        self.model = None
        self.solver = None
        
        super().__init__(environment)
        
        if not MINIZINC_AVAILABLE:
            raise ImportError("minizinc 패키지를 찾을 수 없습니다.")

        self._debug_print("=" * 60)
        self._debug_print(f"MiniZinc 솔버 초기화 (백엔드: {self.solver_name})")
        
        self._load_model()
        self._load_solver()

    def _debug_print(self, msg):
        if self.debug:
            print(f"[DEBUG] {msg}")

    def _load_model(self):
        """문법 오류가 해결된 인라인 모델 생성"""
        self._debug_print("1. MiniZinc 모델 생성 중...")
        
        # 문법 오류를 방지하기 위해 가장 표준적인 MiniZinc 문법 사용
        model_str = """
        include "globals.mzn";

        int: MAX_BENDS;
        int: GRID_X; int: GRID_Y; int: GRID_Z;
        array[1..3] of int: start_pos;
        array[1..3] of int: goal_pos;
        float: diameter;
        int: num_obstacles;
        array[1..num_obstacles, 1..6] of int: obstacles;

        % 결정 변수
        array[0..MAX_BENDS+1, 1..3] of var 0..max([GRID_X, GRID_Y, GRID_Z]): bends;

        % 제약 조건 1: 시작과 끝
        constraint bends[0, 1] = start_pos[1];
        constraint bends[0, 2] = start_pos[2];
        constraint bends[0, 3] = start_pos[3];
        constraint bends[MAX_BENDS+1, 1] = goal_pos[1];
        constraint bends[MAX_BENDS+1, 2] = goal_pos[2];
        constraint bends[MAX_BENDS+1, 3] = goal_pos[3];

        % 제약 조건 2: 직교 이동 (dx, dy, dz 중 하나만 0보다 커야 함)
        constraint forall(i in 1..MAX_BENDS+1) (
            let {
                var int: dx = abs(bends[i,1] - bends[i-1,1]),
                var int: dy = abs(bends[i,2] - bends[i-1,2]),
                var int: dz = abs(bends[i,3] - bends[i-1,3])
            } in
            (dx >= 0 /\ dy = 0 /\ dz = 0) \/ 
            (dx = 0 /\ dy >= 0 /\ dz = 0) \/
            (dx = 0 /\ dy = 0 /\ dz >= 0)
        );

        % 제약 조건 3: 장애물 회피 (각 점이 장애물 박스 밖에 있도록)
        constraint forall(i in 0..MAX_BENDS+1) (
            forall(j in 1..num_obstacles) (
                bends[i,1] < obstacles[j,1] \/ bends[i,1] > obstacles[j,4] \/
                bends[i,2] < obstacles[j,2] \/ bends[i,2] > obstacles[j,5] \/
                bends[i,3] < obstacles[j,3] \/ bends[i,3] > obstacles[j,6]
            )
        );

        % 목적 함수: 맨해튼 거리 최소화
        solve minimize sum(i in 1..MAX_BENDS+1) (
            abs(bends[i,1] - bends[i-1,1]) + 
            abs(bends[i,2] - bends[i-1,2]) + 
            abs(bends[i,3] - bends[i-1,3])
        );
        """
        self.model = Model()
        self.model.add_string(model_str)
        self._debug_print("   ✓ 모델 생성 완료")

    def _load_solver(self):
        try:
            self.solver = Solver.lookup(self.solver_name)
        except:
            self.solver = Solver.lookup("gecode")
            self.solver_name = "gecode"

    def solve(self, pipe, obstacles_pipes=None):
        self._debug_print(f"[탐색 시작] 파이프 {pipe.id}")
        try:
            instance = Instance(self.solver, self.model)
            instance["MAX_BENDS"] = 5  # 계산 속도를 위해 축소
            instance["GRID_X"] = int(self.environment.grid_size[0])
            instance["GRID_Y"] = int(self.environment.grid_size[1])
            instance["GRID_Z"] = int(self.environment.grid_size[2])
            instance["start_pos"] = [int(p) for p in pipe.start]
            instance["goal_pos"] = [int(p) for p in pipe.goal]
            instance["diameter"] = float(pipe.diameter)
            
            # 장애물 변환
            obs_list = []
            for obs in self.environment.obstacles:
                obs_list.append([
                    int(obs.min_corner[0]), int(obs.min_corner[1]), int(obs.min_corner[2]),
                    int(obs.max_corner[0]), int(obs.max_corner[1]), int(obs.max_corner[2])
                ])
            
            if not obs_list:
                obs_list = [[-1, -1, -1, -1, -1, -1]]
            
            instance["num_obstacles"] = len(obs_list)
            instance["obstacles"] = obs_list
            
            result = instance.solve(timeout=timedelta(seconds=self.timeout))
            
            if result.status.has_solution():
                bends = result["bends"]
                path = []
                for i in range(len(bends)):
                    path.append((float(bends[i][0]), float(bends[i][1]), float(bends[i][2])))
                self._debug_print("   ✓ 경로 탐색 성공")
                return path
            return None
        except Exception as e:
            self._debug_print(f"   ✗ 실행 에러: {e}")
            return None

    def set_timeout(self, timeout):
        self.timeout = timeout