from dotenv import load_dotenv

load_dotenv()

import os


def get_base_ml_service_url() -> str:
  return "http://" + os.getenv("ML_HOSTNAME") + ":" + os.getenv("ML_PORT")


def get_base_core_service_url() -> str:
  return "http://" + os.getenv("CORE_HOSTNAME") + ":" + os.getenv("CORE_PORT")


def get_client_domain_name() -> str:
  if os.getenv("ENVIRONMENT") == "production":
    return "https://" + os.getenv("DOMAIN_NAME")
  return "https://" + os.getenv("ENVIRONMENT") + "." + os.getenv("DOMAIN_NAME")


def get_www_client_domain_name() -> str:
  if os.getenv("ENVIRONMENT") == "production":
    return "https://www." + os.getenv("DOMAIN_NAME")
  return "https://" + os.getenv("ENVIRONMENT") + "." + os.getenv("DOMAIN_NAME")
