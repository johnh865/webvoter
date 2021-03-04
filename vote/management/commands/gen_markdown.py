"""Build static html templates from markdown"""
import markdown
from os.path import split, dirname, join, splitext
from django.core.management.base import BaseCommand

def convert_to_html(path, new_ext='.md.html'):
    dirname, basename = split(path)
    name, _ = splitext(basename)
    with open(path, 'r') as f:
        string = f.read()
    new_path = join(dirname, name + new_ext)
    new_str = markdown.markdown(string)
    with open(new_path, 'w') as f:
        f.write(new_str)
    return



def build():
    path1 = 'vote/templates/vote/about.md'
    convert_to_html(path1)



class Command(BaseCommand):
    help = 'Create fake election data with bots'

    def handle(self, *args, **kwargs):
        build()
