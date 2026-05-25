# 실패 및 폐기 후보 정리

이 문서는 현재 워크스페이스에서 알려진 실패 시도와 폐기 후보 산출물을 정리합니다.

## 주요 실패/폐기 항목

- HaMeR `joints.npy + pred_cam_t_full` 방식의 `P_exo_camera` 시도는 최종 파이프라인이 아닙니다.
  - 이 방식은 `P_exo` 최종 생성에 사용되지 않습니다.
  - HaMeR 로컬 조인트와 카메라 이동을 단순 더하는 방식은 현재 최종 포즈로 인정되지 않습니다.

- `outputs/pose/` 폴더가 존재하는 경우
  - 이 폴더는 이전 `P_exo` 시도 또는 비최종 결과를 포함할 수 있습니다.
  - 현재 최종 파이프라인은 `outputs/pose_depth/` 아래 `P_exo.npy`를 사용합니다.

- 오래된 스켈레톤 시각화 결과
  - `outputs/pose_depth/P_exo_skeleton_black.png`는 최종 시각화입니다.
  - 그 외 `pose_depth` 하위의 이전 시각화 파일이 있으면 검토 대상입니다.

- HaMeR 투영 관련 디버그
  - `outputs/hamer_projection/final_projection_debug.png`가 최종 투영 검증 출력입니다.
  - `outputs/hamer_projection/bbox_fallback_projection_debug.png`는 디버그용 fallback 출력입니다.

- `scripts/export_p_exo.py`
  - 이 파일은 이전 `P_exo` 후보 생성 방식으로 현재 최종 파이프라인이 아닙니다.
  - `_trash_review/scripts/export_p_exo.py`에 격리되어 있습니다.

## 현재 사용할 파일

- 최종 `P_exo` 경로: `outputs/pose_depth/P_exo.npy`
- 현재 유효한 P_exo 시각화: `outputs/pose_depth/P_exo_skeleton_black.png`
- 현재 유효한 HaMeR 투영 검증: `outputs/hamer_projection/final_projection_debug.png`

## 요약

- 현재 워크스페이스에서 최종으로 신뢰할 수 있는 경로는 `outputs/scaled_depth/`와 `outputs/pose_depth/` 기반입니다.
- `outputs/pose/` 또는 `_trash_review/`에 있는 이전 결과는 직접 사용할 필요가 없습니다.
- HaMeR raw joints는 최종 `P_exo`가 아니며, 현재 `P_exo`는 2D 랜드마크 + `depth_scaled.npy` + `K_exo.npy` 깊이 리프트 방식입니다.
