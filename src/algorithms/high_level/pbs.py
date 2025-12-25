import time
import random
import numpy as np
from copy import deepcopy

class PBS:
    def __init__(self, environment, solver, max_missing=0, conflict_policy=2):
        self.env = environment
        self.solver = solver
        self.max_missing = max_missing
        self.conflict_policy = conflict_policy

    def solve(self, pipes, timeout=300, one_dive=False, initial_plan=None):
        start_time = time.time()
        
        if initial_plan is None:
            current_plan = {}
            for pipe in pipes:
                current_plan[pipe.id] = self.solver.solve(pipe)
        else:
            current_plan = deepcopy(initial_plan)

        missing_count = sum(1 for p in current_plan.values() if p is None)
        
        root = {
            'constraints': [],
            'plan': current_plan,
            'missing_count': missing_count,
            'cost': self._calculate_total_cost(current_plan)
        }
        
        stack = [root]
        best_plan = root['plan']
        min_missing = missing_count

        while stack and (time.time() - start_time < timeout):
            node = stack.pop()
            
            # [수정] 충돌 체크 시 파이프 객체 리스트를 전달하여 직경을 확인
            conflict = self._get_first_conflict(node['plan'], pipes)
            
            if not conflict and node['missing_count'] <= self.max_missing:
                return node['plan']

            if conflict:
                p1_id, p2_id = conflict['p1'], conflict['p2']
                branches = [(p1_id, p2_id), (p2_id, p1_id)]
                
                if self.conflict_policy == 2:
                    random.shuffle(branches)

                for higher, lower in branches:
                    new_constraints = node['constraints'] + [(higher, lower)]
                    updated_plan = self._replan(node['plan'], lower, new_constraints, pipes)
                    
                    new_missing = sum(1 for p in updated_plan.values() if p is None)
                    
                    if new_missing <= self.max_missing:
                        new_node = {
                            'constraints': new_constraints,
                            'plan': updated_plan,
                            'missing_count': new_missing,
                            'cost': self._calculate_total_cost(updated_plan)
                        }
                        stack.append(new_node)
                        
                        if new_missing < min_missing:
                            min_missing = new_missing
                            best_plan = updated_plan
                        if one_dive: break 
            
            if one_dive and len(stack) > 1:
                stack = [stack[-1]]

        return best_plan

    # [핵심 수정] 물리적 직경을 고려한 간섭 판단 로직
    def _get_first_conflict(self, plan, pipes):
        pipe_dict = {p.id: p for p in pipes}
        pipe_ids = list(plan.keys())
        
        for i in range(len(pipe_ids)):
            for j in range(i + 1, len(pipe_ids)):
                id1, id2 = pipe_ids[i], pipe_ids[j]
                p1_path, p2_path = plan[id1], plan[id2]
                
                if p1_path and p2_path:
                    # 안전 이격 거리 = (반지름1 + 반지름2)
                    safe_dist = (pipe_dict[id1].diameter + pipe_dict[id2].diameter) / 2.0
                    
                    for pt1 in p1_path:
                        for pt2 in p2_path:
                            # 유클리드 거리 계산 후 직경 이내면 충돌로 간주
                            dist = np.linalg.norm(np.array(pt1) - np.array(pt2))
                            if dist < safe_dist: 
                                return {'p1': id1, 'p2': id2}
        return None

    def _calculate_total_cost(self, plan):
        return sum(len(p) for p in plan.values() if p)

    def _replan(self, current_plan, target_id, constraints, all_pipes):
        new_plan = deepcopy(current_plan)
        target_pipe = next(p for p in all_pipes if p.id == target_id)
        
        higher_priority_paths = []
        for higher, lower in constraints:
            if lower == target_id and new_plan[higher]:
                higher_priority_paths.append(new_plan[higher])
        
        new_plan[target_id] = self.solver.solve(target_pipe, obstacles_pipes_paths=higher_priority_paths)
        return new_plan