# preenchimento_app/selectors.py
def best_selector(payload: dict) -> str:
    attrs = payload.get("attrs") or {}

    for key in ["data-testid", "data-test", "data-qa"]:
        val = attrs.get(key)
        if val:
            return f'[{key}="{str(val).replace(chr(34), r"\"")}"]'

    el_id = attrs.get("id")
    if el_id:
        safe = str(el_id).replace('"', r'\"')
        return f'#{safe}'

    name = attrs.get("name")
    if name:
        safe = str(name).replace('"', r'\"')
        return f'[name="{safe}"]'

    placeholder = attrs.get("placeholder")
    if placeholder:
        safe = str(placeholder).replace('"', r'\"')
        return f'[placeholder="{safe}"]'

    css_path = payload.get("cssPath")
    if css_path:
        return css_path

    return (payload.get("tag") or "input").lower()
