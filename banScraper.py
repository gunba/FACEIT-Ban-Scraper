from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv
import os
import re

def get_match_links(team_url):
    # Set up the Selenium webdriver
    driver = webdriver.Chrome()  

    try:
        # Navigate to the team stats page
        stats_url = team_url + "/stats"
        driver.get(stats_url)

        # Wait for the parasite container element to be visible and have the map list load
        def get_map_rows(i):
            # Scroll down to load more rows
            parasite_container = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "parasite-container"))
            )

             # Get the initial height of the parasite container
            initial_height = driver.execute_script("return arguments[0].scrollHeight", parasite_container)

            # Find the main container elements
            main_container_wrapper = driver.find_element(By.ID, "main-container-height-wrapper")

            # Track how many additional scrolls
            map_rows = 10

            # Scroll the parasite container until no more rows are loaded
            while True:
                # Scroll the main container wrapper
                driver.execute_script("arguments[0].scrollBy(0, 10000);", main_container_wrapper)
                time.sleep(1)  # Wait for the rows to load

                # Get the updated height of the parasite container
                new_height = driver.execute_script("return arguments[0].scrollHeight", parasite_container)

                # Output new height value
                print(new_height)

                # ? No more rows loaded, exit 
                if new_height == initial_height:
                    break  

                map_rows += 10
                initial_height = new_height

                # ? Enough rows loaded for processing, exit 
                if map_rows > i+5:
                    break

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@id='parasite-container']//table"))
            )

            header_element = parasite_container.find_element(By.XPATH, ".//div[contains(text(), 'Team Win')]")
            table_element = header_element.find_element(By.XPATH, "ancestor::table[1]")
            tbody_element = table_element.find_element(By.XPATH, "./tbody")
            return tbody_element.find_elements(By.XPATH, "./tr")

        # Pretty print a given selenium element
        def print_html_webelem(elem):
            table_html = elem.get_attribute("outerHTML")
            table_soup = BeautifulSoup(table_html, 'html.parser')
            print("Table HTML:")
            print(table_soup.prettify())

        # Get match rows
        map_rows = get_map_rows(0)

        # Skip count used to skip over maps in the same tournament as previous maps
        skip_count = 0

        # Must use while/true loop because the rowcount is dynamic
        i = 0

        # Store processed rows
        processed_rows = []

        while True:
            if skip_count > 0:
                # Skip the current row as it belongs to the same tournament
                skip_count -= 1
                i += 1
                continue

            # If we've exceeded the map rows even after the return, we have exhausted the list
            if i >= len(map_rows):
                print('Iterator is greater than maprows')
                break

            # Click on the row
            row = map_rows[i]
            row.click()
            
            # Wait for the matchroom scoreboard to load.
            matchroom_scoreboard = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "MATCHROOM-SCOREBOARD"))
            )

            # Wait for the round buttons to load. I assume there's a cleaner way to do this
            # i.e. Waiting until there is some number of divs under the scoreboard.
            time.sleep(1)  

            # Find the div that contains the round buttons
            round_buttons_container = matchroom_scoreboard.find_element(By.XPATH, ".//div[3]/div")

            # Find all the round buttons
            round_buttons = round_buttons_container.find_elements(By.XPATH, ".//button")

            # Determine the number of maps to skip ahead based on the number of round buttons
            skip_count = len(round_buttons) - 1
            
            # Get the current URL after the page loads
            match_url = driver.current_url

            # Tournament match url mined from map data
            print(match_url)

            # Click on the "Overview" span
            overview_span = driver.find_element(By.XPATH, "//span[text()='Overview']")
            overview_span.click()

            # Wait for the veto button to be present
            veto_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//span[@data-testid='mapsVetoHistory']"))
            )

            # Load the veto list
            veto_button.click()

            # Wait for the veto data (ol element) to be present
            veto_data = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//ol"))
            )

            # Extract veto data from the li elements
            veto_items = veto_data.find_elements(By.XPATH, ".//li")
            veto_list = []
            for index, item in enumerate(veto_items, start=1):
                veto_text = item.text
                veto_list.append(f"{index}. {veto_text}")

            # Row ID is the element ID at the end of the Selenium WebElement "element" value 
            row_id = re.findall(r'\.e\.(\d+)"', str(row))[-1]

            # Process the current row with veto data
            processed_row = {
                "row": row_id,
                "veto_data": veto_list
            }

            print(veto_list)

            processed_rows.append(processed_row)

            # Go back to the previous page (twice, since we are on Overview panel.)
            driver.back()
            driver.back()

            i += 1

            # Get rows again.
            map_rows = get_map_rows(i)

        # Output the processed rows as CSV
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "processed_rows.csv")

        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["row", "veto_data"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for row in processed_rows:
                writer.writerow(row)

        print(processed_rows)

    finally:
        driver.quit()

# Example usage
team_url = "https://www.faceit.com/en/teams/bb5dd404-213c-430f-8d12-8687fc3ff747"
get_match_links(team_url)

# Example output (will be in script dir as a .csv)
# row: "479", 'veto_data': ['1. LeftRightGnight banned Nepal', '2. Framedrop banned Samoa', ...