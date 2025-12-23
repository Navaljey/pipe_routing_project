# MiniZinc 설치 가이드

## MiniZinc란?

MiniZinc는 제약 최적화 문제를 모델링하는 언어입니다. 파이프 경로 탐색을 제약 만족 문제(CSP)로 표현하여 더 최적화된 경로를 찾을 수 있습니다.

### A* vs MiniZinc 비교

| 특성 | A* (기본) | MiniZinc |
|------|----------|----------|
| 설치 | 쉬움 (pip만) | 중간 (별도 설치) |
| 속도 | 빠름 (초 단위) | 느림 (분 단위) |
| 경로 품질 | 준최적 | 더 최적 |
| 라이선스 | 무료 | 무료 (오픈소스) |

## 설치 방법

### 1단계: Python 라이브러리 설치

```bash
pip install minizinc
```

### 2단계: MiniZinc IDE 설치

#### Windows
1. [MiniZinc 다운로드 페이지](https://www.minizinc.org/software.html) 방문
2. "MiniZincIDE-X.X.X-bundled-setup-win64.exe" 다운로드
3. 설치 프로그램 실행
4. 기본 설정으로 설치 (모든 솔버 포함)

#### macOS
1. [MiniZinc 다운로드 페이지](https://www.minizinc.org/software.html) 방문
2. "MiniZincIDE-X.X.X-bundled.dmg" 다운로드
3. DMG 파일 마운트 후 Applications 폴더로 드래그

#### Linux (Ubuntu/Debian)
```bash
# 방법 1: 패키지 매니저
sudo apt update
sudo apt install minizinc

# 방법 2: Snap
sudo snap install minizinc --classic

# 방법 3: AppImage
wget https://github.com/MiniZinc/MiniZincIDE/releases/download/X.X.X/MiniZincIDE-X.X.X-x86_64.AppImage
chmod +x MiniZincIDE-X.X.X-x86_64.AppImage
./MiniZincIDE-X.X.X-x86_64.AppImage
```

### 3단계: 설치 확인

```bash
# MiniZinc 버전 확인
minizinc --version

# 사용 가능한 솔버 확인
minizinc --solvers
```

**예상 출력:**
```
Available solver configurations:
  Chuffed 0.10.4
  COIN-OR CBC 2.10.5
  Gecode 6.3.0
  SCIP 8.0.0
  ...
```

## 백엔드 솔버 선택

MiniZinc는 여러 백엔드 솔버를 지원합니다. 우리 프로젝트는 오픈소스 솔버만 사용합니다.

### COIN-OR CBC (권장)
- **특징**: MIP(Mixed Integer Programming) 솔버
- **장점**: 빠른 속도, 안정적
- **단점**: 큰 문제에서는 메모리 많이 사용
- **사용**: `--minizinc-backend cbc`

```bash
python main.py --solver minizinc --minizinc-backend cbc
```

### SCIP
- **특징**: 강력한 제약 최적화 솔버
- **장점**: 복잡한 제약 처리에 강함, 더 최적화된 해
- **단점**: CBC보다 느림
- **사용**: `--minizinc-backend scip`

```bash
python main.py --solver minizinc --minizinc-backend scip
```

### Chuffed
- **특징**: Lazy Clause Generation CP 솔버
- **장점**: 제약 전파에 강함
- **단점**: MIP 문제에는 적합하지 않음
- **사용**: `--minizinc-backend chuffed`

### Gecode
- **특징**: 전통적인 CP 솔버
- **장점**: 교육용으로 좋음
- **단점**: 큰 문제에서 느림
- **사용**: `--minizinc-backend gecode`

## 성능 비교 가이드

### Small 인스턴스 (8개 파이프)

```bash
# A* (빠름, 10-20초)
python main.py --instance small --solver astar

# MiniZinc+CBC (중간, 1-2분)
python main.py --instance small --solver minizinc --minizinc-backend cbc

# MiniZinc+SCIP (느림, 3-5분, 더 최적)
python main.py --instance small --solver minizinc --minizinc-backend scip
```

### Medium 인스턴스 (23-36개 파이프)

```bash
# A* (빠름, 1-2분)
python main.py --instance medium_1 --solver astar --timeout 600

# MiniZinc+CBC (권장, 10-15분)
python main.py --instance medium_1 --solver minizinc --minizinc-backend cbc --timeout 1800

# MiniZinc+SCIP (최고 품질, 30분+)
python main.py --instance medium_1 --solver minizinc --minizinc-backend scip --timeout 3600
```

## 문제 해결

### 오류: "No MiniZinc solver found"

**원인**: MiniZinc IDE가 설치되지 않았거나 PATH에 없음

**해결책**:
```bash
# Windows: 환경 변수에 추가
setx PATH "%PATH%;C:\Program Files\MiniZinc IDE (bundled)"

# Mac/Linux: .bashrc 또는 .zshrc에 추가
export PATH="/Applications/MiniZincIDE.app/Contents/Resources:$PATH"

# 또는 MiniZinc 재설치
```

### 오류: "Solver 'cbc' not found"

**원인**: CBC 솔버가 설치되지 않음

**해결책**:
```bash
# MiniZinc bundled 버전 재설치 (모든 솔버 포함)
# 또는 다른 솔버 사용
python main.py --solver minizinc --minizinc-backend gecode
```

### 오류: "Model timeout"

**원인**: 문제가 너무 복잡하거나 시간 제한이 짧음

**해결책**:
```bash
# 시간 제한 늘리기
python main.py --solver minizinc --timeout 3600

# 또는 A* 솔버 사용
python main.py --solver astar
```

### 느린 성능

**해결책**:
1. 더 빠른 솔버 사용 (SCIP → CBC)
2. 격자 해상도 줄이기 (instance JSON의 grid_resolution 증가)
3. MAX_BENDS 줄이기 (MiniZinc 모델에서 6 → 4)
4. A* 솔버로 전환

## 권장 사용법

### 빠른 프로토타입 / 테스트
```bash
python main.py --solver astar
```

### 연구 / 논문 재현
```bash
python main.py --solver minizinc --minizinc-backend cbc --timeout 3600
```

### 최고 품질 필요
```bash
python main.py --solver minizinc --minizinc-backend scip --timeout 7200
```

### 실시간 / 인터랙티브
```bash
python main.py --solver astar --timeout 60
```

## 참고 자료

- [MiniZinc 공식 문서](https://www.minizinc.org/doc-latest/en/index.html)
- [MiniZinc Python 라이브러리](https://minizinc-python.readthedocs.io/)
- [COIN-OR CBC](https://github.com/coin-or/Cbc)
- [SCIP](https://www.scipopt.org/)
