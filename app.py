from flask import Flask, render_template, request 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

def web_scraper(url):
    try:
        # Use a headless browser (e.g., Chrome) for dynamic content
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=options)

        # Load the URL in the browser
        driver.get(url)

        # Scroll down to trigger dynamic content loading
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)  # Adjust sleep time based on the page's loading speed

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break  # Break the loop if no more content is loaded
            last_height = new_height

        # Wait for the 'job' divs to be present on the page
        # Wait for dynamic content to load (increase wait time if needed)
        wait = WebDriverWait(driver, 120)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'base-search-card__info')))

        # Get the HTML content after JavaScript execution
        html = driver.page_source

        # Close the browser
        driver.quit()

        # Parse the HTML content of the page
        soup = BeautifulSoup(html, 'html.parser')
            
            
        results = []
        job_divs = soup.find_all('div', class_ ='base-search-card__info')
        # print('..........',len(job_divs),'<<<<<<<<')

        
        
        for job_div in job_divs:
            #print("Processing a job element.")
            jobTitle = job_div.find('h3', class_ = 'base-search-card__title') 
            companyName = job_div.find('h4', class_ = 'base-search-card__subtitle') 

            if jobTitle and companyName:
                jobTitle = jobTitle.text.strip() 
                companyName = companyName.text.strip()
                # print(f"Job Title: {jobTitle}")
                # print(f"Company Name: {companyName}")

            companyLocation = job_div.find('span', class_ = 'job-search-card__location') 
            listDate = job_div.find('time', class_ = 'job-search-card__listdate') 

            if companyLocation and listDate:
                companyLocation = companyLocation.text.strip()
                listDate = listDate.text.strip()
                # print(f"Company Location: {companyLocation}")
                # print(f"List Date: {listDate}")

                results.append({
                    'jobTitle': jobTitle, 
                    'companyName': companyName,
                    'companyLocation': companyLocation,
                    'listDate' : listDate
                })
        
        print(len(results))         
        return results
        
    except Exception as e:
        return {'error': str(e)}
        
# # Example usage for console testing
# user_url = input("Enter a URL: ")
# result = web_scraper(user_url)

# #Print or use the result as needed
# print(result)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        user_url = request.form['url']
        
        # Use get method with a default value to avoid KeyError
        # filter_word = request.form.get('filter', '')

        result = web_scraper(user_url)
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)


'''

container div = >  class="base-search-card__info"

jobTitle = 
<h3 class="base-search-card__title"> Manufacturing Engineer/2nd Shift </h3>

companyName = 
<h4 class="base-search-card__subtitle">  <a class="hidden-nested-link" data-tracking-client-ingraph="" data-tracking-control-name="public_jobs_jserp-result_job-search-card-subtitle" data-tracking-will-navigate="" href="https://www.linkedin.com/company/lockheed-martin?trk=public_jobs_jserp-result_job-search-card-subtitle"> Lockheed Martin </a></h4>

companyLocation = 
<span class="job-search-card__location"> Orlando, FL </span>

listedDate = 
<time class="job-search-card__listdate" datetime="2023-09-12">2 months ago </time>
 '''