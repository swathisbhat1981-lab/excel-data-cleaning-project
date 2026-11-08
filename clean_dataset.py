
import sys
import pandas as pd


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)

    print(f"Loaded {len(df)} rows, {len(df.columns)} columns.")

    return df


def phase1_handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:

    before = df["CouponCode"].isna().sum()

    df["CouponCode"] = df["CouponCode"].fillna("No Coupon")

    after = df["CouponCode"].isna().sum()

    print(
        f"Phase 1: CouponCode nulls filled "
        f"({before} -> {after}) using explicit 'No Coupon' category."
    )

    return df


def phase2_remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:

    full_dupes = df.duplicated().sum()
    order_id_dupes = df["OrderID"].duplicated().sum()
    tracking_dupes = df["TrackingNumber"].duplicated().sum()

    print(f"Phase 2: Full-row duplicates found: {full_dupes}")
    print(f"Phase 2: Duplicate OrderIDs found: {order_id_dupes}")
    print(f"Phase 2: Duplicate TrackingNumbers found: {tracking_dupes}")

    if full_dupes > 0:
        df = df.drop_duplicates()

        print(f"  -> Dropped {full_dupes} full-row duplicates.")

    if order_id_dupes > 0:
        df = df.drop_duplicates(subset="OrderID", keep="first")

        print(
            f"  -> Dropped {order_id_dupes} duplicate OrderID rows "
            f"(kept first occurrence)."
        )

    if full_dupes == 0 and order_id_dupes == 0 and tracking_dupes == 0:
        print("  -> No duplicates found. Dataset already passes this gate.")

    return df


def phase3_standardize_formats(df: pd.DataFrame) -> pd.DataFrame:

    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")

    title_case_cols = [
        "Product",
        "PaymentMethod",
        "OrderStatus",
        "ReferralSource"
    ]

    strip_only_cols = [
        "ShippingAddress",
        "CouponCode"
    ]

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

    df["UnitPrice"] = df["UnitPrice"].round(2)

    df["TotalPrice"] = df["TotalPrice"].round(2)

    print("Phase 3: Dates converted to ISO 8601 (YYYY-MM-DD).")

    print(f"Phase 3: Text formatting corrections applied: {changes} cells.")

    print(
        "Phase 3: Numeric precision enforced to 2 decimals "
        "on UnitPrice and TotalPrice."
    )

    return df


def verification_gate(df: pd.DataFrame) -> bool:

    dup_ids = df["OrderID"].duplicated().sum()

    bad_dates = (
        ~df["Date"].astype(str).str.match(r"^\d{4}-\d{2}-\d{2}$")
    ).sum()

    print("\n--- VERIFICATION GATE ---")

    print(
        f"Duplicate OrderIDs: {dup_ids} "
        f"({'PASS' if dup_ids == 0 else 'FAIL'})"
    )

    print(
        f"Incorrectly formatted dates: {bad_dates} "
        f"({'PASS' if bad_dates == 0 else 'FAIL'})"
    )

    passed = dup_ids == 0 and bad_dates == 0

    print(
        "RESULT:",
        "PASSED - Ready for Project 2"
        if passed
        else "FAILED - Fix issues above"
    )

    return passed


def main():

    if len(sys.argv) != 3:

        print(
            "Usage: python clean_dataset.py "
            "input_file.xlsx output_file.xlsx"
        )

        sys.exit(1)

    input_path = sys.argv[1]

    output_path = sys.argv[2]

    df = load_data(input_path)

    df = phase1_handle_missing_values(df)

    df = phase2_remove_duplicates(df)

    df = phase3_standardize_formats(df)

    verification_gate(df)

    df.to_excel(output_path, index=False)

    print(f"\nCleaned file saved to: {output_path}")


if __name__ == "__main__":
    main()
