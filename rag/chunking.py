from langchain_text_splitters import RecursiveCharacterTextSplitter
import pandas as pd
from processing.read_data import load_and_clean_data
from processing.read_mttr_data import load_mttr_data
import os


def sanitize_value(value):
    # Replace | with / to prevent markdown table breaking
    return str(value).replace("|", "/")


def create_chunks(file_path, mttr_path=None):

    print("\nLoading file for chunking...\n")

    # =========================
    # LOAD PERFORMANCE DATA
    # =========================

    data = load_and_clean_data(file_path)
    data = data.drop_duplicates()
    data = data.dropna(how="all")
    data.columns = data.columns.str.strip()

    row_texts = []

    for _, row in data.iterrows():
        row_text = []
        for col in data.columns:
            value = sanitize_value(row[col])
            row_text.append(f"{col}: {value}")

        row_text.append("Source: Asset Performance Matrix Report")
        row_texts.append(" || ".join(row_text))

    print(f"\nPerformance Matrix rows: {len(row_texts)}\n")

    # =========================
    # LOAD MTTR & MTBF DATA
    # =========================

    if mttr_path and os.path.exists(mttr_path):

        try:
            df_main, df_tickets = load_mttr_data(mttr_path)

            for _, row in df_main.iterrows():
                row_text = []
                for col in df_main.columns:
                    value = sanitize_value(row[col])
                    row_text.append(f"{col}: {value}")

                row_text.append("Source: Asset MTTR MTBF Report")
                row_texts.append(" || ".join(row_text))

            print(f"\nMTTR main rows added: {len(df_main)}\n")

            for _, row in df_tickets.iterrows():
                row_text = []
                for col in df_tickets.columns:
                    value = sanitize_value(row[col])
                    row_text.append(f"{col}: {value}")

                row_text.append("Source: Repair Tickets")
                row_texts.append(" || ".join(row_text))

            print(f"\nRepair Ticket rows added: {len(df_tickets)}\n")

        except Exception as e:
            print(f"\nMTTR data loading error: {e}\n")

    else:
        print("\nNo MTTR file found — using Performance Matrix only.\n")

    # =========================
    # CREATE SPLITTER
    # =========================

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    chunks = []

    for row_text in row_texts:
        split_chunks = splitter.split_text(row_text)
        chunks.extend(split_chunks)

    print(f"\nTotal Chunks Created: {len(chunks)}\n")

    for i, chunk in enumerate(chunks[:3]):
        print(f"\n--- Chunk {i+1} ---\n")
        print(chunk)

    return chunks


if __name__ == "__main__":
    create_chunks(
        "downloads/tappetbox_report.csv",
        "downloads/mttr_mtbf_report.xlsx"
    )