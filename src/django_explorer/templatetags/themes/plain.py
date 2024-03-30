from django.utils.safestring import mark_safe
from django_explorer.templatetags.django_explorer import register
from django_explorer.types import ExplorerFile
from django.templatetags.static import static

@register.simple_tag
def plain_file_name(file: ExplorerFile) -> str:
    icon_url = static("media/folder.svg") if file.type == "directory" else static("media/file.svg")
    html_icon = f'<img src="{icon_url}" alt="icon"/>'

    return mark_safe(f"{html_icon} {file.path.name}")
