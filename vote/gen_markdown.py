import markdown
from os.path import split, dirname, join, splitext

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


path1 = 'vote/templates/vote/about.md'
convert_to_html(path1)