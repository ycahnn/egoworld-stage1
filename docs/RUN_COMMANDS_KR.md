# 실행 명령 모음

## 메인 가상환경 활성화

```powershell
Set-Location "c:\Users\Youngchan Ahn\Desktop\egoworld-stage1"
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe --version
```

## HaMeR 가상환경 활성화

```powershell
Set-Location "c:\Users\Youngchan Ahn\Desktop\egoworld-stage1\external\hamer"
.\.hamer\Scripts\Activate.ps1
.\.hamer\Scripts\python.exe --version
```

## 전체 파이프라인 실행

```powershell
Set-Location "c:\Users\Youngchan Ahn\Desktop\egoworld-stage1"
.\.venv\Scripts\python.exe infer_depth_pointcloud.py --image inputs/exo.jpg --out outputs --depth_model moge
.\.venv\Scripts\python.exe infer_hand_bbox.py --image inputs/exo.jpg --out outputs
.\.venv\Scripts\python.exe crop_hands_from_bboxes.py --image inputs/exo.jpg --bbox_json outputs/hand_bboxes.json --out outputs/hand_crops
.\external\hamer\.hamer\Scripts\python.exe infer_hamer_from_bboxes.py --image inputs/exo.jpg --bbox_json outputs/hand_bboxes.json --out outputs/hamer
.\.venv\Scripts\python.exe scripts/verify_hamer_projection.py --image inputs/exo.jpg --hamer_dir outputs/hamer --bbox_json outputs/hand_bboxes.json --out outputs/hamer_projection
.\.venv\Scripts\python.exe scripts/render_hand_depth.py --image inputs/exo.jpg --hamer_dir outputs/hamer --bbox_json outputs/hand_bboxes.json --out outputs/hamer_depth
.\.venv\Scripts\python.exe scripts/scale_depth_with_hand.py --image inputs/exo.jpg --depth outputs/depth_raw.npy --hand_depth outputs/hamer_depth/hand_depth.npy --hand_mask outputs/hamer_depth/hand_mask.png --out outputs/scaled_depth
.\.venv\Scripts\python.exe scripts/export_p_exo_from_depth.py --image inputs/exo.jpg --depth outputs/scaled_depth/depth_scaled.npy --K outputs/K_exo.npy --out outputs/pose_depth
.\.venv\Scripts\python.exe scripts/render_p_exo_skeleton_on_black.py
.\.venv\Scripts\python.exe scripts/check_workspace_integrity.py
```

## 개별 단계 실행

- `MoGe` 깊이 + 포인트클라우드:
  ```powershell
  .\.venv\Scripts\python.exe infer_depth_pointcloud.py --image inputs/exo.jpg --out outputs --depth_model moge
  ```

- MediaPipe 손 바운딩박스:
  ```powershell
  .\.venv\Scripts\python.exe infer_hand_bbox.py --image inputs/exo.jpg --out outputs
  ```

- 손 크롭 생성:
  ```powershell
  .\.venv\Scripts\python.exe crop_hands_from_bboxes.py --image inputs/exo.jpg --bbox_json outputs/hand_bboxes.json --out outputs/hand_crops
  ```

- HaMeR 추론:
  ```powershell
  .\external\hamer\.hamer\Scripts\python.exe infer_hamer_from_bboxes.py --image inputs/exo.jpg --bbox_json outputs/hand_bboxes.json --out outputs/hamer
  ```

- HaMeR 투영 검증:
  ```powershell
  .\.venv\Scripts\python.exe scripts/verify_hamer_projection.py --image inputs/exo.jpg --hamer_dir outputs/hamer --bbox_json outputs/hand_bboxes.json --out outputs/hamer_projection
  ```

- 손 깊이 렌더링:
  ```powershell
  .\.venv\Scripts\python.exe scripts/render_hand_depth.py --image inputs/exo.jpg --hamer_dir outputs/hamer --bbox_json outputs/hand_bboxes.json --out outputs/hamer_depth
  ```

- 깊이 스케일 정렬:
  ```powershell
  .\.venv\Scripts\python.exe scripts/scale_depth_with_hand.py --image inputs/exo.jpg --depth outputs/depth_raw.npy --hand_depth outputs/hamer_depth/hand_depth.npy --hand_mask outputs/hamer_depth/hand_mask.png --out outputs/scaled_depth
  ```

- P_exo 생성:
  ```powershell
  .\.venv\Scripts\python.exe scripts/export_p_exo_from_depth.py --image inputs/exo.jpg --depth outputs/scaled_depth/depth_scaled.npy --K outputs/K_exo.npy --out outputs/pose_depth
  ```

- P_exo 검은 배경 스켈레톤 시각화:
  ```powershell
  .\.venv\Scripts\python.exe scripts/render_p_exo_skeleton_on_black.py
  ```

- 워크스페이스 무결성 확인:
  ```powershell
  .\.venv\Scripts\python.exe scripts/check_workspace_integrity.py
  ```

## 의존성 잠금 파일 재생성

- 메인 환경 lock 파일:
  ```powershell
  .\.venv\Scripts\python.exe -m pip freeze > requirements-main-lock.txt
  ```

- HaMeR 환경 lock 파일:
  ```powershell
  .\external\hamer\.hamer\Scripts\python.exe -m pip freeze > external\hamer\requirements-hamer-lock.txt
  ```

## 중요한 이미지 열기

```powershell
start outputs/hamer_projection/final_projection_debug.png
start outputs/hamer_depth/hand_depth_vis.png
start outputs/pose_depth/P_exo_skeleton_black.png
```
