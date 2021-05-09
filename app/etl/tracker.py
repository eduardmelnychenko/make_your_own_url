import logging
import requests
import ast
from flask import request


def get_user_agent() -> tuple:
    user_agent_fields = [None, ] * 4
    user_agent = request.user_agent

    if user_agent:
        user_agent_fields = [user_agent.platform, user_agent.browser, user_agent.version, user_agent.language]

    for idx in range(len(user_agent_fields)):
        if user_agent_fields[idx] is None:
            user_agent_fields[idx] = "not defined"

    return tuple(user_agent_fields)


def get_ip_details(ip_address: str) -> tuple:
    ip_fields = ("ip",
                 "country_code",
                 "country_name",
                 "region_code",
                 "region_name",
                 "city",
                 "zip_code",
                 "time_zone",
                 "latitude",
                 "longitude")

    url = f"https://freegeoip.app/json/{ip_address}"

    headers = {
        'accept': "application/json",
        'content-type': "application/json"
    }

    response = requests.request("GET", url, headers=headers)

    decoded_response = ast.literal_eval(response.text)

    ip_values = []

    if type(decoded_response) == 'dict':
        for field_name in ip_fields:
            field_value = decoded_response.get(field_name, "not_defined")
            ip_values.append(field_value)
    else:
        ip_values = ["not_defined", ] * len(ip_fields)

    return tuple(ip_values)


def get_user_info() -> tuple:

    user_agent_tuple = get_user_agent()

    ip_address = request.remote_addr

    ip_details_tuple = get_ip_details(ip_address)

    logging.info(user_agent_tuple)
    logging.info(ip_details_tuple)

    res_tuple = (ip_address, ) + user_agent_tuple + ip_details_tuple

    logging.info(res_tuple)

    return res_tuple


