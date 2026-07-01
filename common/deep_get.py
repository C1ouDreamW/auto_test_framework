
def deep_get(d: dict, path: str):
    now = d
    for i in path.split('.'):
        if now is None:
            return None
        if isinstance(now, dict):
            now = now.get(i)
        else:
            raise KeyError(f"路径 {path} 在 {i} 处不是dict")
    return now