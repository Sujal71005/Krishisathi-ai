# Dataset audit — Phase 1

File inspected: `data/Crop_recommendation.csv`

Inspection method: `pandas.read_csv` with shape, dtypes, null counts, duplicate count, `value_counts`, and `describe(include='number')`.

## Shape and schema

- Rows: **2,200**
- Columns: **8**
- Columns in order: `N`, `P`, `K`, `temperature`, `humidity`, `ph`, `rainfall`, `label`
- Expected feature set: `N`, `P`, `K`, `temperature`, `humidity`, `ph`, `rainfall`
- Target: `label`
- Schema difference: **none**

## Data quality and types

| Column | Type | Missing |
|---|---:|---:|
| N | int64 | 0 |
| P | int64 | 0 |
| K | int64 | 0 |
| temperature | float64 | 0 |
| humidity | float64 | 0 |
| ph | float64 | 0 |
| rainfall | float64 | 0 |
| label | object | 0 |

- Missing values: **0 in every column**
- Duplicate records: **0**
- Target classes: **22**
- Records per class: **100 for every class**

## Class distribution

| Label | Count |
|---|---:|
| apple | 100 |
| banana | 100 |
| blackgram | 100 |
| chickpea | 100 |
| coconut | 100 |
| coffee | 100 |
| cotton | 100 |
| grapes | 100 |
| jute | 100 |
| kidneybeans | 100 |
| lentil | 100 |
| maize | 100 |
| mango | 100 |
| mothbeans | 100 |
| mungbean | 100 |
| muskmelon | 100 |
| orange | 100 |
| papaya | 100 |
| pigeonpeas | 100 |
| pomegranate | 100 |
| rice | 100 |
| watermelon | 100 |

## Numerical statistics

| Feature | Mean | Std. dev. | Min | 25% | Median | 75% | Max |
|---|---:|---:|---:|---:|---:|---:|---:|
| N | 50.551818 | 36.917334 | 0.000000 | 21.000000 | 37.000000 | 84.250000 | 140.000000 |
| P | 53.362727 | 32.985883 | 5.000000 | 28.000000 | 51.000000 | 68.000000 | 145.000000 |
| K | 48.149091 | 50.647931 | 5.000000 | 20.000000 | 32.000000 | 49.000000 | 205.000000 |
| temperature | 25.616244 | 5.063749 | 8.825675 | 22.769375 | 25.598693 | 28.561654 | 43.675493 |
| humidity | 71.481779 | 22.263812 | 14.258040 | 60.261953 | 80.473146 | 89.948771 | 99.981876 |
| ph | 6.469480 | 0.773938 | 3.504752 | 5.971693 | 6.425045 | 6.923643 | 9.935091 |
| rainfall | 103.463655 | 54.958389 | 20.211267 | 64.551686 | 94.867624 | 124.267508 | 298.560117 |

## Interpretation for Phase 2

The target is perfectly balanced in this file, so stratified splitting is appropriate for initial evaluation. The numerical ranges should be used to define transparent API validation and should not be treated as universal agronomic limits without domain review.
