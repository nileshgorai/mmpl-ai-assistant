import pandas as pd
import openpyxl


def load_mttr_data(xlsx_path):

    print("\nLoading MTTR & MTBF Report...\n")

    # =========================================
    # READ MAIN SHEET — ASSET MTTR MTBF
    # =========================================

    df_main = pd.read_excel(
        xlsx_path,
        sheet_name="Asset MTTR MTBF Report",
        header=5,
        engine="openpyxl",
        usecols="A:I",
        dtype={"Asset Name": str, "Asset Code": str}
    )

    # Fix Asset Name — combine split columns if needed
    if "Asset Name" in df_main.columns:
        df_main["Asset Name"] = df_main["Asset Name"].astype(str).str.strip()

    # =========================================
    # CLEAN MAIN SHEET
    # =========================================

    df_main = df_main.dropna(how="all")
    df_main = df_main.dropna(axis=1, how="all")
    df_main = df_main.reset_index(drop=True)

    # Remove Running-KM column as it's always 0
    if "Running - KM" in df_main.columns:
        df_main = df_main.drop(columns=["Running - KM"])

    # Fill NaN with 0 for ticket columns explicitly
    for col in ["Number of Tickets", "Repair Tickets"]:
        if col in df_main.columns:
            df_main[col] = df_main[col].fillna(0).astype(int)

    # Clean column names
    df_main.columns = [
        str(col).strip()
        for col in df_main.columns
    ]

    # Smart fillna
    for col in df_main.columns:
        if df_main[col].dtype == object:
            df_main[col] = df_main[col].fillna("")
        else:
            df_main[col] = df_main[col].fillna(0)

    print("\n===== MTTR MAIN DATA LOADED =====\n")
    print(f"Shape: {df_main.shape}")
    print(f"Columns: {df_main.columns.tolist()}")

    # =========================================
    # READ REPAIR TICKETS SHEET
    # =========================================

    df_tickets = pd.read_excel(
        xlsx_path,
        sheet_name="Repair Tickets",
        header=5,
        engine="openpyxl",
        usecols="A:X"
    )

    # =========================================
    # CLEAN TICKETS SHEET
    # =========================================

    df_tickets = df_tickets.dropna(how="all")
    df_tickets = df_tickets.dropna(axis=1, how="all")
    df_tickets = df_tickets.reset_index(drop=True)

    df_tickets.columns = [
        str(col).strip()
        for col in df_tickets.columns
    ]

    for col in df_tickets.columns:
        if df_tickets[col].dtype == object:
            df_tickets[col] = df_tickets[col].fillna("")
        else:
            df_tickets[col] = df_tickets[col].fillna(0)

    print("\n===== REPAIR TICKETS DATA LOADED =====\n")
    print(f"Shape: {df_tickets.shape}")
    print(f"Columns: {df_tickets.columns.tolist()}")

    return df_main, df_tickets


if __name__ == "__main__":
    df_main, df_tickets = load_mttr_data(
        "downloads/mttr_mtbf_report.xlsx"
    )
    print("\nMain Data Sample:")
    print(df_main.head())
    print("\nTickets Sample:")
    print(df_tickets.head())