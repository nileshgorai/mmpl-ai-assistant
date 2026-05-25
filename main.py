from automation.download_bot import download_file
from processing.read_data import load_and_clean_data


def run_download_pipeline():

    print("\n===== STARTING AI AUTOMATION SYSTEM =====\n")

    # STEP 1 → Download both reports
    performance_path, mttr_path = download_file()

    if not performance_path:
        print("\nFailed to download reports.\n")
        return None, None

    # STEP 2 → Read performance data
    data = load_and_clean_data(performance_path)
    print("\n===== DOWNLOAD COMPLETED =====\n")
    print(f"\nAsset Performance Matrix: {performance_path}")
    print(f"MTTR & MTBF Report: {mttr_path}\n")

    return performance_path, mttr_path


if __name__ == "__main__":

    performance_path, mttr_path = run_download_pipeline()

    print("\n===== PROCESS COMPLETED SUCCESSFULLY =====\n")