# Model evaluation — Phase 2

Training timestamp: `2026-10-15T13:13:36.702931+00:00`

## Dataset and procedure

The actual `data/Crop_recommendation.csv` was loaded with 2,200 rows, 22 target classes, and the seven validated features: `N`, `P`, `K`, `temperature`, `humidity`, `ph`, `rainfall`.

A stratified 80/20 train/test split used random seed `42`. Model selection used only the 1,760-row training split with 5-fold stratified cross-validation. The test set was held out until after selection.

## Algorithms compared

- **Decision Tree Classifier:** an interpretable tree-based baseline.
- **Random Forest Classifier:** an ensemble of randomized decision trees.
- **K-Nearest Neighbors Classifier:** uses `StandardScaler` inside a scikit-learn Pipeline so scaling is fitted separately within each training fold.

## Cross-validation comparison

| Model | Fold macro F1 scores | Mean macro F1 | Std. dev. |
|---|---|---:|---:|
| Decision Tree | 0.9943, 0.9773, 0.9886, 0.9886, 0.9772 | 0.9852 | 0.0068 |
| Random Forest | 1.0000, 0.9972, 0.9857, 0.9886, 0.9972 | 0.9937 | 0.0056 |
| K-Nearest Neighbors | 0.9830, 0.9715, 0.9451, 0.9627, 0.9628 | 0.9650 | 0.0124 |

**Selection:** `Random Forest` was selected because it had the highest mean cross-validation macro F1. The criterion was evaluated before using the held-out test set.

## Selected-model held-out test results

| Metric | Value |
|---|---:|
| Accuracy | 0.9932 |
| Macro precision | 0.9935 |
| Macro recall | 0.9932 |
| Macro F1 | 0.9932 |

### Per-class metrics

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| apple | 1.0000 | 1.0000 | 1.0000 | 20 |
| banana | 1.0000 | 1.0000 | 1.0000 | 20 |
| blackgram | 1.0000 | 0.9500 | 0.9744 | 20 |
| chickpea | 1.0000 | 1.0000 | 1.0000 | 20 |
| coconut | 1.0000 | 1.0000 | 1.0000 | 20 |
| coffee | 1.0000 | 1.0000 | 1.0000 | 20 |
| cotton | 1.0000 | 1.0000 | 1.0000 | 20 |
| grapes | 1.0000 | 1.0000 | 1.0000 | 20 |
| jute | 0.9524 | 1.0000 | 0.9756 | 20 |
| kidneybeans | 1.0000 | 1.0000 | 1.0000 | 20 |
| lentil | 1.0000 | 0.9500 | 0.9744 | 20 |
| maize | 0.9524 | 1.0000 | 0.9756 | 20 |
| mango | 1.0000 | 1.0000 | 1.0000 | 20 |
| mothbeans | 0.9524 | 1.0000 | 0.9756 | 20 |
| mungbean | 1.0000 | 1.0000 | 1.0000 | 20 |
| muskmelon | 1.0000 | 1.0000 | 1.0000 | 20 |
| orange | 1.0000 | 1.0000 | 1.0000 | 20 |
| papaya | 1.0000 | 1.0000 | 1.0000 | 20 |
| pigeonpeas | 1.0000 | 1.0000 | 1.0000 | 20 |
| pomegranate | 1.0000 | 1.0000 | 1.0000 | 20 |
| rice | 1.0000 | 0.9500 | 0.9744 | 20 |
| watermelon | 1.0000 | 1.0000 | 1.0000 | 20 |

### Confusion matrix

Rows are actual classes and columns are predicted classes, in the order shown in the header.

| Actual \ Predicted | apple | banana | blackgram | chickpea | coconut | coffee | cotton | grapes | jute | kidneybeans | lentil | maize | mango | mothbeans | mungbean | muskmelon | orange | papaya | pigeonpeas | pomegranate | rice | watermelon |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| apple | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| banana | 0 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| blackgram | 0 | 0 | 19 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| chickpea | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| coconut | 0 | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| coffee | 0 | 0 | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| cotton | 0 | 0 | 0 | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| grapes | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| jute | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| kidneybeans | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| lentil | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 19 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| maize | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| mango | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| mothbeans | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| mungbean | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| muskmelon | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 0 | 0 | 0 |
| orange | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 0 | 0 |
| papaya | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 0 |
| pigeonpeas | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | 0 | 0 | 0 |
| pomegranate | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | 0 | 0 |
| rice | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 19 | 0 |
| watermelon | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 |

## Observed classification errors

The selected model's held-out errors were:

| Actual class | Predicted class | Count |
|---|---|---:|
| blackgram | maize | 1 |
| lentil | mothbeans | 1 |
| rice | jute | 1 |

## Limitations

- Results describe this supplied dataset and its sampled conditions; they are not universal agronomic guarantees.
- A balanced benchmark does not establish real-world performance across farms, regions, seasons, measurement error, or crops outside these 22 classes.
- Probability-like outputs must be interpreted as model confidence, not calibrated agronomic risk, unless calibration is evaluated separately.

## Reproduction

From the project root, run:

```powershell
python backend/scripts/train_model.py
python -m unittest discover -s tests -v
```
The script recreates `backend/models/crop_model.joblib`, `backend/models/model_metadata.json`, and this report from the unchanged CSV.
