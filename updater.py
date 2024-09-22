import requests
from bs4 import BeautifulSoup

def extract_info(user: str, project: str = "AutoPresser"):
    request = requests.get(f"https://github.com/{user}/{project}/releases")
    soup = BeautifulSoup(request.text, 'html.parser')

    return (soup.find("a", {"class": "Link--primary Link"}).getText(), f"https://github.com/{user}/{project}/releases")

def check_version(curr_app_version):
    info = extract_info("FDroider")
    app_version = info[0].split(" ")
    for i in app_version:
        if i != "version":
            app_version.pop(0)
            continue
        app_version.pop(0)
        break

    curr_app_version = curr_app_version.split(" ")
    curr_app_version_num = curr_app_version[0].split(".")

    app_version_num = app_version[0].split(".")


    if len(curr_app_version) > len(app_version) and curr_app_version_num == app_version_num:
        return (app_version, info[1])
    elif len(curr_app_version) < len(app_version) and curr_app_version_num == app_version_num:
        return None
    else:
        for n in range(len(curr_app_version_num)):
            if int(curr_app_version_num[n]) < int(app_version_num[n]):
                return (app_version, info[1])
            elif int(curr_app_version_num[n]) > int(app_version_num[n]):
                return None
    return None

if __name__ == "__main__":
    from main import __version__
    print(check_version(__version__))
