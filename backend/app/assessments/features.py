from datetime import date
from decimal import Decimal

import pandas as pd

from app.assessments.schemas import AssessmentCreateRequest
from app.patients.models import Patient


MODEL_FEATURES = [
    "Age (yrs)",
    "BMI",
    "Cycle(R/I)",
    "Cycle length(days)",
    "FSH(mIU/mL)",
    "LH(mIU/mL)",
    "FSH/LH",
    "AMH(ng/mL)",
    "Weight gain(Y/N)",
    "hair growth(Y/N)",
    "Skin darkening (Y/N)",
    "Fast food (Y/N)",
    "Reg.Exercise(Y/N)",
    "Follicle No. (L)",
    "Follicle No. (R)",
    "Total Follicles",
    "Follicle Difference",
    "Symptom Score",
    "LifeStyle Risk Score",
]


def calculate_age(
    date_of_birth: date,
    assessment_date: date,
) -> int:
    return (
        assessment_date.year
        - date_of_birth.year
        - (
            (assessment_date.month, assessment_date.day)
            < (date_of_birth.month, date_of_birth.day)
        )
    )


def build_model_features(
    patient: Patient,
    data: AssessmentCreateRequest,
    assessment_date: date,
) -> tuple[pd.DataFrame, Decimal | None]:
    height_m = float(patient.height_cm) / 100
    weight_kg = float(data.weight_kg)

    bmi = weight_kg / (height_m**2)

    fsh = float(data.fsh_miu_ml)
    lh = float(data.lh_miu_ml)

    ratio = fsh / lh if lh > 0 else None

    left = data.follicle_left
    right = data.follicle_right

    symptom_score = sum([
        int(data.weight_gain),
        int(data.hair_growth),
        int(data.skin_darkening),
        int(data.hair_loss),
        int(data.pimples),
    ])

    features = {
        "Age (yrs)": calculate_age(
            patient.date_of_birth,
            assessment_date,
        ),
        "BMI": bmi,

        # Training data uses 2=regular and 4=irregular.
        "Cycle(R/I)": 2 if data.cycle_regular else 4,
        "Cycle length(days)": data.cycle_length,

        "FSH(mIU/mL)": fsh,
        "LH(mIU/mL)": lh,
        "FSH/LH": ratio if ratio is not None else float("nan"),
        "AMH(ng/mL)": (
            float(data.amh_ng_ml)
            if data.amh_ng_ml is not None
            else float("nan")
        ),

        "Weight gain(Y/N)": int(data.weight_gain),
        "hair growth(Y/N)": int(data.hair_growth),
        "Skin darkening (Y/N)": int(data.skin_darkening),
        "Fast food (Y/N)": int(data.fast_food),
        "Reg.Exercise(Y/N)": int(data.regular_exercise),

        "Follicle No. (L)": left,
        "Follicle No. (R)": right,
        "Total Follicles": left + right,
        "Follicle Difference": abs(left - right),
        "Symptom Score": symptom_score,
        "LifeStyle Risk Score": (
            int(data.fast_food)
            - int(data.regular_exercise)
        ),
    }

    frame = pd.DataFrame(
        [features],
        columns=MODEL_FEATURES,
    )

    stored_ratio = (
        Decimal(str(ratio)).quantize(Decimal("0.01"))
        if ratio is not None
        else None
    )

    return frame, stored_ratio