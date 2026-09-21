# -*- coding: utf-8 -*-
"""Generate XMLTV EPG data and publish it using the existing settings.py."""

import logging
import os
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from ftplib import FTP

import requests
import schedule
import xmltv

try:
    import epg_info
    from settings import *  # noqa: F403 - settings.py intentionally provides script configuration.
except Exception as exc:
    print(exc)
    logging.basicConfig(level=logging.ERROR)
    logging.exception("365 EPG Generator could not load its dependencies or settings")
    sys.exit(1)


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, file_name)  # noqa: F405
CUSTOM_NAMES_FILE = os.path.join(BASE_DIR, "custom_names.txt")
GITHUB_REPOSITORY = "/Users/marekdana/EPG/ep"
# A normal TV schedule changes from day to day.  Keep the previously published
# EPG unless a source loses more than 20 % of its programmes.
MINIMUM_PUBLISHED_SOURCE_RATIO = 0.80

logging.basicConfig(
    filename=os.path.join(BASE_DIR, "log.log"),
    filemode="w",
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO,
)
LOGGER = logging.getLogger(__name__)

local_now = datetime.now().astimezone()
TIMEZONE_SUFFIX = " " + str(local_now)[-6:].replace(":", "")
SMS_USER_AGENT = (
    "SMSTVP/1.7.3 (242;cs_CZ) ID/ef284441-c1cd-4f9e-8e30-f5d8b1ac170c "
    "HW/Redmi Note 7 Android/10 (QKQ1.190910.002)"
)


def encode(value):
    """Keep the original XMLTV identifier behaviour."""
    return value


def load_custom_names():
    try:
        with open(CUSTOM_NAMES_FILE, encoding="utf-8") as custom_names_file:
            return [
                tuple(line.split("=", 1))
                for line in custom_names_file.read().splitlines()
                if "=" in line
            ]
    except OSError:
        return []


CUSTOM_NAMES = load_custom_names()


def replace_names(value):
    for original, replacement in CUSTOM_NAMES:
        if original == value:
            return replacement
    return value


def get_tm_programmes(tm_ids, d, d_b, lng):
    # The source offers a maximum of ten days. Retain the original limit.
    if d > 10:
        d = 10

    prefix = "tm-" if lng == "cz" else "mag-"
    requested_ids = tm_ids.split(",")
    programmes = []

    params = {
        "dsid": "c75536831e9bdc93",
        "deviceName": "Xiaomi Mi 11",
        "deviceType": "OTT_STB",
        "osVersion": "13",
        "appVersion": "3.7.0",
        "language": lng.upper(),
    }
    headers = {
        "Host": lng + "go.magio.tv",
        "authorization": "Bearer",
        "User-Agent": "okhttp/3.12.12",
        "content-type": "application/json",
        "Connection": "Keep-Alive",
    }
    response = requests.post(
        "https://" + lng + "go.magio.tv/v2/auth/init",
        params=params,
        headers=headers,
        verify=True,
    ).json()
    token = response["token"]["accessToken"]
    api_headers = {
        "Host": lng + "go.magio.tv",
        "authorization": "Bearer " + token,
        "User-Agent": "okhttp/5.3.2",
        "content-type": "application/json",
    }
    api_channels = requests.get(
        "https://" + lng + "go.magio.tv/v2/television/channels?list=LIVE&queryScope=LIVE",
        headers=api_headers,
    ).json()["items"]

    channels = []
    channel_ids = []
    channel_map = {}
    for item in api_channels:
        channel_id = str(item["channel"]["channelId"])
        if requested_ids != [""] and channel_id not in requested_ids:
            continue
        channel_ids.append(channel_id)
        name = item["channel"]["name"]
        channel_xml_id = prefix + channel_id + "-" + encode(name).replace(" HD", "").lower().replace(" ", "-")
        channel_map[name] = channel_xml_id
        display_name = replace_names(name.replace(" HD", "")) if requested_ids == [""] else name.replace(" HD", "")
        channels.append({
            "display-name": [(display_name, "cs")],
            "id": channel_xml_id,
            "icon": [{"src": str(item["channel"]["logoUrl"])}],
        })

    now = datetime.now()
    for offset in range(d_b * -1, d):
        next_day = now + timedelta(days=offset)
        previous_day = next_day - timedelta(days=1)
        date_to = next_day.strftime("%Y-%m-%d")
        date_from = previous_day.strftime("%Y-%m-%d")
        printable_date = next_day.strftime("%d.%m.%Y")
        print(f"Stahuji program pro den: {printable_date}")

        for channel_id in channel_ids:
            try:
                url = (
                    "https://" + lng + "go.magio.tv/v2/television/epg?filter=channel.id=in=("
                    + channel_id + ");endTime=ge=" + date_from
                    + "T23:00:00.000Z;startTime=le=" + date_to
                    + "T23:59:59.999Z&limit=150&offset=0&lang=" + lng.upper()
                )
                items = requests.get(url, headers=api_headers).json().get("items", [])
                time.sleep(0.05)
                for item in items:
                    for programme_data in item["programs"]:
                        programme = build_tm_programme(programme_data, channel_map)
                        if programme is not None and programme not in programmes:
                            programmes.append(programme)
            except Exception:
                LOGGER.exception("Unable to retrieve %s programme data for channel %s", lng, channel_id)
        print(printable_date + "  OK")

    print()
    return channels, programmes


def build_tm_programme(data, channel_map):
    """Map one T-Mobile/Magio response item to the original XMLTV structure."""
    try:
        program = data["program"]
        value = program["programValue"]
        title = program["title"]
        episode_id = value["episodeId"]
        if episode_id is not None:
            title += " (" + episode_id + ")"
        result = {
            "channel": channel_map[data["channel"]["name"]],
            "start": data["startTime"].replace("-", "").replace("T", "").replace(":", "") + TIMEZONE_SUFFIX,
            "stop": data["endTime"].replace("-", "").replace("T", "").replace(":", "") + TIMEZONE_SUFFIX,
            "title": [(title, "")],
            "desc": [(program["description"], "")],
        }
        if value["creationYear"] is not None:
            result["date"] = value["creationYear"]
        try:
            subgenre = program["programCategory"]["subCategories"][0]["desc"]
        except (KeyError, IndexError, TypeError):
            subgenre = ""
        try:
            result["category"] = [(program["programCategory"]["desc"], ""), (subgenre, "")]
        except (KeyError, TypeError):
            pass
        try:
            result["icon"] = [{"src": program["images"][0]}]
        except (KeyError, IndexError, TypeError):
            pass
        try:
            directors = [person["fullName"] for person in program["programRole"]["directors"]]
        except (KeyError, TypeError):
            directors = []
        try:
            actors = [person["fullName"] for person in program["programRole"]["actors"]]
        except (KeyError, TypeError):
            actors = []
        if directors or actors:
            credits = {}
            if directors:
                credits["director"] = directors
            if actors:
                credits["actor"] = actors
            result["credits"] = credits
        return result
    except Exception:
        LOGGER.exception("Unable to process T-Mobile/Magio programme")
        return None


class Get_channels_sms:
    def __init__(self):
        self.channels = []
        self.ch = {}
        self.html = requests.get(
            "http://programandroid.365dni.cz/android/v6-tv.php?locale=cs_CZ",
            headers={"user-agent": SMS_USER_AGENT},
        ).text

    def all_channels(self):
        return self._collect_channels()

    def cz_sk_channels(self):
        return self._collect_channels(czech_and_slovak_only=True)

    def own_channels(self, requested_channels):
        return self._collect_channels(requested_ids=requested_channels.split(","))

    def _collect_channels(self, requested_ids=None, czech_and_slovak_only=False):
        try:
            root = ET.fromstring(self.html)
            for item in root.iter("a"):
                if requested_ids is not None and item.attrib["id"] not in requested_ids:
                    continue
                if czech_and_slovak_only and item.find("p").text not in ("České", "Slovenské"):
                    continue
                self._add_channel(item)
        except Exception:
            LOGGER.exception("Unable to process TV.SMS.cz channels")
        return self.ch, self.channels

    def _add_channel(self, item):
        name = item.find("n").text
        channel_id = encode((item.attrib["id"] + "-" + name).replace(" ", "-").lower())
        self.ch[item.attrib["id"]] = channel_id
        try:
            icon = "http://sms.cz/kategorie/televize/bmp/loga/velka/" + item.find("o").text
        except (AttributeError, TypeError):
            icon = ""
        self.channels.append({
            "display-name": [(replace_names(name), "cs")],
            "id": channel_id,
            "icon": [{"src": icon}],
        })


class Get_programmes_sms:
    def __init__(self, days_back, days):
        self.programmes_sms = []
        self.days_back = days_back
        self.days = days

    def data_programmes(self, channels):
        if channels:
            channel_list = ",".join(channels.keys())
            now = datetime.now()
            for offset in range(self.days_back * -1, self.days):
                next_day = now + timedelta(days=offset)
                date = next_day.strftime("%Y-%m-%d")
                printable_date = next_day.strftime("%d.%m.%Y")
                print(f"Stahuji program pro den: {printable_date}")
                print(printable_date)
                response = requests.get(
                    "http://programandroid.365dni.cz/android/v6-program.php?datum=" + date + "&id_tv=" + channel_list,
                    headers={"user-agent": SMS_USER_AGENT},
                )
                response.raise_for_status()
                root = ET.fromstring(response.text)
                root[:] = sorted(root, key=lambda child: (child.tag, child.get("o")))
                programmes_for_day = 0
                for item in root.iter("p"):
                    if item.attrib["id_tv"] not in channels:
                        continue
                    title = item.find("n").text
                    try:
                        description = item.find("k").text
                    except AttributeError:
                        description = ""
                    self.programmes_sms.append({
                        "channel": channels[item.attrib["id_tv"]].replace("804-ct-art", "805-ct-:d"),
                        "start": item.attrib["o"].replace("-", "").replace(":", "").replace(" ", "") + TIMEZONE_SUFFIX,
                        "stop": item.attrib["d"].replace("-", "").replace(":", "").replace(" ", "") + TIMEZONE_SUFFIX,
                        "title": [(title, "")],
                        "desc": [(description, "")],
                    })
                    programmes_for_day += 1
                if programmes_for_day == 0:
                    raise RuntimeError(
                        "TV.SMS.cz returned no programmes for " + printable_date
                    )
                print(printable_date + "  OK")
                time.sleep(0.5)
        print()
        return self.programmes_sms


def run_git(command, *, capture_output=True, check=True):
    return subprocess.run(
        ["git", "-C", GITHUB_REPOSITORY, *command],
        check=check,
        capture_output=capture_output,
        text=capture_output,
    )


def programme_counts_by_source(programmes):
    """Return programme counts for the three source-specific XMLTV ID formats."""
    counts = {"sms": 0, "tm": 0, "mag": 0}
    for programme in programmes:
        channel_id = programme["channel"]
        if channel_id.startswith("tm-"):
            counts["tm"] += 1
        elif channel_id.startswith("mag-"):
            counts["mag"] += 1
        else:
            counts["sms"] += 1
    return counts


def published_programme_counts():
    """Read counts from the currently published file after git pull has completed."""
    published_file = os.path.join(GITHUB_REPOSITORY, "epg.xml")
    if not os.path.isfile(published_file):
        return {"sms": 0, "tm": 0, "mag": 0}

    counts = {"sms": 0, "tm": 0, "mag": 0}
    for _, element in ET.iterparse(published_file, events=("end",)):
        if element.tag != "programme":
            continue
        channel_id = element.attrib.get("channel", "")
        if channel_id.startswith("tm-"):
            counts["tm"] += 1
        elif channel_id.startswith("mag-"):
            counts["mag"] += 1
        else:
            counts["sms"] += 1
        element.clear()
    return counts


def validate_before_publish(programmes):
    """Refuse to overwrite a published EPG when an enabled source is substantially incomplete."""
    new_counts = programme_counts_by_source(programmes)
    enabled_sources = {
        "sms": TV_SMS_CZ == 1,  # noqa: F405
        "tm": T_MOBILE_TV_GO == 1,  # noqa: F405
        "mag": MAGIO_GO == 1,  # noqa: F405
    }
    for source, enabled in enabled_sources.items():
        if enabled and new_counts[source] == 0:
            raise RuntimeError(f"No programmes were generated for enabled source: {source}")

    old_counts = published_programme_counts()
    for source, enabled in enabled_sources.items():
        minimum_acceptable_count = old_counts[source] * MINIMUM_PUBLISHED_SOURCE_RATIO
        if enabled and new_counts[source] < minimum_acceptable_count:
            raise RuntimeError(
                f"Refusing to publish incomplete {source} EPG: "
                f"{new_counts[source]} programmes is below 80 % of the previously "
                f"published {old_counts[source]}."
            )


def upload_to_github(programmes):
    """Validate and publish the generated EPG to the repository's current branch."""
    try:
        if not os.path.isdir(os.path.join(GITHUB_REPOSITORY, ".git")):
            raise RuntimeError(
                "Git repository not found at: " + GITHUB_REPOSITORY
            )

        # Use the repository's actual branch instead of assuming it is always
        # named 'main'. This also makes the script work after a GitHub branch
        # rename or when the repository was originally created with 'master'.
        branch_result = run_git(["rev-parse", "--abbrev-ref", "HEAD"])
        branch = (branch_result.stdout or "").strip()
        if not branch or branch == "HEAD":
            raise RuntimeError("Could not determine the current Git branch.")

        remote_result = run_git(["remote", "get-url", "origin"])
        remote = (remote_result.stdout or "").strip()
        if not remote:
            raise RuntimeError("Git remote 'origin' is not configured.")

        print(f"Git: repository={GITHUB_REPOSITORY}")
        print(f"Git: branch={branch}")
        print(f"Git: remote={remote}")

        # Bring the local checkout up to date before replacing epg.xml.
        print("Git: pull...")
        run_git(["pull", "--rebase", "origin", branch])

        # The safety check compares the newly generated programme counts with
        # the EPG that is currently published in the repository.
        validate_before_publish(programmes)

        destination = os.path.join(GITHUB_REPOSITORY, "epg.xml")
        shutil.copy2(OUTPUT_FILE, destination)
        print("Git: epg.xml připraven k nahrání.")

        run_git(["add", "--all"])

        staged = run_git(["diff", "--cached", "--quiet"], capture_output=True, check=False)
        if staged.returncode == 0:
            print("Žádné změny v Git repozitáři - nic se nenahrává.")
            return True
        if staged.returncode != 1:
            raise subprocess.CalledProcessError(
                staged.returncode,
                staged.args,
                staged.stdout,
                staged.stderr,
            )

        print("Git: commit...")
        commit = run_git(["commit", "-m", "Automatic EPG update"])
        if commit.stdout:
            print(commit.stdout.strip())

        print("Git: push...")
        push = run_git(["push", "origin", branch])
        if push.stdout:
            print(push.stdout.strip())
        if push.stderr:
            print(push.stderr.strip())

        print("GitHub upload OK")
        return True

    except subprocess.CalledProcessError as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        print("GitHub upload chyba:")
        if stdout:
            print(stdout.strip())
        if stderr:
            print(stderr.strip())
        LOGGER.error(
            "GitHub upload failed: command=%s returncode=%s stdout=%s stderr=%s",
            exc.cmd,
            exc.returncode,
            stdout,
            stderr,
        )
        return False
    except OSError as exc:
        print("GitHub upload chyba:", exc)
        LOGGER.exception("GitHub upload could not start: %s", exc)
        return False
    except Exception as exc:
        print("GitHub upload zrušen:", exc)
        LOGGER.exception("GitHub upload was cancelled to protect the published EPG: %s", exc)
        return False


def upload_to_ftp():
    try:
        with FTP() as ftp:
            ftp.set_debuglevel(2)
            ftp.connect(ftp_server, ftp_port)  # noqa: F405
            ftp.login(ftp_login, ftp_password)  # noqa: F405
            ftp.cwd(ftp_folder)  # noqa: F405
            with open(OUTPUT_FILE, "rb") as epg_file:
                ftp.storbinary("STOR " + file_name, epg_file)  # noqa: F405
    except Exception as exc:
        print("Chyba\n")
        LOGGER.exception("FTP upload failed: %s", exc)


def main():
    channels = []
    programmes = []
    generation_complete = True
    print("365 EPG Generator(michalba) ver." + str(VERZE) + "\n")  # noqa: F405

    if TV_SMS_CZ == 1:  # noqa: F405
        try:
            print("TV.SMS.cz kanály\nStahuji data...")
            source = Get_channels_sms()
            channel_map, sms_channels = (
                source.all_channels() if TV_SMS_CZ_IDS == "" else source.own_channels(TV_SMS_CZ_IDS)  # noqa: F405
            )
            channels.extend(sms_channels)
            programmes.extend(Get_programmes_sms(days_back, days).data_programmes(channel_map))  # noqa: F405
        except Exception as exc:
            print("Chyba\n")
            LOGGER.exception("TV.SMS.cz channels failed: %s", exc)
            generation_complete = False

    for enabled, configured_ids, language, label in (
        (T_MOBILE_TV_GO, T_MOBILE_TV_GO_IDS, "cz", "T-Mobile TV Go"),  # noqa: F405
        (MAGIO_GO, MAGIO_GO_IDS, "sk", "Magio Go"),  # noqa: F405
    ):
        if enabled != 1:
            continue
        try:
            print(label + " kanály\nStahuji data...")
            source_channels, source_programmes = get_tm_programmes(configured_ids, days, days_back, language)  # noqa: F405
            channels.extend(source_channels)
            programmes.extend(source_programmes)
        except Exception as exc:
            print("Chyba\n")
            LOGGER.exception("%s channels failed: %s", label, exc)
            generation_complete = False

    if not channels:
        print("Žádné kanály\n")
        return

    print("Celkem kanálů: " + str(len(channels)))
    print("Generuji...")
    try:
        writer = xmltv.Writer(
            encoding="utf-8",
            source_info_url="http://www.funktronics.ca/python-xmltv",
            source_info_name="Funktronics",
            generator_info_name="python-xmltv",
            generator_info_url="http://www.funktronics.ca/python-xmltv",
        )
        for channel in channels:
            writer.addChannel(channel)
        for programme in programmes:
            writer.addProgramme(programme)
        writer.write(OUTPUT_FILE, pretty_print=True)

        if EPG_INFO_GEN == 1:  # noqa: F405
            epg_info.generuj_prehled(channels, BASE_DIR)
        if generation_complete:
            if ftp_upload == 1:  # noqa: F405
                upload_to_ftp()
            upload_to_github(programmes)
        else:
            print("EPG se nikam nenahrává: alespoň jeden zdroj nedokončil stahování.")
            LOGGER.error("EPG publication cancelled because a configured source did not finish.")

        if update == 1:  # noqa: F405
            print("\n\nHotovo (" + datetime.now().strftime("%d.%m.%Y %H:%M") + ")\n")
        else:
            print("Hotovo\n")
    except Exception as exc:
        print("Chyba\n")
        LOGGER.exception("xmltv.Writer failed: %s", exc)


if __name__ == "__main__":
    main()
    try:
        schedule.every(interval).hours.do(main)  # noqa: F405
        while update:  # noqa: F405
            schedule.run_pending()
            time.sleep(1)
    except Exception as exc:
        print(exc)
        LOGGER.exception("Scheduled EPG generation failed: %s", exc)
