from turtle import pos
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


def export_posts(vk: vk_api.VkApi, club_id: int, depth: int, filter: str = "") -> tuple:
    """Exports posts of club_id for depth days from now.

    If a filter given exports only posts that contain filter

    Return list of posts and list of tuples post_id, comments_number as the queue
    """
    print(f"Exporting posts for {club_id} club {depth} day(s) from now.")

    posts, queue = [[5, "hello"], [6, "word"]], [(5, 2), (6, 3)]
    return posts, queue


def export_comments(vk: vk_api.VkApi, club_id: int, post_id: int, number: int) -> list:
    """Exports number of comments to post_id of club_id club

    Returns list of comments
    """
    print(f"Export {number} comments for {post_id} post")

    comments = []
    return comments


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

    posts, queue = export_posts(vk, club_id=club_id, depth=depth)

    comments = []
    for item in queue:
        comments = comments + export_comments(
            vk, club_id=club_id, post_id=item[0], number=item[1]
        )

    print(club_id, depth, filter)
    print(f"id {VK_ID}, passw {VK_PASSWORD}, timezone {TIMEZONE}, {vk}")


if __name__ == "__main__":
    get_comments()
