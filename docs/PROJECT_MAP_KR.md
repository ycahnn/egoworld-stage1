# 프로젝트 전체 구조

이 문서는 EgoWorld Stage 1 재현 워크스페이스의 전체 구조, 실행 환경, 코드 파일 역할, 산출물 흐름, 실행 순서를 한국어로 정리합니다.

## 디렉터리 구조

- `inputs/`
  - 입력 exocentric RGB 이미지(`exo.jpg`)를 보관하는 폴더입니다.

- `outputs/`
  - 파이프라인에서 생성되는 모든 결과를 저장하는 폴더입니다.
  - 깊이, 포인트클라우드, MediaPipe 바운딩박스, HaMeR 출력, 스케일 정렬, P_exo 등이 여기에 포함됩니다.

- `scripts/`
  - 파이프라인 연결, 검증, 시각화, 정렬, P_exo 생성 같은 후처리와 보조 스크립트를 담습니다.

- `external/hamer/`
  - HaMeR 외부 리포지토리와 관련 환경이 있는 폴더입니다.
  - 이 폴더 안의 `.hamer`는 HaMeR 전용 Python 가상환경입니다.

- `requirements.txt`, `requirements-main-lock.txt`
  - 메인 파이프라인 `.venv`의 의존성입니다.

- `requirements-hamer.txt`, `requirements-hamer-lock.txt`
  - HaMeR 환경 `external/hamer/.hamer`의 의존성입니다.

- `docs/`
  - 한국어 및 영어 문서 파일을 저장하는 폴더입니다.

- 루트 수준 Python 스크립트
  - `infer_depth_pointcloud.py`, `infer_hand_bbox.py`, `crop_hands_from_bboxes.py`, `infer_hamer_from_bboxes.py`, `infer_hand_pose.py`, `visualize_pointcloud.py` 등이 있습니다.

## 실행 환경

이 워크스페이스는 두 개의 분리된 Python 환경을 사용합니다.

1. `.venv`
   - 메인 파이프라인용 환경입니다.
   - MoGe, MediaPipe, OpenCV, Open3D, NumPy 등을 설치해야 합니다.
   - 사용 대상: 깊이 추정, 포인트클라우드, MediaPipe 바운딩박스, 손 크롭, HaMeR 결과 검증, 손 깊이 렌더링, 스케일 정렬, P_exo 생성, 워크스페이스 검증 등.

   PowerShell 예시:
   ```powershell
   Set-Location "c:\Users\Youngchan Ahn\Desktop\egoworld-stage1"
   .\.venv\Scripts\Activate.ps1
   .\.venv\Scripts\python.exe --version
   ```

2. `external/hamer/.hamer`
   - HaMeR 전용 환경입니다.
   - HaMeR 모델과 MANO 파일을 로드하고 HaMeR 추론을 실행하는 데만 사용합니다.
   - 메인 `.venv`와 분리된 환경이어야 합니다.

   PowerShell 예시:
   ```powershell
   Set-Location "c:\Users\Youngchan Ahn\Desktop\egoworld-stage1\external\hamer"
   .\.hamer\Scripts\Activate.ps1
   .\.hamer\Scripts\python.exe --version
   ```

## 코드 파일 설명

### 루트 코드 파일

#### `infer_depth_pointcloud.py`
- 경로: `infer_depth_pointcloud.py`
- 목적: 입력 exo 이미지를 받아 깊이 맵과 컬러 포인트클라우드를 생성합니다.
- 입력: `--image inputs/exo.jpg`
- 출력: `outputs/depth_raw.npy`, `outputs/depth_vis.png`, `outputs/exo_point_cloud.ply`, `outputs/K_exo.npy`, `outputs/depth_intrinsics.json`, `outputs/depth_gray.png`, `outputs/depth_mask.png`
- 환경: `.venv`
- 명령 예시:
  ```powershell
  .\.venv\Scripts\python.exe infer_depth_pointcloud.py --image inputs/exo.jpg --out outputs --depth_model moge
  ```
- 분류: 최종 파이프라인 코드

#### `infer_hand_bbox.py`
- 경로: `infer_hand_bbox.py`
- 목적: MediaPipe Hands를 사용해 손 바운딩박스를 감지합니다.
- 입력: `--image inputs/exo.jpg`
- 출력: `outputs/hand_bboxes.json`, `outputs/hand_bbox_debug.png`
- 환경: `.venv`
- 명령 예시:
  ```powershell
  .\.venv\Scripts\python.exe infer_hand_bbox.py --image inputs/exo.jpg --out outputs
  ```
- 분류: 최종 파이프라인 코드

#### `crop_hands_from_bboxes.py`
- 경로: `crop_hands_from_bboxes.py`
- 목적: MediaPipe 바운딩박스를 이용해 손 이미지를 크롭하고 메타데이터를 생성합니다.
- 입력: `--image inputs/exo.jpg`, `--bbox_json outputs/hand_bboxes.json`
- 출력: `outputs/hand_crops/hand_crops_metadata.json`, `outputs/hand_crops/*.png`, `outputs/hand_crops/crop_debug.png`
- 환경: `.venv`
- 명령 예시:
  ```powershell
  .\.venv\Scripts\python.exe crop_hands_from_bboxes.py --image inputs/exo.jpg --bbox_json outputs/hand_bboxes.json --out outputs/hand_crops
  ```
- 분류: 최종 파이프라인 코드

#### `infer_hamer_from_bboxes.py`
- 경로: `infer_hamer_from_bboxes.py`
- 목적: HaMeR를 통해 MediaPipe 바운딩박스에서 MANO 메쉬와 관절을 추출합니다.
- 입력: `--image inputs/exo.jpg`, `--bbox_json outputs/hand_bboxes.json`
- 출력: `outputs/hamer/hand_00_left_vertices.npy`, `outputs/hamer/hand_00_left_joints.npy`, `outputs/hamer/hand_00_left_faces.npy`, `outputs/hamer/hand_00_left_mesh.obj`, `outputs/hamer/hamer_metadata.json`, `outputs/hamer/hamer_raw_output_summary.json`, `outputs/hamer/hamer_bbox_debug.png`
- 환경: `external/hamer/.hamer`
- 명령 예시:
  ```powershell
  .\external\hamer\.hamer\Scripts\python.exe infer_hamer_from_bboxes.py --image inputs/exo.jpg --bbox_json outputs/hand_bboxes.json --out outputs/hamer
  ```
- 분류: 최종 파이프라인 코드

#### `visualize_pointcloud.py`
- 경로: `visualize_pointcloud.py`
- 목적: PLY 포인트클라우드를 Open3D 또는 matplotlib로 시각화합니다.
- 입력: `--ply outputs/exo_point_cloud.ply` 또는 다른 PLY 파일
- 출력: 화면 표시
- 환경: `.venv`
- 명령 예시:
  ```powershell
  .\.venv\Scripts\python.exe visualize_pointcloud.py --ply outputs/exo_point_cloud.ply
  ```
- 분류: 디버그/시각화 코드

#### `infer_hand_pose.py`
- 경로: `infer_hand_pose.py`
- 목적: placeholder 방식의 손 포즈 추정기입니다.
- 입력: `--image inputs/exo.jpg`
- 출력: `outputs/*` (placeholder 결과)
- 환경: `.venv`
- 명령 예시:
  ```powershell
  .\.venv\Scripts\python.exe infer_hand_pose.py --image inputs/exo.jpg --out outputs/hand_pose
  ```
- 분류: 실험/비최종 코드
- 주의: 현재 실제 파이프라인이 아닌 placeholder 추정기입니다.

### `scripts/` 폴더 코드

#### `scripts/verify_hamer_projection.py`
- 경로: `scripts/verify_hamer_projection.py`
- 목적: HaMeR 메쉬를 원본 exo 이미지 위에 투영하여 결과를 검증합니다.
- 입력: `--image inputs/exo.jpg`, `--hamer_dir outputs/hamer`, `--bbox_json outputs/hand_bboxes.json`
- 출력: `outputs/hamer_projection/final_projection_debug.png`, `outputs/hamer_projection/bbox_fallback_projection_debug.png`, `outputs/hamer_projection/final_projection_report.md`
- 환경: `.venv`
- 명령 예시:
  ```powershell
  .\.venv\Scripts\python.exe scripts/verify_hamer_projection.py --image inputs/exo.jpg --hamer_dir outputs/hamer --bbox_json outputs/hand_bboxes.json --out outputs/hamer_projection
  ```
- 분류: 최종/검증 코드

#### `scripts/render_hand_depth.py`
- 경로: `scripts/render_hand_depth.py`
- 목적: HaMeR 메쉬 정점과 카메라 정보를 사용해 손 깊이 맵을 렌더링합니다.
- 입력: `--image inputs/exo.jpg`, `--hamer_dir outputs/hamer`, `--bbox_json outputs/hand_bboxes.json`
- 출력: `outputs/hamer_depth/hand_depth.npy`, `outputs/hamer_depth/hand_depth_vis.png`, `outputs/hamer_depth/hand_mask.png`, `outputs/hamer_depth/hand_depth_debug.png`, `outputs/hamer_depth/hand_depth_report.md`
- 환경: `.venv`
- 명령 예시:
  ```powershell
  .\.venv\Scripts\python.exe scripts/render_hand_depth.py --image inputs/exo.jpg --hamer_dir outputs/hamer --bbox_json outputs/hand_bboxes.json --out outputs/hamer_depth
  ```
- 분류: 최종 파이프라인 코드

#### `scripts/scale_depth_with_hand.py`
- 경로: `scripts/scale_depth_with_hand.py`
- 목적: 손 깊이와 원본 exo 깊이를 맞춰 스케일을 계산하고, 스케일된 깊이 및 포인트클라우드를 생성합니다.
- 입력: `--image inputs/exo.jpg`, `--depth outputs/depth_raw.npy`, `--hand_depth outputs/hamer_depth/hand_depth.npy`, `--hand_mask outputs/hamer_depth/hand_mask.png`
- 출력: `outputs/scaled_depth/depth_scaled.npy`, `outputs/scaled_depth/depth_scaled_vis.png`, `outputs/scaled_depth/scale_valid_mask.png`, `outputs/scaled_depth/exo_point_cloud_scaled.ply`, `outputs/scaled_depth/scale_report.md`, `outputs/scaled_depth/scale_ratio_hist.png`
- 환경: `.venv`
- 명령 예시:
  ```powershell
  .\.venv\Scripts\python.exe scripts/scale_depth_with_hand.py --image inputs/exo.jpg --depth outputs/depth_raw.npy --hand_depth outputs/hamer_depth/hand_depth.npy --hand_mask outputs/hamer_depth/hand_mask.png --out outputs/scaled_depth
  ```
- 분류: 최종 파이프라인 코드

#### `scripts/export_p_exo_from_depth.py`
- 경로: `scripts/export_p_exo_from_depth.py`
- 목적: 2D MediaPipe 랜드마크와 스케일된 깊이를 사용해 최종 `P_exo` 3D 포즈를 생성합니다.
- 입력: `--image inputs/exo.jpg`, `--depth outputs/scaled_depth/depth_scaled.npy`, `--K outputs/K_exo.npy`
- 출력: `outputs/pose_depth/P_exo.npy`, `outputs/pose_depth/P_exo_2d.npy`, `outputs/pose_depth/P_exo_valid.npy`, `outputs/pose_depth/P_exo_metadata.json`, `outputs/pose_depth/P_exo_projection_debug.png`, `outputs/pose_depth/P_exo_report.md`
- 환경: `.venv`
- 명령 예시:
  ```powershell
  .\.venv\Scripts\python.exe scripts/export_p_exo_from_depth.py --image inputs/exo.jpg --depth outputs/scaled_depth/depth_scaled.npy --K outputs/K_exo.npy --out outputs/pose_depth
  ```
- 분류: 최종 파이프라인 코드

#### `scripts/render_p_exo_skeleton_on_black.py`
- 경로: `scripts/render_p_exo_skeleton_on_black.py`
- 목적: `P_exo` 스켈레톤을 검은 배경 위에 렌더링하여 시각화합니다.
- 입력: 기본값으로 `outputs/pose_depth/P_exo.npy`, `outputs/pose_depth/P_exo_2d.npy`, `outputs/pose_depth/P_exo_valid.npy`, `outputs/K_exo.npy`, `inputs/exo.jpg`
- 출력: `outputs/pose_depth/P_exo_skeleton_black.png`
- 환경: `.venv`
- 명령 예시:
  ```powershell
  .\.venv\Scripts\python.exe scripts/render_p_exo_skeleton_on_black.py
  ```
- 분류: 디버그/시각화 코드

#### `scripts/check_workspace_integrity.py`
- 경로: `scripts/check_workspace_integrity.py`
- 목적: 최종 필수 아웃풋 파일 존재 여부와 주요 `.npy` 형태를 검사합니다.
- 입력: 없음(루트 경로 기준 고정)
- 출력: 콘솔 메시지
- 환경: `.venv`
- 명령 예시:
  ```powershell
  .\.venv\Scripts\python.exe scripts/check_workspace_integrity.py
  ```
- 분류: 검증 코드

#### `scripts/check_project_state.py`
- 경로: `scripts/check_project_state.py`
- 목적: `.venv`와 HaMeR `.hamer` 환경에서 주요 라이브러리 임포트 및 주요 파일 존재 여부를 검사합니다.
- 입력: 없음
- 출력: `outputs/environment_report.md`
- 환경: `.venv` (HaMeR 환경도 하위 프로세스로 검사)
- 명령 예시:
  ```powershell
  .\.venv\Scripts\python.exe scripts/check_project_state.py
  ```
- 분류: 검증 코드

#### `scripts/click_depth_viewer.py`
- 경로: `scripts/click_depth_viewer.py`
- 목적: 깊이 영상의 픽셀을 클릭하여 깊이 값을 탐색하는 인터랙티브 뷰어입니다.
- 입력: `--image`, `--raw`, `--scaled`, `--hand`
- 출력: 화면 표시
- 환경: `.venv`
- 명령 예시:
  ```powershell
  .\.venv\Scripts\python.exe scripts/click_depth_viewer.py --image inputs/exo.jpg --raw outputs/depth_raw.npy --scaled outputs/scaled_depth/depth_scaled.npy --hand outputs/hamer_depth/hand_depth.npy
  ```
- 분류: 디버그/유틸리티 코드

## 산출물 파일 설명

### `outputs/` 일반 설명
- 이 폴더는 파이프라인의 모든 생성 결과를 저장합니다.
- 최종 산출물과 디버그/중간 산출물을 함께 포함하고 있습니다.
- 중요한 최종 산출물은 `outputs/scaled_depth/`와 `outputs/pose_depth/` 아래에 집중되어 있습니다.

#### `outputs/depth_raw.npy`
- 유형: NumPy 배열
- shape: (1367, 1229)
- 의미: 입력 exo 이미지에 대한 원시 깊이 값
- 생성: `infer_depth_pointcloud.py`
- 사용: `scale_depth_with_hand.py`에서 손 깊이와 정렬, `export_p_exo_from_depth.py`에서 2D 랜드마크 깊이 사용
- 분류: 최종/중간 산출물

#### `outputs/K_exo.npy`
- 유형: NumPy 배열
- shape: (3, 3)
- 의미: exocentric 카메라 내부 파라미터
- 생성: `infer_depth_pointcloud.py`
- 사용: `export_p_exo_from_depth.py`, `scripts/render_p_exo_skeleton_on_black.py`, 그 외 투영 관련 코드
- 분류: 최종 산출물

#### `outputs/depth_intrinsics.json`
- 유형: JSON
- 의미: `K_exo.npy`의 카메라 파라미터를 사람이 읽을 수 있는 형식으로 저장
- 생성: `infer_depth_pointcloud.py`
- 분류: 중간/디버그 산출물

#### `outputs/depth_vis.png`, `outputs/depth_gray.png`, `outputs/depth_mask.png`
- 유형: PNG 이미지
- 의미:
  - `depth_vis.png`: 깊이 값을 컬러맵으로 시각화
  - `depth_gray.png`: 회색조 깊이 시각화
  - `depth_mask.png`: 유효 깊이 픽셀 마스크
- 생성: `infer_depth_pointcloud.py` (`src/io_utils.save_depth_vis`)
- 분류: 디버그/시각화 산출물

#### `outputs/exo_point_cloud.ply`
- 유형: PLY 포인트클라우드
- 의미: `depth_raw.npy`와 입력 RGB로 생성한 exo 포인트클라우드
- 생성: `infer_depth_pointcloud.py`
- 사용: `visualize_pointcloud.py`로 확인, 스케일 정렬을 위한 참고 자료
- 분류: 중간 산출물

#### `outputs/hand_bboxes.json`
- 유형: JSON
- 의미: MediaPipe 손 바운딩박스 감지 결과
- 생성: `infer_hand_bbox.py`
- 사용: `crop_hands_from_bboxes.py`, `infer_hamer_from_bboxes.py`, `verify_hamer_projection.py`, `render_hand_depth.py`
- 분류: 최종/중간 산출물

#### `outputs/hand_bbox_debug.png`
- 유형: PNG 이미지
- 의미: 감지된 손 바운딩박스를 원본 이미지에 시각화
- 생성: `infer_hand_bbox.py`
- 분류: 디버그/시각화 산출물

#### `outputs/hand_crops/`
- 유형: 폴더
- 의미: 손 크롭 이미지와 크롭 메타데이터
- 생성: `crop_hands_from_bboxes.py`
- 사용: HaMeR 추론을 위해 손 크롭 확인에 사용
- 분류: 중간 산출물

#### `outputs/hamer/`
- 유형: 폴더
- 의미: HaMeR 추론 결과 및 메타데이터 저장
- 생성: `infer_hamer_from_bboxes.py` (`external/hamer/.hamer` 환경 사용)
- 주요 파일:
  - `*_vertices.npy`: HaMeR 메쉬 정점
  - `*_faces.npy`: HaMeR 메쉬 삼각형 인덱스
  - `*_joints.npy`: HaMeR 추정 관절 좌표
  - `*_mesh.obj`: 메쉬 OBJ 파일
  - `hamer_metadata.json`: 전체 HaMeR 결과 메타데이터
  - `hamer_raw_output_summary.json`: 원시 HaMeR 출력 요약
  - `hamer_bbox_debug.png`: HaMeR 입력 바운딩박스 디버그 이미지
- 사용: `verify_hamer_projection.py`, `render_hand_depth.py`
- 분류: 최종/중간 산출물

#### `outputs/hamer_projection/`
- 유형: 폴더
- 의미: HaMeR 메쉬 투영 검증 결과
- 주요 파일:
  - `final_projection_debug.png`: 최종 투영 검증 이미지
  - `final_projection_report.md`: 투영 검증 리포트
  - `bbox_fallback_projection_debug.png`: 바운딩박스 기반 fallback 투영 디버그
- 생성: `scripts/verify_hamer_projection.py`
- 사용: 투영 정확도 확인
- 분류: 최종/디버그 산출물

#### `outputs/hamer_depth/`
- 유형: 폴더
- 의미: HaMeR 메쉬로부터 렌더링한 손 깊이 결과
- 주요 파일:
  - `hand_depth.npy`: 손 깊이 맵
  - `hand_depth_vis.png`: 손 깊이 컬러 시각화
  - `hand_mask.png`: 손 깊이 영역 마스크
  - `hand_depth_debug.png`: 손 메쉬 투영 디버그 이미지
  - `hand_depth_report.md`: 손 깊이 렌더링 리포트
- 생성: `scripts/render_hand_depth.py`
- 사용: `scripts/scale_depth_with_hand.py`
- 분류: 최종/중간 산출물

#### `outputs/scaled_depth/`
- 유형: 폴더
- 의미: 손 깊이 기준으로 스케일 정렬된 exo 깊이 결과
- 주요 파일:
  - `depth_scaled.npy`: 스케일된 exo 깊이
  - `depth_scaled_vis.png`: 스케일된 깊이 시각화
  - `scale_valid_mask.png`: 스케일 계산에 사용된 유효 픽셀 마스크
  - `exo_point_cloud_scaled.ply`: 스케일된 exo 포인트클라우드
  - `scale_report.md`: 스케일 정렬 리포트
  - `scale_ratio_hist.png`: 비율 히스토그램 (matplotlib 설치 시)
- 생성: `scripts/scale_depth_with_hand.py`
- 사용: `scripts/export_p_exo_from_depth.py`
- 분류: 최종 산출물

#### `outputs/pose_depth/`
- 유형: 폴더
- 의미: 최종 exo 3D 포즈(`P_exo`) 결과
- 주요 파일:
  - `P_exo.npy`: 최종 3D 포즈 좌표, shape = (42, 3)
  - `P_exo_2d.npy`: 2D 랜드마크 픽셀 좌표, shape = (42, 2)
  - `P_exo_valid.npy`: 유효성 마스크, shape = (42,)
  - `P_exo_metadata.json`: 좌표계와 키포인트 정보
  - `P_exo_projection_debug.png`: 2D 재투영 디버그 이미지
  - `P_exo_skeleton_black.png`: 검은 배경 위 스켈레톤 시각화
  - `P_exo_report.md`: P_exo 생성 리포트
- 생성: `scripts/export_p_exo_from_depth.py`
- 사용: 최종 P_exo 분석 및 시각화
- 분류: 최종 산출물

## 파이프라인 실행 순서

1. MoGe depth + raw point cloud
   ```powershell
   .\.venv\Scripts\python.exe infer_depth_pointcloud.py --image inputs/exo.jpg --out outputs --depth_model moge
   ```

2. MediaPipe hand bbox
   ```powershell
   .\.venv\Scripts\python.exe infer_hand_bbox.py --image inputs/exo.jpg --out outputs
   ```

3. Hand crop generation
   ```powershell
   .\.venv\Scripts\python.exe crop_hands_from_bboxes.py --image inputs/exo.jpg --bbox_json outputs/hand_bboxes.json --out outputs/hand_crops
   ```

4. HaMeR inference
   ```powershell
   .\external\hamer\.hamer\Scripts\python.exe infer_hamer_from_bboxes.py --image inputs/exo.jpg --bbox_json outputs/hand_bboxes.json --out outputs/hamer
   ```

5. HaMeR projection verification
   ```powershell
   .\.venv\Scripts\python.exe scripts/verify_hamer_projection.py --image inputs/exo.jpg --hamer_dir outputs/hamer --bbox_json outputs/hand_bboxes.json --out outputs/hamer_projection
   ```

6. Hand depth rendering
   ```powershell
   .\.venv\Scripts\python.exe scripts/render_hand_depth.py --image inputs/exo.jpg --hamer_dir outputs/hamer --bbox_json outputs/hand_bboxes.json --out outputs/hamer_depth
   ```

7. Depth scale alignment
   ```powershell
   .\.venv\Scripts\python.exe scripts/scale_depth_with_hand.py --image inputs/exo.jpg --depth outputs/depth_raw.npy --hand_depth outputs/hamer_depth/hand_depth.npy --hand_mask outputs/hamer_depth/hand_mask.png --out outputs/scaled_depth
   ```

8. P_exo export from depth
   ```powershell
   .\.venv\Scripts\python.exe scripts/export_p_exo_from_depth.py --image inputs/exo.jpg --depth outputs/scaled_depth/depth_scaled.npy --K outputs/K_exo.npy --out outputs/pose_depth
   ```

9. P_exo skeleton black visualization
   ```powershell
   .\.venv\Scripts\python.exe scripts/render_p_exo_skeleton_on_black.py
   ```

10. Workspace integrity check
   ```powershell
   .\.venv\Scripts\python.exe scripts/check_workspace_integrity.py
   ```

## 핵심 개념 정리

- `D_exo / depth_raw.npy`
  - exo 카메라에서 추정한 원시 깊이 맵입니다.
  - 깊이 스케일 정렬과 P_exo 생성의 기반입니다.

- `K_exo`
  - exo 카메라 내부 파라미터입니다.
  - 3x3 intrinsics 행렬로, 3D-2D 재투영과 2D 깊이 리프트에 사용됩니다.

- HaMeR `*_vertices.npy`, `*_faces.npy`, `*_joints.npy`
  - HaMeR는 각 손에 대해 매쉬 정점, 삼각형, 3D 관절 좌표를 출력합니다.
  - 주의: 이 `*_joints.npy`는 로컬/손 좌표계 성격이 강하므로 최종 `P_exo`로 그대로 사용해서는 안 됩니다.

- `hand_depth.npy`
  - HaMeR 메쉬를 exo 카메라로 투영해 렌더링한 손 깊이 맵입니다.
  - 손 깊이 스케일 정렬의 기준입니다.

- `hand_mask.png`
  - 손 깊이 맵에서 유효 픽셀 영역을 나타내는 이진 마스크입니다.

- 스케일 팩터 `s*`
  - `D_hand / D_exo` 비율을 이용해 exo 깊이를 HaMeR 손 깊이와 정렬하는 값입니다.
  - `scale_depth_with_hand.py`에서 통계적으로 계산됩니다.

- `depth_scaled.npy`
  - 스케일 정렬된 exo 깊이입니다.
  - 이 깊이를 사용하면 `P_exo`가 exo 카메라 좌표계에서 더 현실적인 깊이를 갖습니다.

- `exo_point_cloud_scaled.ply`
  - 스케일 정렬된 깊이로 생성한 exo 포인트클라우드입니다.
  - `P_exo` 좌표계와 일관된 exo 포인트클라우드입니다.

- `P_exo.npy`
  - 2D MediaPipe 랜드마크를 스케일된 깊이와 `K_exo`로 리프트하여 만든 최종 3D 포즈 좌표입니다.

- `P_exo_2d.npy`
  - 2D 랜드마크 픽셀 좌표입니다.

- `P_exo_valid.npy`
  - 각 키포인트의 유효 여부를 나타내는 마스크입니다.

### 중요 주의 사항

- HaMeR `*_joints.npy`는 로컬/손 기반 출력이며 최종 `P_exo`로 직접 사용해서는 안 됩니다.
- HaMeR `joints.npy + pred_cam_t_full`를 그대로 더해 만든 `P_exo_camera` 방식은 실패한 시도였습니다.
- 현재 최종 `P_exo`는 2D 랜드마크에 `depth_scaled.npy`와 `K_exo.npy`를 적용해 생성됩니다.
- 따라서 현재 `P_exo`는 `exo_point_cloud_scaled.ply`와 같은 exo 카메라 좌표계를 공유합니다.

## 최종 산출물 목록

- `outputs/scaled_depth/depth_scaled.npy`
- `outputs/scaled_depth/exo_point_cloud_scaled.ply`
- `outputs/pose_depth/P_exo.npy`
- `outputs/pose_depth/P_exo_2d.npy`
- `outputs/pose_depth/P_exo_valid.npy`
- `outputs/pose_depth/P_exo_projection_debug.png`
- `outputs/pose_depth/P_exo_skeleton_black.png`

## 다음 단계

- P_ego 추정기 구현이 필요합니다.
- P_ego는 `P_exo`와 동일한 관절 순서를 사용해야 합니다.
- P_exo/P_ego 정합을 위해 Umeyama 변환을 적용해야 합니다.
- 그런 다음 exo 좌표계에서 ego 좌표계(`C_exo` -> ego)로 변환을 설계합니다.
- 이어서 희소 ego RGB 지도 `S_ego`를 생성하고 재구성/생성 단계로 진입할 수 있습니다.
