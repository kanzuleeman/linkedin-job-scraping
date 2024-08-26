from selenium import webdriver
import pandas as pd
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import pickle

def load_create_cookies(driver, login_url, email, password,cookie_file='cookies.pkl'):
    """
    Load cookies from a file, or log in to create and save cookies if not available.

    :param driver: Selenium WebDriver instance
    :param login_url: The login URL for LinkedIn
    :param email: Email address for login
    :param password: Password for login
    :param cookie_file: File path for storing cookies
    """
    try:
        with open(cookie_file, 'rb') as file_obj:
            cookies = pickle.load(file_obj)
            for cookie in cookies:
                driver.add_cookie(cookie)
        print("Cookies loaded successfully.")
    except (FileNotFoundError, EOFError):
        driver.get(login_url)
        email_input = driver.find_element(By.ID, 'username')
        password_input = driver.find_element(By.ID, 'password')
        email_input.send_keys(email)
        password_input.send_keys(password)
        password_input.send_keys(Keys.ENTER)
        time.sleep(5)
        cookies = driver.get_cookies()
        with open(cookie_file, 'wb') as file_obj:
            pickle.dump(cookies, file_obj)
        print("Cookies saved successfully.")

def jobs_url(driver):
    """
    Extract job URLs from the LinkedIn job search page.

    :param driver: Selenium WebDriver instance
    :return: List of job URLs
    """
    links = []
    li_elements = driver.find_elements(By.CLASS_NAME, 'jobs-search-results__list-item')
    for li in li_elements:
        try:
            li.click()
            job_link = li.find_element(By.TAG_NAME, 'a')
            href = job_link.get_attribute('href')
            links.append(href)
        except NoSuchElementException:
            print("Job link not found.")
            continue
    return links

def job_info(driver, hrefs):
    
    titles = []
    companies = []
    skills_list = []
    locations = []

    for link in hrefs:
        driver.get(link)
        time.sleep(10)
        try:
            title = driver.find_element(By.CLASS_NAME, 't-24').text
            company = driver.find_element(By.CLASS_NAME, 'job-details-jobs-unified-top-card__company-name').text
            skills = driver.find_element(By.CLASS_NAME, 'job-details-how-you-match__skills-item-subtitle').text
            location = driver.find_element(By.CLASS_NAME, 'tvm__text').text
        except NoSuchElementException:
            title = None
            company = None
            skills = None
            location = None
        titles.append(title)
        companies.append(company)
        skills_list.append(skills)
        locations.append(location)
        print(f'title: {title}')
        print(f'company: {company}')
        print(f'skills: {skills}')
        print(f'location: {location}')
    
    return titles, companies, skills_list, locations

if __name__ == '__main__':
    
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    driver.get('https://linkedin.com/login')

    # Load cookies or perform login
    try:
        with open('cookies.pkl', 'rb') as file_obj:
            cookies = pickle.load(file_obj)
            for cookie in cookies:
                driver.add_cookie(cookie)
    except (FileNotFoundError, EOFError):
        driver.get('https://linkedin.com/login')  
        email_input = driver.find_element(By.ID, 'username')
        password_input = driver.find_element(By.ID, 'password')
        email_input.send_keys('your email')
        password_input.send_keys('password')
        password_input.send_keys(Keys.ENTER)
        time.sleep(5)  
        cookies = driver.get_cookies()
        with open('cookies.pkl', 'wb') as file_obj:
            pickle.dump(cookies, file_obj)

    job_title = []
    company_name = []
    req_skills = []
    Location = []

    keywords = ''
    start = 0
    pages_to_scrape = 8
    pages_scraped =0 
    
    while pages_scraped < pages_to_scrape:
        driver.get(f'https://www.linkedin.com/jobs/search/?keywords={keywords}&start={start}')
        time.sleep(5)
        links=[]

        # href_links = jobs_url(driver)
        li_elements=driver.find_elements(By.CLASS_NAME,'jobs-search-results__list-item')
        for li in li_elements:
            li.click()
            job_link=li.find_element(By.TAG_NAME,'a')
            href = job_link.get_attribute('href')
            links.append(href)
            # print(links)
        if not links:
            print('No more jobs found.')
            break
        
        titles, companies, skills_list, locations = job_info(driver, links)



        
        job_title.extend(titles)
        company_name.extend(companies)
        req_skills.extend(skills_list)
        Location.extend(locations)
        
        start += 25
        pages_scraped += 1
        time.sleep(5)

    # Save job data to CSV
    jobs_data = pd.DataFrame({
        'Job_title': job_title, 
        'Company_name': company_name, 
        'Skills': req_skills, 
        'Location': Location
    })
    jobs_data.to_csv('jobs_data.csv', index=False)
    print("Job data saved to 'jobs_data.csv'.")
    
    # Close the browser
    driver.quit()
