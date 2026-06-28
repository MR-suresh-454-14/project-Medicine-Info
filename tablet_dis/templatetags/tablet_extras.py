from django import template

register = template.Library()


@register.simple_tag
def tablet_field(tablet, field_base, lang):
    if not tablet:
        return ""
    getter = getattr(tablet, "get_localized", None)
    if getter:
        return getter(field_base, lang)
    return getattr(tablet, f"{field_base}_{lang}", "") or ""
