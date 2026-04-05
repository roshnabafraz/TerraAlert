import re


def parse_location_input(location_input):
    if not location_input:
        return {"text": None, "coords": None}

    location_input = location_input.strip()
    coord_match = re.match(r"^(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)$", location_input)
    if coord_match:
        return {
            "text": location_input,
            "coords": (float(coord_match.group(1)), float(coord_match.group(2))),
        }

    return {"text": location_input, "coords": None}
