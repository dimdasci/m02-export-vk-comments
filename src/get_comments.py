import vk_api
import json
import click
import datetime
from pytz import timezone
import pandas
import re
from dotenv import load_dotenv
import os


def init(id: str, password: str) -> vk_api.VkApi:
    """Initializes VK session"""
    vk_session = vk_api.VkApi(id, password)
    vk_session.auth()

    return vk_session.get_api()


@click.command()
@click.argument("club_id", type=click.INT)
@click.option(
    "-d", "--depth", default=1, type=int, help="number of days from now for post export"
)
@click.option(
    "-f",
    "--filter",
    default="",
    type=str,
    help="a string that a post must contain or empty string to not filter",
)
def get_comments(club_id: int, depth: int, filter: str) -> None:
    """Exports posts of a given by CLUB_ID VK club and its comments"""

    load_dotenv()
    VK_ID = os.getenv("VK_ID")
    VK_PASSWORD = os.getenv("VK_PASSWORD")
    TIMEZONE = timezone(os.getenv("TIMEZONE"))

    vk = init(VK_ID, VK_PASSWORD)
    print(club_id, depth, filter)
    print(f"id {VK_ID}, passw {VK_PASSWORD}, timezone {TIMEZONE}, {vk}")


if __name__ == "__main__":
    get_comments()
