#!/usr/bin/python3
import cgi, os, time, mistune
import cgitb
cgitb.enable()

# Every time a paste is created, metadata is saved to a file, which is
# used for the index. Formatted like title<author<unix_timestamp
paste_log = "./pastes.txt"

# Number of static files (all files in directory which are not pastes)
sf_num = 5

# Dates are rendered according to strftime
time_form = '%Y-%m-%d %H:%M'

form = cgi.FieldStorage()

# Your markdown renderer
markdown = mistune.markdown

def head():
    print("Content-type: text/html\r\n")
    print("<title>Pastebin</title>")
    print("<link rel='stylesheet' href='style.css'>")
    print("<h2>paste</h2>")
    if get_form('m'):
        print("<a href='.'>&lt;&lt; back</a>")
    print("<p>")

def get_form(thing):
    escaped = None
    if form.getvalue(thing):
        escaped = cgi.escape(form.getvalue(thing))
    return escaped

def get_log():
    with open(paste_log, "r") as paste_list:
        paste_list = paste_list.read().splitlines()
    for n, paste in enumerate(paste_list):
        paste_list[n] = paste.split("<")
    return paste_list

def fancy_time(utime='', mode=''):
# Return the current time as a Unix or strf-formatted string.
    if not utime:
        utime = int(time.time())
    else:
        utime = int(utime)
    if mode == 'unix':
        return str(utime)
    htime = time.localtime(utime)
    htime = time.strftime(time_form, htime)
    if mode == "human":
        return htime
    else:
        return [utime, htime]

def main():
    head()
    modes = {'view':'view_paste()',
             'list':'list_paste()',
             'new':'new_paste()'}

    if get_form('m') in modes:
        eval(modes[get_form('m')])
    else:
        list_paste()

def view_paste():
# Try to load a plaintext file and format it using Markdown.
    p_info = []
    paste = get_form('p')
    try:
        test = int(paste)
    except:
        paste = None
    pastes = os.listdir()
    if paste + '.txt' in pastes:
        with open(paste + '.txt', 'r') as the_paste:
            paste = the_paste.read().splitlines()
        paste[0] = paste[0].split(' ')
        paste[0] = [' '.join(paste[0][:-1]), \
                    fancy_time(paste[0][-1], 'human')]
        p_author = paste[0][0]
        p_time = paste[0][1]
        p_title = paste[1]
        p_content = '\n'.join(paste[2:])
        p_marked = markdown(p_content)
        p_info = [p_title, p_author, p_time, p_marked, p_content]
        with open('view.html', 'r') as view_paste:
            view_paste = view_paste.read()
        paste = view_paste.format(*p_info)
    else:
        paste = None
    print("<p>", paste)

def list_paste():
# Try to generate and print an index of pastes, based on an index file.
    print("list // <a href='?m=new'>new+</a><p>")
    print("<table><tr><th>")
    print("<th>Paste name:")
    print("<th>Paste author:")
    print("<th>Paste time:")
    paste_list = get_log()
    for n, i in enumerate(paste_list):
        n += 1
        n = str(n).zfill(3)
        print("<tr><td>", n)
        i[0] = "<a href='.?m=view;p={0}'>{1}</a>".format(n, i[0])
        i[2] = fancy_time(i[2], 'human')
        print("<td>{0}<td>{1}<td>{2}".format(*i))
    print("</table>")

def new_paste():
# Create a new paste file from 'title', 'author', and 'paste' CGI form
    if None in [get_form('title'), get_form('paste')]:
        with open('new.html', 'r') as np:
            np = np.read()
        print(np)
    else:
        if not get_form('author'):
            p_author = "Anonymous"
        else:
            p_author = get_form('author')[:12]
        p_num = str(len(os.listdir()) - sf_num + 1).zfill(3)
        p_time = fancy_time('', 'unix')
        p_data = []
        p_data.append(p_author + " " + p_time)
        p_data.append(get_form('title')[:20])
        p_data.append(get_form('paste').replace('\r', ''))
        p_data = '\n'.join(p_data)
        with open(p_num + '.txt', 'x') as new_paste:
            new_paste.writelines(p_data)
        with open("pastes.txt", 'a') as paste_log:
            paste_log.write("<".join([get_form('title')[:20],
                                      p_author, p_time]) + "\n")
        print("Your paste has been published,", p_author + "!")
        
main()
