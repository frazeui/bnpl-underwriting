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


N_MERCHANTS=500

CATEGORIES = {
    "fashion":     {"weight": 0.25, "risk_tier": "low",    "avg_ticket": 350,  "risk_shift":  0.00},
    "grocery":     {"weight": 0.12, "risk_tier": "low",    "avg_ticket": 180,  "risk_shift": -0.20},
    "beauty":      {"weight": 0.12, "risk_tier": "low",    "avg_ticket": 220,  "risk_shift":  0.00},
    "health":      {"weight": 0.06, "risk_tier": "low",    "avg_ticket": 260,  "risk_shift": -0.10},
    "home":        {"weight": 0.13, "risk_tier": "medium", "avg_ticket": 700,  "risk_shift":  0.05},
    "travel":      {"weight": 0.08, "risk_tier": "medium", "avg_ticket": 1500, "risk_shift":  0.15},
    "electronics": {"weight": 0.14, "risk_tier": "high",   "avg_ticket": 1400, "risk_shift":  0.35},
    "jewelry":     {"weight": 0.06, "risk_tier": "high",   "avg_ticket": 1800, "risk_shift":  0.30},
    "gift_cards":  {"weight": 0.04, "risk_tier": "high",   "avg_ticket": 400,  "risk_shift":  0.50},
}   


PLANS = {
    "pay_in_3":        {"share": 0.45, "min": 50,  "max": 3000, "tenor_days": 60},
    "pay_in_4":        {"share": 0.40, "min": 50,  "max": 2000, "tenor_days": 42},
    "installments_6m": {"share": 0.15, "min": 500, "max": 5000, "tenor_days": 180},
}


ORDERS_PER_MONTH = 0.5      
BASKET_SIGMA = 0.5  



RISK_BASE=-4.4
RISK_PER_DTI=2.5
RISK_PER_BUREAU_100=-0.8
RISK_THIN_FILE=0.35
RISK_PER_BASKET_RATIO=1.5
RISK_NOISE_SD=0.5
LABEL_WINDOWS_DAYS=120  