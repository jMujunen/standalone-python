#!/usr/bin/env python3 

# remote_jobs_scrape_main.py - Scrapes remote jobs from  Indeed and LinkedIn

import sys
import argparse

import requests
from bs4 import BeautifulSoup
from datetime import datetime

def parse_args():
    parser = argparse.ArgumentParser(description='Scrape remote jobs from Indeed and LinkedIn')
    parser.add_argument('filename', type=str, help='Filename to save results')
    parser.add_argument('location', type=str, help='Location to search')
    parser.add_argument('-k', '--keywords', type=list, help='Keywords to search', required=False)

    return parser.parse_args()

    
def convert_to_markdown_table(sites):

    markdown_table = "Title|Company|Location|Link\n"
    markdown_table += "---|---|---|---\n"
    for site in sites:
            for job in site:
                title = job.find('h3', class_='base-search-card__title').text.strip()
                company = job.find('h4', class_='base-search-card__subtitle').text.strip()
                location = job.find('span', class_='job-search-card__location').text.strip()
                link = job.find('a', class_="base-card__full-link absolute top-0 right-0 bottom-0 left-0 p-0 z-[2]")['href']

                markdown_table += f"{title}|{company}|{location}|[Link]({link})\n"

                print(f"{title} @ {company}")
                print(f"{'-'*30}")
                
    return markdown_table


def get_remote_jobs(location, filename):
    urls = ['https://www.linkedin.com/jobs/search/?currentJobId=3689657922&geoId=101174742&keywords=remote&location=Canada','https://www.linkedin.com/jobs/search/?currentJobId=3806762802&keywords=abbotsford']
    joblist = []
    for url in urls:
        response = requests.get(url)

        soup = BeautifulSoup(response.content, 'html.parser')
        linkedin_job_listings = soup.find_all('div', class_="base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card")
        #indeed_job_listings = soup.find_all('div', class_="gnav-Logo-icon")
        #joblist.append(indeed_job_listings)
        joblist.append(linkedin_job_listings)
        
        # TODO: Implement keywords, location as args
        # TODO - keywords = ['rental',
        # TODO -          'coordinator', 'system admin', 'dispatch', 'Millwright', 'Heavy machinery', 'mechanic', 'excel', 'office', 'microsoft', 'install', 'service', 'no experiance']

    # Write markdown table to file
    try:
        with open(f"/home/joona/Docs/{filename}", 'w') as file:
            file.write(f'# {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  \n\n')
            file.writelines(convert_to_markdown_table(joblist))

    except Exception as e:
        with open("C:\\Users\\Ella\\Documents\\JobScrape.md", 'w') as file:
            file.write(f'# {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  \n\n')
            file.writelines(convert_to_markdown_table(joblist))


if __name__ == '__main__':
    args = parse_args()
    filename = args.filename + '.md'
    get_remote_jobs(filename, 'Abbotsford')





# -------------------------------------------------- #


'''
        for job in job_listings:
            title = job.find('h3', class_='base-search-card__title').text.strip()
            company = job.find('h4', class_='base-search-card__subtitle').text.strip()
            location = job.find('span', class_='job-search-card__location').text.strip()
            link = job.find('a', class_="base-card__full-link absolute top-0 right-0 bottom-0 left-0 p-0 z-[2]")['href']
            print(f"{title} @ {company}")
            with open("/home/joona/Documents/remote_jobs.md", 'a') as file:
                #file.writelines(f"Title: {title}\nCompany: {company}\nLocation: {location}\nLink: {link}\n{'-'*30}\n")
'''