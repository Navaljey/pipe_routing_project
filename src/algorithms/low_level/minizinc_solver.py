import os
from datetime import timedelta
from minizinc import Instance, Model, Solver

class MiniZincSolver:
    def __init__(self, environment, solver_name="cbc"):
        self.environment = environment
        self.solver_name = solver_name
        self.timeout = 60
        self.max_bends = 20
        self.bend_penalty = 5
        self._load_model()

    def _load_model(self):
        model_str = """
        include "globals.mzn";
        int: MAX_BENDS; int: GRID_X; int: GRID_Y; int: GRID_Z;
        array[1..3] of int: start_pos; array[1..3] of int: goal_pos;
        int: BEND_PENALTY; int: num_obstacles;
        array[1..num_obstacles, 1..6] of int: obstacles;

        array[0..MAX_BENDS+1, 1..3] of var 0..max([GRID_X, GRID_Y, GRID_Z]): bends;

        var int: total_dist = sum(i in 1..MAX_BENDS+1) (
            abs(bends[i,1]-bends[i-1,1]) + abs(bends[i,2]-bends[i-1,2]) + abs(bends[i,3]-bends[i-1,3])
        );
        var int: actual_bends = sum(i in 1..MAX_BENDS) (
            bool2int(sum(j in 1..3)(bends[i,j] != bends[i-1,j]) > 0)
        );

        constraint bends[0,1]=start_pos[1] /\ bends[0,2]=start_pos[2] /\ bends[0,3]=start_pos[3];
        constraint bends[MAX_BENDS+1,1]=goal_pos[1] /\ bends[MAX_BENDS+1,2]=goal_pos[2] /\ bends[MAX_BENDS+1,3]=goal_pos[3];

        % [수정] 장애물 관통 방지 및 파이프 두께를 고려한 안전 이격(+1) 적용
        constraint forall(i in 1..MAX_BENDS+1, j in 1..num_obstacles) (
            (min(bends[i-1,1], bends[i,1]) >= (obstacles[j,4] + 1) \/ max(bends[i-1,1], bends[i,1]) <= (obstacles[j,1] - 1)) \/
            (min(bends[i-1,2], bends[i,2]) >= (obstacles[j,5] + 1) \/ max(bends[i-1,2], bends[i,2]) <= (obstacles[j,2] - 1)) \/
            (min(bends[i-1,3], bends[i,3]) >= (obstacles[j,6] + 1) \/ max(bends[i-1,3], bends[i,3]) <= (obstacles[j,3] - 1))
        );

        constraint forall(i in 1..MAX_BENDS+1) (
            sum(j in 1..3)(bool2int(bends[i,j] != bends[i-1,j])) <= 1
        );

        solve minimize total_dist + (actual_bends * BEND_PENALTY);
        """
        self.model = Model()
        self.model.add_string(model_str)
        try:
            self.solver = Solver.lookup(self.solver_name)
        except:
            self.solver = Solver.lookup("gecode")

    def solve(self, pipe, obstacles_pipes_paths=None):
        instance = Instance(self.solver, self.model)
        instance["MAX_BENDS"] = self.max_bends
        instance["BEND_PENALTY"] = self.bend_penalty
        instance["GRID_X"] = int(self.environment.grid_size[0])
        instance["GRID_Y"] = int(self.environment.grid_size[1])
        instance["GRID_Z"] = int(self.environment.grid_size[2])
        instance["start_pos"] = [int(p) for p in pipe.start]
        instance["goal_pos"] = [int(p) for p in pipe.goal]
        instance["num_obstacles"] = len(self.environment.obstacles)
        instance["obstacles"] = [[int(o.min_corner[0]), int(o.min_corner[1]), int(o.min_corner[2]), 
                                  int(o.max_corner[0]), int(o.max_corner[1]), int(o.max_corner[2])] for o in self.environment.obstacles]
        
        result = instance.solve(timeout=timedelta(seconds=self.timeout))
        if result.status.has_solution():
            return [(float(b[0]), float(b[1]), float(b[2])) for b in result["bends"]]
        return None