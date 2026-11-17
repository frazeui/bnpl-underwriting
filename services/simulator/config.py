from datetime import date

SIM_START = date(2024, 11, 1)     
SIM_END = date(2026, 11, 1)

AGE_MEAN, AGE_SD = 33, 9
AGE_MIN, AGE_MAX = 18, 65

INCOME_SIGMA = 0.45
INCOME_MIN, INCOME_MAX = 1_500, 60_000

OBLIGATION_BETA = (2.0, 6.0)


EMPLOYMENT = {
    "salaried_gov":       {"share": 0.30, "income_median": 9_500, "risk_shift": -0.35},
    "salaried_private":   {"share": 0.40, "income_median": 7_000, "risk_shift":  0.00},
    "self_employed":      {"share": 0.15, "income_median": 8_000, "risk_shift":  0.30},
    "student_unemployed": {"share": 0.15, "income_median": 2_500, "risk_shift":  0.45},
}


CITIES = {
    "Riyadh": 0.34, "Jeddah": 0.22, "Dammam": 0.10, "Makkah": 0.07,
    "Madinah": 0.06, "Khobar": 0.05, "Tabuk": 0.04, "Abha": 0.04,
    "Other": 0.08,
}


BUREAU_MEAN, BUREAU_SD = 680, 70
BUREAU_MIN, BUREAU_MAX = 300, 900
BUREAU_PER_LOG_INCOME = 60        
BUREAU_PER_AGE_YEAR = 1.5         
THIN_FILE_PROB_YOUNG = 0.30       
THIN_FILE_PROB_ADULT = 0.08


KYC_VERIFIED_PROB = 0.97
PHONE_VERIFIED_PROB = 0.98


GENDER = {"male": 0.55, "female": 0.45}
NATIONALITY = {"saudi": 0.60, "non_saudi": 0.40}

SEED = 42
N_CUSTOMERS = 1_000 