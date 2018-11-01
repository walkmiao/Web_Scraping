#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : utils.py
# @Author: lch
# @Date  : 2018/11/1
# @Desc  :
import os, sys, urllib

def usage():
    print("""Usage: python tharia2.py [OPTIONS] URL
    OPTIONS: As same as options of aria2c""")


def get_url_list(url, listpath):
    if not os.path.exists(listpath):
        print ("Getting URL list, please wait...")
        f = urllib.request.urlopen("http://cocobear.info/demo/pythunder/?url=%s" % url)
        lst = open(listpath, "w+")
        lst.writelines(f.readlines())
        f.close
        lst.seek(0)
    else:
        print ("Found existing url list: ", listpath)
        lst = open(listpath)

    url_list = [line[:-1] for line in lst]
    lst.close()
    print ("Recieved %d url(s)." % len(url_list))
    return " ".join(url_list)


def download(url):
    for prefix in (r"http://", r"https://", r"ftp://"):
        if url.startswith(prefix):
            break
    else:
        print("Invalid URL: %s" % url)
        exit()

    listdir = os.path.expanduser("~/.tharia2/list/")
    listfile = os.path.split(url)[-1] + ".list"
    if not os.path.exists(listdir):
        os.makedirs(listdir)
    listpath = os.path.join(listdir, listfile)

    url_list = get_url_list(url, listpath)
    cmd = " ".join(("aria2c -c", " ".join(sys.argv[1:-1]), url_list))
    print ("Executing command: %s" % cmd)
    if not os.system(cmd):
        os.remove(listpath)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        download(sys.argv[-1])
    else:
        usage()