# Anaconda 환경 설정 가이드

## 문제 상황

일반 Python과 Anaconda Python이 다른 경우, MiniZinc 패키지 인식 문제가 발생할 수 있습니다.

### 확인 방법

```bash
# 일반 명령 프롬프트
python --version
# 출력: Python 3.9.x

# Anaconda Prompt
python --version
# 출력: Python 3.11.x (다를 수 있음)
```

## 해결 방법 1: Anaconda 가상환경 사용 (권장)

### 1단계: 새 가상환경 생성

```bash
# Anaconda Prompt 실행 후
conda create -n pipe_routing python=3.9
```

### 2단계: 환경 활성화

```bash
conda activate pipe_routing
```

### 3단계: 패키지 설치

```bash
# 기본 패키지
pip install numpy scipy pandas matplotlib seaborn plotly

# MiniZinc
pip install minizinc

# OR-Tools (선택)
pip install ortools

# 테스트 및 유틸리티
pip install pytest tabulate tqdm
```

### 4단계: 실행

```bash
# 환경이 활성화된 상태에서
cd C:\Users\naval\MyReviewForPaper\pipe_routing_project
python main.py --create-sample
python main.py --instance small --solver minizinc --minizinc-backend cbc
```

### 5단계: 환경 비활성화 (작업 끝난 후)

```bash
conda deactivate
```

## 해결 방법 2: requirements.txt로 일괄 설치

### requirements.txt 수정 (Anaconda 호환)

프로젝트 루트의 `requirements.txt` 사용:

```bash
conda activate pipe_routing
pip install -r requirements.txt
```

## 해결 방법 3: conda로 패키지 설치

일부 패키지는 conda로 설치하는 것이 더 안정적입니다:

```bash
conda activate pipe_routing

# conda로 설치 가능한 것들
conda install numpy scipy pandas matplotlib seaborn

# pip으로 설치해야 하는 것들
pip install minizinc plotly ortools tabulate tqdm pytest
```

## MiniZinc 설치 확인

### 1. Python 패키지 확인

```bash
conda activate pipe_routing
python -c "import minizinc; print('MiniZinc Python OK')"
```

### 2. MiniZinc IDE 확인

```bash
# 어느 명령 프롬프트에서든
minizinc --version
minizinc --solvers
```

**중요**: MiniZinc IDE는 Python 환경과 별개로 시스템 전역에 설치됩니다.

## 일반 명령 프롬프트에서도 Anaconda 환경 사용

### Windows

```bash
# 방법 1: Anaconda Prompt 대신 일반 cmd 사용
C:\Users\naval\anaconda3\Scripts\activate.bat
conda activate pipe_routing

# 방법 2: Anaconda를 PATH에 추가 (재부팅 필요)
# Anaconda 설치 시 "Add to PATH" 옵션 선택
```

### VSCode나 다른 IDE에서 사용

```json
// VSCode settings.json
{
    "python.defaultInterpreterPath": "C:\\Users\\naval\\anaconda3\\envs\\pipe_routing\\python.exe"
}
```

## 전체 설치 스크립트 (Anaconda)

### Windows Anaconda Prompt

```bash
# 1. 환경 생성
conda create -n pipe_routing python=3.9 -y

# 2. 환경 활성화
conda activate pipe_routing

# 3. 기본 패키지 (conda)
conda install numpy scipy pandas matplotlib seaborn -y

# 4. 추가 패키지 (pip)
pip install plotly minizinc ortools tabulate tqdm pytest pytest-cov

# 5. 프로젝트로 이동
cd C:\Users\naval\MyReviewForPaper\pipe_routing_project

# 6. 샘플 생성 및 테스트
python main.py --create-sample
python main.py --instance small --solver astar

# 7. MiniZinc 테스트 (MiniZinc IDE 설치 후)
python main.py --instance small --solver minizinc --minizinc-backend cbc
```

## 환경 관리 명령어

```bash
# 환경 목록 보기
conda env list

# 환경 활성화
conda activate pipe_routing

# 환경 비활성화
conda deactivate

# 환경 삭제 (필요시)
conda env remove -n pipe_routing

# 설치된 패키지 목록
conda list
pip list
```

## 문제 해결

### "conda: command not found"

**원인**: Anaconda가 PATH에 없음

**해결**:
```bash
# Windows
set PATH=%PATH%;C:\Users\naval\anaconda3\Scripts
set PATH=%PATH%;C:\Users\naval\anaconda3

# 또는 Anaconda Prompt 사용
```

### "No module named 'minizinc'"

**원인**: 잘못된 Python 환경에서 실행

**해결**:
```bash
# 올바른 환경 활성화 확인
conda activate pipe_routing
python -c "import sys; print(sys.executable)"
# 출력: C:\Users\naval\anaconda3\envs\pipe_routing\python.exe

# minizinc 재설치
pip uninstall minizinc
pip install minizinc
```

### MiniZinc 모델 오류: "no function max(int,int,int)"

**원인**: MiniZinc 문법 오류 (이미 수정됨)

**해결**: 최신 `pipe_routing_model.mzn` 파일 사용
```minizinc
% 수정 전 (오류)
var 0..max(GRID_X, max(GRID_Y, GRID_Z)): bends;

% 수정 후 (정상)
int: MAX_GRID = max([GRID_X, GRID_Y, GRID_Z]);
var 0..MAX_GRID: bends;
```

### ImportError: DLL load failed

**원인**: numpy, scipy 등의 바이너리 호환성 문제

**해결**:
```bash
# conda로 재설치
conda activate pipe_routing
conda uninstall numpy scipy
conda install numpy scipy -c conda-forge
```

## 권장 워크플로우

### 프로젝트 시작 시

```bash
# 1. Anaconda Prompt 실행
# 2. 환경 활성화
conda activate pipe_routing

# 3. 프로젝트 디렉토리로 이동
cd C:\Users\naval\MyReviewForPaper\pipe_routing_project

# 4. 실행
python main.py --instance small --solver minizinc
```

### VSCode에서 작업 시

1. VSCode에서 프로젝트 폴더 열기
2. `Ctrl+Shift+P` → "Python: Select Interpreter"
3. `pipe_routing` 환경 선택
4. 터미널에서 자동으로 환경 활성화됨

## 요약

| 상황 | 해결책 |
|------|--------|
| MiniZinc 인식 안 됨 | Anaconda 환경 사용 |
| 두 Python 버전 충돌 | conda 가상환경 생성 |
| 패키지 설치 오류 | conda + pip 혼용 |
| MiniZinc 모델 오류 | 최신 .mzn 파일 사용 |

**핵심**: Anaconda 가상환경을 만들어서 격리된 환경에서 작업하는 것이 가장 안전합니다!
