import requests
import os

url_api = "https://cavening.de/api/"
url_web_users = "https://cavening.de/users/"
url_web_kvm = "https://cavening.de/webinterface/kvm/"
url_web_domain = "https://cavening.de/webinterface/domain/"
url_web_custom = "https://cavening.de/webinterface/custom-service/"


async def defaultConnect(url: str, method: str = "GET", payload=None):
    if payload is None:
        payload = {}
    headers = {
        "X-API-Key": os.getenv("CAVE_TOKEN")
    }

    return requests.request(
        method,
        url_api + url,
        headers=headers,
        data=payload
    )


async def accountRequest(donate: bool = False):
    if donate:
        response = await defaultConnect("accounting/donate")
    else:
        response = await defaultConnect("accounting")

    return response.json()


async def kvmRequest(kvm_id: str):
    response = await defaultConnect("kvm/" + kvm_id + "/status")

    return response.json()


async def domainRequest(domain: str):
    response = await defaultConnect("domain/" + domain)

    return response.json()
