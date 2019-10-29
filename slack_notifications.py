import requests, json, logging, os
from dotenv import load_dotenv

load_dotenv()

slack_hook = os.getenv("SLACK_HOOK_URL")


def send_block_notification(number_of_new_vacancies, payload):
    headers_slack = {"Content-Type": "application/json"}
    slack_payload = json.dumps(
        {
            "attachments": [
                {
                    "pretext": "New vacancies posted! :innocent: :ghost: :man-cartwheeling:",
                    "title": number_of_new_vacancies + "new have been posted!",
                    "text": "Error code: "
                    + str(r.status_code)
                    + " Response: "
                    + r.text,
                    "color": "#7CD197",
                }
            ]
        }
    )

    p_res = requests.post(slack_hook, headers=headers_slack, data=slack_payload)

    if p_res.status_code != 200:
        raise ValueError(
            "Send requuest to payload to slack failed! %s, respose: \n%s",
            p_res.status_code,
            p_res.text,
        )

        return False
    else:
        return True


def send_notification(vacancy_title, vacancy_rating):
    headers_slack = {"Content-Type": "application/json"}
    slack_payload = json.dumps(
        {
            "attachments": [
                {
                    "pretext": "New vacancies posted! :innocent: :ghost: :man-cartwheeling:",
                    "title": "New vancancy have been posted!",
                    "text": "Vacancy title: "
                    + vacancy_title
                    + " with rating: "
                    + str(vacancy_rating),
                    "color": "#7CD197",
                }
            ]
        }
    )

    p_res = requests.post(slack_hook, headers=headers_slack, data=slack_payload)

    if p_res.status_code != 200:
        raise ValueError(
            "Send requuest to payload to slack failed! %s, respose: \n%s",
            p_res.status_code,
            p_res.text,
        )

        return False
    else:
        return True


def send_fake_notification(vacancy_title, vacancy_rating):
    logging.info("Sending notification " + vacancy_title + " " + str(vacancy_rating))

    return True

