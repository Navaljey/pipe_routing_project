% ============================================================================
% 3D Pipe Routing Model - MiniZinc
% ============================================================================
% 이 모델은 3D 공간에서 파이프 경로를 찾는 제약 최적화 문제입니다.
% 백엔드 솔버: COIN-OR CBC, SCIP (오픈소스)
% ============================================================================

include "globals.mzn";

% ----------------------------------------------------------------------------
% 입력 파라미터
% ----------------------------------------------------------------------------

% 최대 구부림 개수
int: MAX_BENDS;

% 격자 크기
int: GRID_X;
int: GRID_Y;
int: GRID_Z;

% 시작 위치와 목표 위치 [x, y, z]
array[1..3] of int: start_pos;
array[1..3] of int: goal_pos;

% 파이프 지름 (미터)
float: diameter;

% 장애물 개수와 위치
% obstacles[i] = [x_min, y_min, z_min, x_max, y_max, z_max]
int: num_obstacles;
array[1..num_obstacles, 1..6] of int: obstacles;

% ----------------------------------------------------------------------------
% 상수
% ----------------------------------------------------------------------------

% 구부림 페널티 (각 구부림당 추가 비용)
float: BEND_PENALTY = 100.0;

% 높이 페널티 (높을수록 지지대 비용 증가)
float: HEIGHT_PENALTY = 10.0;

% 최소 세그먼트 길이 (구부림 반경 고려)
int: MIN_SEGMENT_LEN = ceil(diameter * 3.0);

% ----------------------------------------------------------------------------
% 결정 변수
% ----------------------------------------------------------------------------

% 최대 격자 크기 계산
int: MAX_GRID = max([GRID_X, GRID_Y, GRID_Z]);

% 구부림 위치들 (0번은 시작점, MAX_BENDS+1번은 끝점)
% bends[i] = [x, y, z]
array[0..MAX_BENDS+1, 1..3] of var 0..MAX_GRID: bends;

% 실제 사용된 구부림 개수
var 0..MAX_BENDS: num_bends_used;

% ----------------------------------------------------------------------------
% 제약 조건
% ----------------------------------------------------------------------------

% 1. 시작점과 끝점 고정
constraint bends[0, 1] = start_pos[1];
constraint bends[0, 2] = start_pos[2];
constraint bends[0, 3] = start_pos[3];

constraint bends[MAX_BENDS+1, 1] = goal_pos[1];
constraint bends[MAX_BENDS+1, 2] = goal_pos[2];
constraint bends[MAX_BENDS+1, 3] = goal_pos[3];

% 2. 축 평행 세그먼트 (한 번에 한 방향으로만 이동)
% 각 세그먼트는 X, Y, Z 중 하나의 축으로만 이동해야 함
constraint forall(i in 1..MAX_BENDS+1) (
    let {
        var int: dx = abs(bends[i,1] - bends[i-1,1]),
        var int: dy = abs(bends[i,2] - bends[i-1,2]),
        var int: dz = abs(bends[i,3] - bends[i-1,3])
    } in
    % X축 이동 또는 Y축 이동 또는 Z축 이동 또는 제자리
    (dx > 0 /\ dy = 0 /\ dz = 0) \/ 
    (dx = 0 /\ dy > 0 /\ dz = 0) \/
    (dx = 0 /\ dy = 0 /\ dz > 0) \\/
    (dx = 0 /\ dy = 0 /\ dz = 0)  % 중복 구부림 허용 (최적화 과정에서 제거됨)
);

% 3. 최소 세그먼트 길이 (구부림 반경 고려)
% 각 세그먼트는 최소 3*diameter 길이를 가져야 함
constraint forall(i in 1..MAX_BENDS+1) (
    let {
        var int: seg_len = abs(bends[i,1] - bends[i-1,1]) + 
                           abs(bends[i,2] - bends[i-1,2]) + 
                           abs(bends[i,3] - bends[i-1,3])
    } in
    % 세그먼트가 0이거나 최소 길이 이상
    seg_len = 0 \/ seg_len >= MIN_SEGMENT_LEN
);

% 4. 장애물 회피
% 각 구부림 위치가 장애물 내부에 있으면 안 됨
constraint forall(i in 0..MAX_BENDS+1) (
    forall(j in 1..num_obstacles) (
        % 구부림이 장애물 박스 밖에 있어야 함
        bends[i,1] < obstacles[j,1] \/ bends[i,1] > obstacles[j,4] \/
        bends[i,2] < obstacles[j,2] \/ bends[i,2] > obstacles[j,5] \/
        bends[i,3] < obstacles[j,3] \/ bends[i,3] > obstacles[j,6]
    )
);

% 5. 격자 범위 내에 있어야 함
constraint forall(i in 0..MAX_BENDS+1) (
    bends[i,1] >= 0 /\ bends[i,1] <= GRID_X /\
    bends[i,2] >= 0 /\ bends[i,2] <= GRID_Y /\
    bends[i,3] >= 0 /\ bends[i,3] <= GRID_Z
);

% 6. 구부림 개수 계산
% 방향이 바뀌는 지점을 세어야 함
constraint num_bends_used = sum(i in 1..MAX_BENDS) (
    bool2int(
        % i번째와 i+1번째 구부림이 다른 위치에 있으면 구부림으로 간주
        bends[i,1] != bends[i+1,1] \/
        bends[i,2] != bends[i+1,2] \/
        bends[i,3] != bends[i+1,3]
    )
);

% ----------------------------------------------------------------------------
% 목적 함수: 총 비용 최소화
% ----------------------------------------------------------------------------

% 총 길이 계산 (유클리드 거리)
var float: total_length = sum(i in 1..MAX_BENDS+1) (
    sqrt(int2float(
        (bends[i,1] - bends[i-1,1]) * (bends[i,1] - bends[i-1,1]) +
        (bends[i,2] - bends[i-1,2]) * (bends[i,2] - bends[i-1,2]) +
        (bends[i,3] - bends[i-1,3]) * (bends[i,3] - bends[i-1,3])
    ))
);

% 평균 높이 계산 (지지대 비용 추정)
var float: avg_height = sum(i in 0..MAX_BENDS+1) (
    int2float(bends[i,3])
) / int2float(MAX_BENDS + 2);

% 총 비용 = 길이*지름 + 구부림 페널티 + 높이 페널티
var float: total_cost = 
    total_length * diameter + 
    BEND_PENALTY * int2float(num_bends_used) +
    HEIGHT_PENALTY * avg_height;

% 최소화 목표
solve minimize total_cost;

% ----------------------------------------------------------------------------
% 출력
% ----------------------------------------------------------------------------

output [
    "=== 3D Pipe Routing Solution ===\n",
    "Total Cost: ", show(total_cost), "\n",
    "Total Length: ", show(total_length), " m\n",
    "Number of Bends: ", show(num_bends_used), "\n",
    "Average Height: ", show(avg_height), " m\n\n",
    "Path (grid coordinates):\n"
] ++
[
    "  Point ", show(i), ": (", 
    show(bends[i,1]), ", ", 
    show(bends[i,2]), ", ", 
    show(bends[i,3]), ")\n"
    | i in 0..MAX_BENDS+1
    where i = 0 \/ i = MAX_BENDS+1 \/ 
          (bends[i,1] != bends[i+1,1] \/ 
           bends[i,2] != bends[i+1,2] \/ 
           bends[i,3] != bends[i+1,3])
];
