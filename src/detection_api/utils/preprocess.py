import re

def split_request_text(raw_request: str):
    """
    If detection side receives a single raw_request string, try to split:
    Example raw_request: "GET /search?q=1 OR 1=1"
    Returns (method, path, query, body)
    """
    if raw_request is None:
        return ("", "", "", "")
    s = str(raw_request).strip()
    # quick heuristics
    parts = s.split(" ", 2)
    method = parts[0] if len(parts) > 0 else ""
    rest = parts[1] if len(parts) > 1 else ""
    rest2 = parts[2] if len(parts) > 2 else ""
    # separate query from path
    path = rest
    query = ""
    if "?" in rest:
        path, query = rest.split("?", 1)
    body = rest2
    return (method, path, query, body)

def url_decode(s: str):
    try:
        return re.sub(r'%20', ' ', s)
    except Exception:
        return s
