from playwright.sync_api import sync_playwright
import os
 
 
DOWNLOAD_FOLDER = "downloads"
 
 
def download_file():
 
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
 
    # ====================================
    # START PLAYWRIGHT MANUALLY
    # ====================================
 
    p = sync_playwright().start()
 
    try:
 
        # ====================================
        # OPEN BROWSER
        # ====================================
 
        browser = p.chromium.launch(
            headless=False,
            slow_mo=300
        )
 
        context = browser.new_context(
            accept_downloads=True
        )
 
        page = context.new_page()
 
        print("\nOpening TappetBox...\n")
 
        # ====================================
        # OPEN WEBSITE
        # ====================================
 
        page.goto("https://www.tappetbox.in/my_dashboard")
 
        page.wait_for_timeout(1500)
 
        # ====================================
        # AUTO LOGIN
        # ====================================

        from dotenv import load_dotenv
        load_dotenv()

        group_id = os.getenv("TAPPETBOX_GROUP_ID")
        user_id = os.getenv("TAPPETBOX_USER_ID")
        password = os.getenv("TAPPETBOX_PASSWORD")

        print("\nLogging into TappetBox automatically...\n")

        # Enter Group ID
        page.locator("input[placeholder='Enter Group/Company ID']").fill(group_id)
        page.wait_for_timeout(500)

        # Enter User ID
        page.locator("input[placeholder='Enter Mobile Number']").fill(user_id)
        page.wait_for_timeout(500)

        # Click Submit
        page.locator("button:has-text('Submit')").click()
        page.wait_for_timeout(2000)

        # Enter Password
        page.locator("input[type='password']").fill(password)
        page.wait_for_timeout(500)

        # Click Login
        # Click Login — use exact match to avoid OTP button
        page.get_by_role("button", name="Login", exact=True).click()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)

        print("\nLogin successful!\n")
 
        # ====================================
        # OPEN SIDEBAR REPORTS
        # ====================================
 
        print("\nOpening sidebar Reports...\n")
 
        page.locator("text=Reports").first.click()
 
        page.wait_for_timeout(800)
 
        # ====================================
        # OPEN SUBMENU REPORTS
        # ====================================
 
        print("\nOpening submenu Reports...\n")
 
        page.locator("text=Reports").nth(1).click()
 
        page.wait_for_timeout(1500)
 
        # ====================================
        # OPEN ASSET PERFORMANCE MATRIX
        # ====================================
 
        print("\nOpening Asset Performance Matrix...\n")
 
        page.locator("text=Asset Performance Matrix").first.click()
 
        page.wait_for_timeout(1500)
 
        print("\nAsset Performance Matrix opened successfully.\n")
 
        # ====================================
        # SELECT DRILL RIG
        # ====================================
 
        print("\nSelecting DRILL RIG...\n")
 
        page.locator("text=Select Asset Type Group").click()
 
        page.wait_for_timeout(800)
 
        page.get_by_text(
            "DRILL RIG",
            exact=True
        ).last.click()
 
        page.wait_for_load_state("networkidle")
 
        page.wait_for_timeout(1500)
 
        print("\nDRILL RIG selected.\n")
 
        # ====================================
        # SELECT PREVIOUS MONTH
        # ====================================
 
        print("\nSelecting Previous Month...\n")
 
        page.locator("text=Select Period").click()
 
        page.wait_for_timeout(800)
 
        page.get_by_text(
            "Previous Month",
            exact=True
        ).last.click()
 
        page.wait_for_load_state("networkidle")
 
        page.wait_for_timeout(1500)
 
        print("\nPrevious Month selected.\n")
 
        # ====================================
        # GENERATE REPORT
        # ====================================
 
        print("\nGenerating report...\n")
 
        page.click("text=Show Report")
 
        page.wait_for_timeout(1500)
 
        # ====================================
        # DOWNLOAD MENU
        # ====================================
 
        print("\nOpening download menu...\n")
 
        page.locator(
            "button:has(svg)"
        ).nth(1).click()
 
        page.wait_for_timeout(800)
 
        print("\nSelecting Download Detailed Report...\n")
 
        page.get_by_role(
            "link",
            name="Download Detailed Report"
        ).click()
 
        page.wait_for_timeout(1500)
 
        # ====================================
        # OPEN REQUEST QUEUE
        # ====================================
 
        print("\nOpening request queue...\n")
 
        page.click("text=View")
 
        page.wait_for_timeout(1500)
 
        # ====================================
        # WAIT FOR ACTIVE STATUS
        # ====================================
 
        print("\nWaiting for report generation...\n")
 
        while True:
 
            try:
 
                page.goto(
                    "https://www.tappetbox.in/report/download_request",
                    wait_until="domcontentloaded"
                )
 
                page.wait_for_timeout(3000)
 
                first_status = page.locator(
                    "table tbody tr"
                ).first.locator("td").nth(4).inner_text()
 
                print(f"Current Status: {first_status}")
 
                if "Active" in first_status:
                    print("\nLatest report is ACTIVE.\n")
                    break
 
                elif "Pending" in first_status:
                    print("Latest report still PENDING...")
 
                elif "In-Progress" in first_status:
                    print("Latest report IN-PROGRESS...")
 
            except Exception as e:
                print("Refresh issue:", e)
 
            page.wait_for_timeout(5000)
 
        # ====================================
        # DOWNLOAD ASSET PERFORMANCE MATRIX
        # ====================================
 
        print("\nDownloading Asset Performance Matrix report...\n")
 
        with page.expect_download() as download_info:
            page.get_by_text(
                "Download Report"
            ).first.click()
 
        download = download_info.value
 
        performance_path = os.path.join(
            DOWNLOAD_FOLDER,
            "tappetbox_report.csv"
        )
 
        download.save_as(performance_path)
 
        if os.path.exists(performance_path):
            file_size = os.path.getsize(performance_path)
            if file_size > 0:
                print(f"\nAsset Performance Matrix downloaded:\n{performance_path}\n")
            else:
                print("\nAsset Performance Matrix file is empty.\n")
                return None, None
        else:
            print("\nAsset Performance Matrix download failed.\n")
            return None, None
 
        # ====================================
        # NAVIGATE TO MTTR & MTBF REPORT
        # ====================================
 
        print("\nNavigating to Asset MTTR & MTBF Report...\n")
 
        page.goto(
            "https://www.tappetbox.in/report/asset_mttr_mtbf_report",
            wait_until="domcontentloaded"
        )
 
        page.wait_for_timeout(2000)
 
        # ====================================
        # SELECT DRILL RIG FOR MTTR REPORT
        # ====================================
 
        print("\nSelecting DRILL RIG for MTTR report...\n")
 
        page.locator("text=Select Asset Type Group").click()
 
        page.wait_for_timeout(800)
 
        page.get_by_text(
            "DRILL RIG",
            exact=True
        ).last.click()
 
        page.wait_for_load_state("networkidle")
 
        page.wait_for_timeout(1500)
 
        print("\nDRILL RIG selected for MTTR report.\n")
 
        # ====================================
        # SELECT PREVIOUS MONTH FOR MTTR REPORT
        # ====================================
 
        print("\nSelecting Previous Month for MTTR report...\n")
 
        page.locator("text=Select Period").click()
 
        page.wait_for_timeout(800)
 
        page.get_by_text(
            "Previous Month",
            exact=True
        ).last.click()
 
        page.wait_for_load_state("networkidle")
 
        page.wait_for_timeout(1500)
 
        print("\nPrevious Month selected for MTTR report.\n")
 
        # ====================================
        # GENERATE MTTR REPORT
        # ====================================
 
        print("\nGenerating MTTR & MTBF report...\n")
 
        page.click("text=Show Report")
 
        page.wait_for_load_state("networkidle")
 
        page.wait_for_timeout(4000)
 
        # ====================================
        # DOWNLOAD MTTR & MTBF REPORT
        # ====================================
 
        print("\nDownloading MTTR & MTBF report...\n")

        # Wait longer for download
        # Wait for report to fully load
        page.wait_for_timeout(3000)

        with page.expect_download(timeout=60000) as download_info:
            # Click download button using nth — 
            # 0=Change Filter, 1=Download, 2=Close
            page.locator(
                "div.text-end button"
            ).nth(1).click()

        download = download_info.value
 
        mttr_path = os.path.join(
            DOWNLOAD_FOLDER,
            "mttr_mtbf_report.xlsx"
        )
 
        download.save_as(mttr_path)
 
        if os.path.exists(mttr_path):
            file_size = os.path.getsize(mttr_path)
            if file_size > 0:
                print(f"\nMTTR & MTBF Report downloaded:\n{mttr_path}\n")
            else:
                print("\nMTTR & MTBF file is empty.\n")
                return performance_path, None
        else:
            print("\nMTTR & MTBF download failed.\n")
            return performance_path, None
 
        # ====================================
        # CLOSE BROWSER
        # ====================================
 
        print("\nClosing browser...\n")
 
        try:
            browser.close()
        except:
            pass
 
        try:
            p.stop()
        except:
            pass
 
        return str(performance_path), str(mttr_path)
 
    except Exception as e:
 
        print("\nAutomation Error:\n", e)
 
        try:
            browser.close()
        except:
            pass
 
        try:
            p.stop()
        except:
            pass
 
        return None, None