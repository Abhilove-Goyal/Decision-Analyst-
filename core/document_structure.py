TOC_MAP = {}
def set_toc(ipo_id, toc):
    TOC_MAP[ipo_id] = toc


def get_toc(ipo_id):
    return TOC_MAP.get(ipo_id, {})
