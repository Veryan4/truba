import os
import json
from pywebpush import webpush, WebPushException
from shared import setup, tracing
from services.story import story
from services.user import user, email

current_module = 'Push'
languages = ("en", "fr")

VAPID_PRIVATE_KEY = os.getenv("PRIVATE_VAPID")
VAPID_PUBLIC_KEY = os.getenv("PUBLIC_VAPID")
VAPID_CLAIMS = {
    "sub": "mailto:info@truba.news",
    "aud:": setup.get_client_domain_name()
}


def send_web_push(subscription_information, message_body):
  return webpush(subscription_info=subscription_information,
                 data=message_body,
                 vapid_private_key=VAPID_PRIVATE_KEY,
                 vapid_claims=VAPID_CLAIMS)


def push():
  for language in languages:
    news = story.get_public_stories(language)
    emails = user.get_emails(language)
    if emails:
      email.send_daily_snap_emails(emails, news)
    subscriptions = user.get_subscriptions(language)
    if subscriptions:
      for subscription in subscriptions:
        data = {
            "notification": {
                "title": news[0].title,
                "icon": 'assets/truba-logo-square.svg'
            }
        }
        try:
          send_web_push(subscription, json.dumps(data))
        except WebPushException as ex:
          tracing.log(current_module, 'error',
                      "ERROR sending push notification")
          if ex.response and ex.response.json():
            extra = ex.response.json()
            message = f"""Remote service replied with
              {extra.code}:{extra.errno}:
              {extra.message}"""
            tracing.log(current_module, 'error', message)


# Call push() when file is called
if __name__ == '__main__':
  push()
