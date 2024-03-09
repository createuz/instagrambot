import re


async def replace_text_to_links(text):
    def create_html_link(match):
        text_name, url = match.groups()
        return f'<a href="{url}">{text_name}</a>'

    pattern = r'\((.*?)\)\[(.*?)\]'
    return re.sub(pattern, create_html_link, text)


def format_time(elapsed_time):
    hours, rem = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{int(hours):02d} : {int(minutes):02d} : {int(seconds):02d}"
