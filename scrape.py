import requests
import sys
import re
import logging
import schedule
import time
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from collections import OrderedDict
from models import *
import peewee
from slack_notifications import *


def getThePageSourceAndReturnListOfAllVacancies(url):

    dictToBeReturned = {}

    # get the page source
    try:
        logging.info("Attempting to get page source code...")
        page = requests.get(url)
    except requests.exceptions.RequestException as e:
        logging.error(e)
        sys.exit(1)

    soup = BeautifulSoup(page.content, "html.parser")

    # get only the listings
    list_of_vacancies = soup.find_all("a", {"class": "vip"})

    # capture the vacancy id from the href
    pattern = "(\d{5,7})"
    for i in list_of_vacancies:
        search = re.search(pattern, i.get("href"))
        if search:
            href = search.group(1)

        dictToBeReturned.update({i.get_text(): href})

    return dictToBeReturned


def searchThroughListForPossibleKeywordsAndReturnTop70Results(
    vacancy_href_dict, aboveRating
):

    results = {}
    results_top_X = {}

    keywords = "DevOps Automation QA Quality Assurance Engineer"

    for key, value in vacancy_href_dict.items():
        result = fuzz.partial_ratio(keywords.lower(), key.lower())
        if result is not None:
            results.update({result: value})

    results_O = OrderedDict(sorted(results.items(), reverse=True))

    for key, value in results.items():
        if key >= aboveRating:
            results_top_X.update({key: value})

    return results_top_X


def getTheVacancyTitleAndFullLink(full_list, top_list):
    title_full_href = {}

    for k, v in full_list.items():
        for kr, vr in top_list.items():
            if v in vr:
                title_full_href.update({k: "/en/?view=jobs&id=" + vr})

    return title_full_href


def checkIfNotificationIsAlreadySent(post_id, top_list):

    # top list is a dict that consists of vancancy_rank and vancancy_id i.e. { 78 : 33445 }
    for k, v in top_list.items():
        if v in post_id:
            return True
        else:
            return False


def main():
    logging.info("Starting app..")

    create_tables()

    listOB = getThePageSourceAndReturnListOfAllVacancies(
        "https://jobs.ge/en/?page=1&q=&cid=6&lid=&jid="
    )

    keywords = ["DevOps", "Automation", "QA", "Quality Assurance", "python"]

    # Loop through list of vacancies and write those to DB with match of > 80.
    for i, v in listOB.items():
        i_l = i.lower()
        for k in keywords:
            match_score = fuzz.partial_ratio(k.lower(), i.lower())
            if match_score >= 80:
                logging.info(
                    "Found match! Score: "
                    + str(match_score)
                    + " for position: "
                    + i
                    + " with keyword: "
                    + k
                )
                query = Vacancy.select().where(Vacancy.vacancy_list_id == v)
                if not query.exists():
                    logging.info("New entry found. writing to db.")
                    record = Vacancy(
                        vacancy_title=i,
                        rating=match_score,
                        vacancy_list_id=v,
                        notification_sent="",
                    )
                    record.save()

    # Loop through DB and and get all vacancies that have no notification sent
    query = Vacancy.select().where(Vacancy.notification_sent == "")
    if not query.exists():
        logging.info("All notifications have been sent.")
    else:
        vacanvy_query_from_db = list(query)

        for i in vacanvy_query_from_db:
            if send_notification(i.vacancy_title, i.rating):
                update_empty = Vacancy.update(notification_sent=time.time()).where(
                    Vacancy.vacancy_list_id == i.vacancy_list_id
                )
                if update_empty.execute() == 1:
                    logging.info("Successfuly sent notification and updated db!")
                else:
                    logging.error("More than one row updated! Something went wrong!")
            else:
                logging.error("Error snding notification")


schedule.every(1).minutes.do(main)

while True:
    logging.basicConfig(level=logging.DEBUG)
    schedule.run_pending()
    time.sleep(1)
