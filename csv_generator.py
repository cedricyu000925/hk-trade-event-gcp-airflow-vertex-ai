import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import uuid

random.seed(42)
np.random.seed(42)

# --- Reference data ---
companies = [
    "Alibaba Group", "Jardine Matheson", "CK Hutchison", "HSBC Holdings",
    "Cathay Pacific", "BYD Auto", "Siemens AG", "Samsung Electronics",
    "Toyota Motor", "Sony Group", "Lenovo Group", "Huawei Technologies",
    "DHL Express", "Maersk Group", "Bosch Group", "Philips NV", "Canon Inc",
    "LG Electronics", "Foxconn Technology", "Mitsubishi Electric"
]
sectors = [
    "Electronics & Technology", "Consumer Goods", "Industrial Machinery",
    "Finance & Banking", "Logistics & Supply Chain", "Automotive",
    "Chemical & Materials", "Retail & Fashion", "Food & Beverage",
    "Healthcare & Medical", "Telecommunications", "Professional Services"
]
region_labels = ["Hong Kong", "Mainland China", "Taiwan", "Japan", "South Korea",
                 "Southeast Asia", "Europe", "North America", "Middle East", "Others"]
region_probs  = [0.20, 0.28, 0.06, 0.07, 0.06, 0.10, 0.09, 0.08, 0.04, 0.02]

events = [
    ("EVT-2023-001", "Electronics Asia Expo 2023",            2023, "Electronics & Technology",  "HKCEC Hall 1"),
    ("EVT-2023-002", "HK International Sourcing Fair 2023",   2023, "Consumer Goods",             "AsiaWorld-Expo"),
    ("EVT-2023-003", "Industrial Automation Summit 2023",     2023, "Industrial Machinery",       "HKCEC Hall 3"),
    ("EVT-2023-004", "Global Supply Chain Forum 2023",        2023, "Logistics & Supply Chain",   "HK Convention Centre"),
    ("EVT-2024-001", "Electronics Asia Expo 2024",            2024, "Electronics & Technology",  "HKCEC Hall 1"),
    ("EVT-2024-002", "HK International Sourcing Fair 2024",   2024, "Consumer Goods",             "AsiaWorld-Expo"),
    ("EVT-2024-003", "Smart Manufacturing Expo 2024",         2024, "Industrial Machinery",       "HKCEC Hall 2"),
    ("EVT-2024-004", "Global Trade & Logistics Summit 2024",  2024, "Logistics & Supply Chain",   "HK Convention Centre"),
    ("EVT-2024-005", "Asia Finance & Investment Forum 2024",  2024, "Finance & Banking",          "Four Seasons HK"),
]

goals = [
    "Sourcing new suppliers", "Finding buyers/distributors", "Market research",
    "Networking", "Product launch", "Brand awareness",
    "Partnership development", "Technology scouting",
    "Investment opportunities", "Regulatory updates"
]
leads   = ["Email Campaign", "Website", "Referral", "Social Media", "Direct", "Partner"]
fnames  = ["Wei", "Mei", "John", "David", "Sarah", "Michael", "James", "Lisa",
           "Hiroshi", "Yuki", "Ahmad", "Fatima", "Hans", "Maria", "Chen",
           "Yan", "Kenji", "Robert", "Emily", "Raj", "Min-jun", "Ji-yeon"]
lnames  = ["Wong", "Chan", "Lee", "Lam", "Cheung", "Ho", "Ng", "Tanaka",
           "Kim", "Zhang", "Liu", "Yang", "Muller", "Johnson", "Smith",
           "Garcia", "Al-Hassan", "Patel", "Park", "Suzuki"]

# --- Generate customer master (80,000 customers) ---
N = 80000
cids    = [f"CUST-{str(i).zfill(6)}" for i in range(1, N + 1)]
cnames  = [f"{random.choice(fnames)} {random.choice(lnames)}" for _ in range(N)]
ccos    = [random.choice(companies) for _ in range(N)]
csecs   = [random.choice(sectors) for _ in range(N)]
cregs   = np.random.choice(region_labels, size=N, p=region_probs).tolist()
cemails = [f"{n.lower().replace(' ', '.').replace('/', '')}{random.randint(10,999)}@business.com"
           for n in cnames]
cjoin   = [datetime(2018, 1, 1) + timedelta(days=random.randint(0, 1825))
           for _ in range(N)]

print("Customer master ready. Generating event registrations...")

# --- Generate registrations per event (~55K each = ~495K total) ---
from pathlib import Path
OUTPUT_PATH = Path(__file__).parent / "hk_trade_event_registrations.csv"
CHUNK_SIZE  = 55000
header_written = False

for eid, ename, eyear, ecat, evenue in events:
    idx       = random.choices(range(N), k=CHUNK_SIZE)
    reg_fees  = np.round(np.random.uniform(800, 5000, CHUNK_SIZE), 2)
    disc_mask = np.random.random(CHUNK_SIZE) < 0.35
    discs     = np.where(disc_mask, np.round(np.random.uniform(0, 0.30, CHUNK_SIZE), 2), 0.0)
    finals    = np.round(reg_fees * (1 - discs), 2)
    attended  = np.random.random(CHUNK_SIZE) < 0.82

    chunk_rows = []
    for j, i in enumerate(idx):
        att = bool(attended[j])
        chunk_rows.append({
            "registration_id":        f"REG-{uuid.uuid4().hex[:10].upper()}",
            "customer_id":            cids[i],
            "customer_name":          cnames[i]  if random.random() > 0.02 else None,
            "customer_email":         cemails[i] if random.random() > 0.03 else None,
            "company_name":           ccos[i],
            "business_sector":        csecs[i]   if random.random() > 0.01 else "Unknown",
            "customer_region":        cregs[i]   if random.random() > 0.015 else None,
            "customer_since":         cjoin[i].strftime("%Y-%m-%d"),
            "event_id":               eid,
            "event_name":             ename,
            "event_year":             eyear,
            "event_category":         ecat,
            "event_venue":            evenue,
            "registration_date":      (datetime(eyear, random.randint(1, 6),
                                               random.randint(1, 28))).strftime("%Y-%m-%d"),
            "attended":               "Y" if att else "N",
            "registration_fee_hkd":   float(reg_fees[j]),
            "discount_rate":          float(discs[j]),
            "final_fee_hkd":          float(finals[j]) if random.random() > 0.02 else None,
            "participation_goal":     random.choice(goals),
            "satisfaction_score":     random.randint(1, 5) if att and random.random() > 0.25 else None,
            "sessions_attended":      random.randint(1, 8) if att else 0,
            "lead_source":            random.choice(leads),
            "is_returning_customer":  "Y" if cjoin[i].year < eyear else "N",
        })

    chunk_df = pd.DataFrame(chunk_rows)
    chunk_df.to_csv(OUTPUT_PATH, mode="a", header=not header_written, index=False)
    header_written = True
    print(f"  ✓ {eid} — {len(chunk_rows):,} rows written")

final_df = pd.read_csv(OUTPUT_PATH)
print(f"\nDone! Total rows: {len(final_df):,}  |  Columns: {len(final_df.columns)}")
print(f"File saved as: {OUTPUT_PATH}")
print("\nNull summary:")
print(final_df.isnull().sum()[final_df.isnull().sum() > 0])