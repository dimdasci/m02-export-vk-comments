import vk_api
import json
import click
import datetime
from pytz import timezone
import pandas
import re


@click.command()
@click.argument("club_id", type=click.INT)
@click.option("-d", "--depth", default=1, type=int)
@click.option("-f", "--filter", default="", type=str)
def get_comments(club_id: int, depth: int, filter: str) -> None:
    print(club_id, depth, filter)


if __name__ == "__main__":
    get_comments()
