import pandas as pd
import numpy as np
import joblib
import json

# =========================
# 1. LOAD USER DATA
# =========================
df = pd.read_csv("restaurant_final.csv")

# =========================
# 2. CLEAN DATA
# =========================
df = df.drop_duplicates()
df = df.fillna(0)

if 'Parking Availability' in df.columns:
    df['Parking Availability'] = df['Parking Availability'].map({
        'Yes': 1,
        'No': 0
    })

# =========================
# 3. HANDLE OUTLIERS (IQR CLIP)
# =========================
def cap_outliers(df, cols):
    for col in cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        
        df[col] = np.clip(df[col], lower, upper)
    return df

df = cap_outliers(df, [
    'Social Media Followers',
    'Number of Reviews',
    'Rating',
    'Ambience Score'
])

# =========================
# 4. AGGREGATE (CRITICAL)
# =========================
followers_mean = df['Social Media Followers'].mean()
reviews_mean = df['Number of Reviews'].mean()

rating_mean = df['Rating'].mean()
ambience_mean = df['Ambience Score'].mean()

# =========================
# 5. DERIVED METRICS (SMART LAYER)
# =========================

# Customer
reviews_per_follower = reviews_mean / followers_mean if followers_mean > 0 else 0

def classify_engagement(rpf):
    if rpf < 0.02:
        return {
            "level": "low",
            "interpretation": "weak conversion of audience into engagement"
        }
    elif rpf < 0.05:
        return {
            "level": "moderate",
            "interpretation": "average engagement efficiency"
        }
    else:
        return {
            "level": "high",
            "interpretation": "strong engagement and demand conversion"
        }

engagement_info = classify_engagement(reviews_per_follower)

# Business
def analyze_experience(rating, ambience):
    if ambience < 6:
        return {
            "level": "weak",
            "interpretation": "experience quality lags behind food quality"
        }
    elif ambience < 7.5:
        return {
            "level": "moderate",
            "interpretation": "experience is acceptable but not differentiated"
        }
    else:
        return {
            "level": "strong",
            "interpretation": "experience enhances overall brand perception"
        }

experience_info = analyze_experience(rating_mean, ambience_mean)

# =========================
# 6. RAW SCORES
# =========================
raw_customer = (followers_mean + reviews_mean) / 2
raw_business = rating_mean * ambience_mean

# =========================
# 7. LOAD SCALERS (IMPORTANT)
# =========================
scaler_customer = joblib.load("scaler_customer.pkl")
scaler_business = joblib.load("scaler_business.pkl")

customer_score = scaler_customer.transform([[raw_customer]])[0][0]
business_score = scaler_business.transform([[raw_business]])[0][0]

# =========================
# 8. LABEL FUNCTION
# =========================
def score_to_label(score):
    if score >= 1.0:
        return "very strong"
    elif score >= 0.5:
        return "strong"
    elif score > -0.5:
        return "neutral"
    elif score > -1.0:
        return "weak"
    else:
        return "very weak"

# =========================
# 9. DYNAMIC INSIGHT FUNCTIONS
# =========================

def build_customer_insight(followers, reviews, rpf):
    if rpf < 0.02:
        return {
            "strength": f"high reach (~{int(followers):,} followers)",
            "weakness": f"low engagement (~{int(reviews):,} reviews, weak conversion)"
        }
    elif rpf < 0.05:
        return {
            "strength": "balanced reach and engagement",
            "weakness": "moderate conversion efficiency"
        }
    else:
        return {
            "strength": "strong engagement conversion",
            "weakness": "limited scalability"
        }

def build_business_insight(rating, ambience):
    if rating > 4 and ambience < 6:
        return {
            "strength": f"strong food quality (rating {rating:.2f})",
            "weakness": f"weak ambience ({ambience:.2f}/10) limits experience"
        }
    elif rating < 3.5:
        return {
            "strength": "baseline operations",
            "weakness": f"low rating ({rating:.2f}) indicates quality issues"
        }
    else:
        return {
            "strength": f"balanced quality (rating {rating:.2f})",
            "weakness": f"moderate ambience ({ambience:.2f}) limits differentiation"
        }

# =========================
# 10. BUILD FINAL PAYLOAD
# =========================
payload = {
    "customer": {
        "score": float(customer_score),
        "label": score_to_label(customer_score),

        "metrics": {
            "followers": float(followers_mean),
            "reviews": float(reviews_mean)
        },

        "derived": {
            "reviews_per_follower": float(reviews_per_follower),
            "engagement_level": engagement_info["level"],
            "engagement_interpretation": engagement_info["interpretation"]
        },

        "insight": build_customer_insight(
            followers_mean,
            reviews_mean,
            reviews_per_follower
        )
    },

    "business": {
        "score": float(business_score),
        "label": score_to_label(business_score),

        "metrics": {
            "rating": float(rating_mean),
            "ambience": float(ambience_mean)
        },

        "derived": {
            "experience_level": experience_info["level"],
            "experience_interpretation": experience_info["interpretation"]
        },

        "insight": build_business_insight(
            rating_mean,
            ambience_mean
        )
    }
}

# =========================
# 11. SAVE JSON
# =========================
with open("zai_payload.json", "w") as f:
    json.dump(payload, f, indent=2)

print("✅ JSON saved as zai_payload.json")
print(json.dumps(payload, indent=2))