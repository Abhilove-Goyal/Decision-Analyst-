current_ipo_id: str | None = None


def set_current_ipo(ipo_id: str):
    global current_ipo_id
    current_ipo_id = ipo_id


def get_current_ipo():
    return current_ipo_id


def reset_current_ipo():
    global current_ipo_id
    current_ipo_id = None