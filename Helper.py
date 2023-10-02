import json
import logging

# Assuming the file nettimakes.json is in the same directory as your script
file_path = "nettimakes.json"

try:
    with open(file_path, "r") as file:
        netti_makes = json.load(file)
except FileNotFoundError:
    logging.error(f"File {file_path} not found.")
    netti_makes = []


def get_make_id(make_name):
    """
    Get the ID of a make by its name.

    Args:
        make_name (str): The name of the make.

    Returns:
        int or None: The ID of the make, or None if not found.
    """
    lower_make_name = make_name.lower()
    for make in netti_makes:
        if make["name"].lower() == lower_make_name:
            return make["id"]
    return None


def get_make_ids(make_names):
    """
    Get the IDs of multiple makes by their names.

    Args:
        make_names (list of str): List of make names.

    Returns:
        list of int: List of make IDs.
    """
    return [get_make_id(name) for name in make_names]


def generate_tori_url(makes):
    """
    Generate a Tori URL based on a list of makes.

    Args:
        makes (list of str): List of make names.

    Returns:
        str: The generated Tori URL.
    """
    base_url = 'https://autot.tori.fi/kuljetuskalusto-ja-raskas-kalusto/myydaan?alusta_2='

    make_url = f"{base_url}{','.join(makes).replace(' ', '-')}"

    return make_url
