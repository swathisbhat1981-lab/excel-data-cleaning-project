"""
DecodeLabs - Data Analytics Internship - Project 1
Data Cleaning & Preparation Script

This script performs the 3-phase cleaning process from the training kit:
  Phase 1: Strategic Imputation (handle missing values)
  Phase 2: Integrity Audit (remove duplicates)
  Phase 3: Speak One Language (standardize formatting)

Then it verifies the "0% error" gate required before Project 2.

Usage:
    python clean_dataset.py input_file.xlsx output_file.xlsx
"""

import sys
import pandas as pd


def load_data(path: str) -> pd.DataFrame:
    """Load the raw dataset."""
    df = pd.read_excel(path)
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns.")
    return df


def phase1_handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill or flag missing values.

    IMPORTANT LESSON: not every blank cell should be statistically imputed
    (mean/median/mode). A blank can also be a legitimate category meaning
    "this doesn't apply" or "none was used." Check what the blank *means*
    before deciding how to fill it.

    In this dataset, only CouponCode has nulls (309 / 1200 rows). A blank
    CouponCode means "no coupon was applied to this order" -- it is real
    information, not noise. So we encode it explicitly rather than guessing
    a coupon code with mode-imputation, which would fabricate data.
    """
    before = df["CouponCode"].isna().sum()
    df["CouponCode"] = df["CouponCode"].fillna("No Coupon")
    after = df["CouponCode"].isna().sum()
    print(f"Phase 1: CouponCode nulls filled ({before} -> {after}) using explicit "
          f"'No Coupon' category (not mean/median/mode, since blank = a real state).")

    # General-purpose pattern for other columns, if a future dataset needs it:
    # numeric_cols = df.select_dtypes(include="number").columns
    # for col in numeric_cols:
    #     if df[col].isna().any():
    #         df[col] = df[col].fillna(df[col].median())  # median resists outliers
    # categorical_cols = df.select_dtypes(include="object").columns
    # for col in categorical_cols:
    #     if df[col].isna().any():
    #         df[col] = df[col].fillna(df[col].mode()[0])

    return df


def phase2_remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Audit for duplicate records.
    Checks full-row duplicates AND duplicate unique keys (OrderID, TrackingNumber),
    since two rows can differ slightly (e.g. re-typed) but still represent the
    same real-world order.
    """
    full_dupes = df.duplicated().sum()
    order_id_dupes = df["OrderID"].duplicated().sum()
    tracking_dupes = df["TrackingNumber"].duplicated().sum()

    print(f"Phase 2: full-row duplicates found: {full_dupes}")
    print(f"Phase 2: duplicate OrderIDs found: {order_id_dupes}")
    print(f"Phase 2: duplicate TrackingNumbers found: {tracking_dupes}")

    if full_dupes > 0:
        df = df.drop_duplicates()
        print(f"  -> Dropped {full_dupes} full-row duplicates.")
    if order_id_dupes > 0:
        df = df.drop_duplicates(subset="OrderID", keep="first")
        print(f"  -> Dropped {order_id_dupes} duplicate OrderID rows (kept first occurrence).")

    if full_dupes == 0 and order_id_dupes == 0 and tracking_dupes == 0:
        print("  -> No duplicates found. Dataset already passes this gate.")

    return df


def phase3_standardize_formats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize dates, text case/whitespace, and numeric precision.
    """
    # Dates -> ISO 8601
    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")

    # Text columns -> trim whitespace, consistent title case.
    # NOTE: ShippingAddress (free text) and CouponCode (uppercase code convention,
    # e.g. "SAVE10") are intentionally excluded from title-casing -- title-casing
    # a code like "SAVE10" would turn it into "Save10", which is a corruption,
    # not a fix. Only trim whitespace on those two.
    title_case_cols = ["Product", "PaymentMethod", "OrderStatus", "ReferralSource"]
    strip_only_cols = ["ShippingAddress", "CouponCode"]
    changes = 0
    for col in title_case_cols:
        original = df[col].astype(str)
        cleaned = original.str.strip().str.title()
        changes += (original != cleaned).sum()
        df[col] = cleaned
    for col in strip_only_cols:
        original = df[col].astype(str)
        cleaned = original.str.strip()
        changes += (original != cleaned).sum()
        df[col] = cleaned

    # Numeric precision -> 2 decimals for currency fields
    df["UnitPrice"] = df["UnitPrice"].round(2)
    df["TotalPrice"] = df["TotalPrice"].round(2)

    print(f"Phase 3: dates converted to ISO 8601 (YYYY-MM-DD).")
    print(f"Phase 3: text formatting corrections applied: {changes} cell(s).")
    print(f"Phase 3: numeric precision enforced to 2 decimals on UnitPrice/TotalPrice.")

    return df


def verification_gate(df: pd.DataFrame) -> bool:
    """
    The kit's "0% error" checkpoint before Project 2:
      - 0% duplicate unique identifiers
      - 0% incorrectly formatted dates
    Returns True if the dataset passes.
    """
    dup_ids = df["OrderID"].duplicated().sum()
    bad_dates = (~df["Date"].astype(str).str.match(r"^\d{4}-\d{2}-\d{2}$")).sum()

    print("\n--- VERIFICATION GATE ---")
    print(f"Duplicate OrderIDs: {dup_ids}  ({'PASS' if dup_ids == 0 else 'FAIL'})")
    print(f"Incorrectly formatted dates: {bad_dates}  ({'PASS' if bad_dates == 0 else 'FAIL'})")

    passed = dup_ids == 0 and bad_dates == 0
    print("RESULT:", "PASSED - ready for Project 2" if passed else "FAILED - fix issues above")
    return passed


def main():
    if len(sys.argv) != 3:
        print("Usage: python clean_dataset.py input_file.xlsx output_file.xlsx")
        sys.exit(1)

    input_path, output_path = sys.argv[1], sys.argv[2]

    df = load_data(input_path)
    df = phase1_handle_missing_values(df)
    df = phase2_remove_duplicates(df)
    df = phase3_standardize_formats(df)
    verification_gate(df)

    df.to_excel(output_path, index=False)
    print(f"\nCleaned file saved to: {output_path}")


if __name__ == "__main__":
    main()
