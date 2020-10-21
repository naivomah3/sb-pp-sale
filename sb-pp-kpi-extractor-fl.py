
import numpy as np
import math
import pandas as pd


# Define Multiple KPI Extractor functions
def get_rba(row):
    if np.isnan(row["UNIT_NUMBER"]):
        return np.nan
    if row["UNIT_NUMBER"] >= 5:
        return row["RESIDENTIAL_REVENUE"] + row["COMMERCIAL_REVENUE"] + row["PARKING_REVENUE"] + row["OTHERS_REVENUE"]
    else:
        return np.nan


def get_round_up(row):
    if np.isnan(row["RBA"]):
        return np.nan
    decimals = -3
    multiplier = 10 ** decimals
    return math.ceil(row["RBA"] * multiplier) / multiplier


def get_norm_expense_heat(row):
    if np.isnan(row["EXPENSES_OIL"]) and np.isnan(row["EXPENSES_GAZ"]):
        return np.nan
    return row["EXPENSES_OIL"] + row["EXPENSES_GAZ"]


def get_norm_expense_maint(row):
    if np.isnan(row["UNIT_NUMBER"]):
        return np.nan
    return row["UNIT_NUMBER"] * 500


def get_norm_expense_conc(row):
    if np.isnan(row["UNIT_NUMBER"]):
        return np.nan
    if 4 <= row["UNIT_NUMBER"] <= 6:
        row = row["UNIT_NUMBER"]*125
    elif 7 <= row["UNIT_NUMBER"] <= 11:
        row = row["UNIT_NUMBER"]*170
    else:
        row = row["UNIT_NUMBER"]*300
    return row


def get_norm_expense_mngt(row):
    if np.isnan(row["RBA"]) or np.isnan(row["UNIT_NUMBER"]):
        return np.nan
    if 4 <= row["UNIT_NUMBER"] <= 6:
        row = row["RBA"]*.03
    elif 7 <= row["UNIT_NUMBER"] <= 11:
        row = row["RBA"]*.04
    else:
        row = row["RBA"]*.05
    return row


def get_norm_expense_vac(row):
    if np.isnan(row["RBA"]):
        return np.nan
    return round(row["RBA"] * 0.03, 2)


def get_norm_expense_ins(row):
    if np.isnan(row["UNIT_NUMBER"]):
        return np.nan
    if np.isnan(row["EXPENSES_ASSURANCE"]) or row["EXPENSES_ASSURANCE"] < 100:
        return row["UNIT_NUMBER"] * 500
    else:
        return row["EXPENSES_ASSURANCE"]


def get_norm_expense_elec(row):
    if np.isnan(row["UNIT_NUMBER"]):
        return np.nan
    if np.isnan(row["EXPENSES_ELECTRICITY"]) or row["EXPENSES_ELECTRICITY"] < 100:
        return row["UNIT_NUMBER"] * 100
    else:
        return row["EXPENSES_ELECTRICITY"]


def get_total_expenses(row):
    total_exp = row["MUNICIPAL_TAXE"] + row["SCHOOL_TAXE"] + \
        row["NORM_EXP_MAINTENANCE"] + row["NORM_EXP_CONCIERGE"] + \
        row["NORM_EXP_MANAGEMENT"] + row["NORM_EXP_INSURANCE"] + \
        row["NORM_EXP_ELECTRICITY"] + row["NORM_EXP_HEAT"] + \
        row["NORM_EXP_VACANCY"]
    total_exp = round(total_exp, 3)

    return total_exp


def get_norm_total_expenses(row):
    if np.isnan(row["TOTAL_EXPENSES"]):
        return np.nan
    decimals = -2
    multiplier = 10 ** decimals
    norm_total = math.ceil(row["TOTAL_EXPENSES"] * multiplier) / multiplier
    return abs(norm_total)


def get_net_norm_income(row):
    if np.isnan(row["RBA"]) or np.isnan(row["NORM_TOTAL_EXPENSES"]):
        return np.nan
    return round(row["RBA"] - row["NORM_TOTAL_EXPENSES"], 2)


def get_cap_rate(row):
    if np.isnan(row["NET_NORM_INCOME"]) or np.isnan(row["SOLD_PRICE"]):
        return np.nan
    return round((row["NET_NORM_INCOME"] / row["SOLD_PRICE"] * 100), 2)


def get_gross_revenue_mult(row):
    if np.isnan(row["SOLD_PRICE"]) or np.isnan(row["RBA"]) or row["RBA"] == 0:
        return np.nan
    return round(row["SOLD_PRICE"] / row["RBA"], 2)


def get_unit_price(row):
    if np.isnan(row["SOLD_PRICE"]) or np.isnan(row["UNIT_NUMBER"]):
        return np.nan
    if row["UNIT_NUMBER"] == 0:
        return row["UNIT_NUMBER"]
    return round(row["SOLD_PRICE"] / row["UNIT_NUMBER"], 2)


def get_net_revenue_mult(row):
    if np.isnan(row["SOLD_PRICE"]) or np.isnan(row["NET_NORM_INCOME"]):
        return np.nan
    return round(row["SOLD_PRICE"] / row["NET_NORM_INCOME"], 2)


def get_kpi(dataset):
    df = dataset.copy()
    df["RBA"] = df.apply(get_rba, axis=1)
    df["REVENUS_GROSS_ROUND"] = df.apply(get_round_up, axis=1)
    df["NORM_EXP_HEAT"] = df.apply(get_norm_expense_heat, axis=1)
    df["NORM_EXP_MAINTENANCE"] = df.apply(get_norm_expense_maint, axis=1)
    df["NORM_EXP_CONCIERGE"] = df.apply(get_norm_expense_conc, axis=1)
    df["NORM_EXP_MANAGEMENT"] = df.apply(get_norm_expense_mngt, axis=1)
    df["NORM_EXP_INSURANCE"] = df.apply(get_norm_expense_ins, axis=1)
    df["NORM_EXP_VACANCY"] = df.apply(get_norm_expense_vac, axis=1)
    df["NORM_EXP_ELECTRICITY"] = df.apply(get_norm_expense_elec, axis=1)
    df["TOTAL_EXPENSES"] = df.apply(get_total_expenses, axis=1)
    df["NORM_TOTAL_EXPENSES"] = df.apply(get_norm_total_expenses, axis=1)
    df["NET_NORM_INCOME"] = df.apply(get_net_norm_income, axis=1)
    df["CAP_RATE"] = df.apply(get_cap_rate, axis=1)
    df["GROSS_REVENUE_MULTIPLICATOR"] = df.apply(get_gross_revenue_mult, axis=1)
    df["UNIT_PRICE"] = df.apply(get_unit_price, axis=1)
    df["NET_REVENUE_MULTIPLICATOR"] = df.apply(get_net_norm_income, axis=1)
    return df


if __name__ == "__main__":
    file = 'datasets/sherbrooke/COMP_SALE_SB_EXTRACT_20201019.csv'
    df = pd.read_csv(file)
    df_kpi = get_kpi(df)
    df_kpi.to_csv(r'datasets/sherbrooke/COMP_SALE_SB_EXTRACT_KPI_20201020.csv', index=False)
