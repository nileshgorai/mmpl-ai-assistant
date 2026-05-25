import pandas as pd

def load_and_clean_data(csv_path):

    # =========================================
    # SCAN FOR REAL HEADER ROW
    # =========================================

    header_row = None

    with open(csv_path, encoding="utf-8-sig") as f:
        for i, line in enumerate(f):
            if "Asset Name" in line and "Asset Code" in line:
                header_row = i
                print(f"\nHEADER FOUND AT ROW: {i}")
                break

    if header_row is None:
        raise Exception("Could not detect actual report table header.")

    # =========================================
    # LOAD CLEAN TABLE FROM REAL HEADER
    # =========================================

    df = pd.read_csv(
        csv_path,
        skiprows=header_row,
        encoding="utf-8-sig",
        engine="python",
        on_bad_lines="skip",
    )

    # =========================================
    # DROP FOOTER ROWS (e.g. "Powered by TappetBox")
    # =========================================

    df = df[df["Asset Name"].notna()]
    df = df[~df["Asset Name"].str.contains("Powered by", na=True)]

    # =========================================
    # REMOVE EMPTY COLUMNS & ROWS
    # =========================================

    df = df.dropna(axis=1, how="all")
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df = df.dropna(axis=0, how="all")
    df = df.reset_index(drop=True)

    # =========================================
    # CLEAN COLUMN NAMES
    # =========================================

    df.columns = [str(col).strip() for col in df.columns]

    # =========================================
    # SMART FILL — numeric → 0, text → ""
    # =========================================

    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].fillna("")
        else:
            df[col] = df[col].fillna(0)

    # =========================================
    # CONVERT NUMERIC COLUMNS
    # =========================================

    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col], errors="ignore")
        except:
            pass

    df = df.drop_duplicates()

    print("\n===== CLEAN DATASET LOADED =====\n")
    print(f"Shape: {df.shape}")
    print("\n===== COLUMNS =====\n")
    print(df.columns.tolist())

    return df