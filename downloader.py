import os
import re
import argparse
import tweepy
import configparser
import requests
import shutil
from typing import Tuple
from colorama import init, Fore, Style

init(autoreset=True)

class RequestError(Exception): pass
class ParserError(Exception): pass

class TID(object):
    def __init__(self, user: str, items: int = 200) -> None:
        self.user = user
        self.items = items
        self.images = []
        self.api = None

    def _init_oauth(self) -> None:
        try:
            credentials = configparser.ConfigParser()
            credentials.read(os.path.dirname(os.path.realpath(__file__)) + "\credentials.ini")
            credentials = credentials["CREDENTIALS"]
        except (Exception, KeyError):
            raise ParserError(f"{Fore.RED}{Style.BRIGHT}[TID] An error occurred while trying to parse the .ini config file.")
        else:
            auth = tweepy.OAuthHandler(credentials["PublicConsumerKey"], credentials["SecretConsumerKey"])
            auth.set_access_token(credentials["PublicAccessToken"], credentials["SecretAccessToken"])
            self.api = tweepy.API(auth)

    def _get_media(self) -> None:
        try:
            request = tweepy.Cursor(
                self.api.user_timeline,
                id=self.user,
                tweet_mode="extended",
                include_entities=True,
                count=200
            ).items(self.items)

            for tweet in request:
                if "media" in tweet.entities:
                    for image in tweet.extended_entities["media"]:
                        self.images.append((image["expanded_url"], image["media_url_https"]))
        except tweepy.TweepError as e:
            raise RequestError(f"{Fore.RED}{Style.BRIGHT}[TID] An error occurred while trying to request to the Twitter API: '{e}'")
        finally:
            del request
    
    def _sanitize_filename(self, urls: Tuple[str, str]) -> Tuple[str, str]:
        username = re.search(r"(?:https?:\/\/)?twitter\.com\/([^\/]+)", urls[0])
        filename = re.search(r"(?:https?:\/\/)?pbs\.twimg\.com\/media\/([^\/]+)", urls[1])
        return (username[1], filename[1])

    def _download_media(self) -> None:
        if not os.path.isdir(os.path.dirname(os.path.realpath(__file__)) + "\downloads"):
            os.mkdir("downloads")

        i = 1
        for image in self.images:
            sanitizer = self._sanitize_filename(image)
            percentage = "{:.2f}".format(i / len(self.images) * 100)
            request = requests.get(image[1], stream=True)

            if os.path.isfile(f"downloads\{sanitizer[0]}_{sanitizer[1]}"):
                print(f"{Fore.YELLOW}{Style.BRIGHT}[TID]{Style.RESET_ALL} {percentage}% Skipping {Fore.GREEN}{sanitizer[1]}{Style.RESET_ALL} File already exists")
                i += 1
                continue
            else:
                if request.status_code == 200:
                    with open(f"downloads\{sanitizer[0]}_{sanitizer[1]}", "wb") as output:
                        request.raw.decode_content = True
                        shutil.copyfileobj(request.raw, output)
                        print(f"{Fore.BLUE}{Style.BRIGHT}[TID]{Style.RESET_ALL} {percentage}% Downloading {Fore.GREEN}{sanitizer[1]}{Style.RESET_ALL} from {Fore.GREEN}@{sanitizer[0]}{Style.RESET_ALL}")
                        i += 1
                else:
                    raise RequestError(f"{Fore.RED}{Style.BRIGHT}[TID] An error occurred while trying to download a picture. Error status code: '{request.status_code}'")
        del request

    def download(self) -> None:
        self._init_oauth()
        self._get_media()
        self._download_media()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", type=str, required=True, default=None, help="User username (@username)")
    parser.add_argument("-i", "--items", type=int, required=False, default=200, help="Number of items (Tweets) to scrape in total (max. 3200).")
    args = parser.parse_args()

    tid = TID(args.user, args.items)
    tid.download()
