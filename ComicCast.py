#!/usr/bin/env python2
# Copyright (c) 2014 Chaserhkj
# This software is licensed under the MIT license.
# See LICENSE for more details.

import tornado.web as web
import tornado.template as template
import tornado.ioloop as ioloop
import os,sys,mimetypes
import rarfile,zipfile

supported_archive = [".zip", ".rar"]

supported_image = [".jpe", ".jpg", ".jpeg", ".gif", ".png"]

work_dir = os.getcwd()

list_template = template.Template(
"""<html>
    <head>
        <title>PyComicCast</title>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    </head>
    <body>
        <ul>
        {% for i in names %} 
            <li> <a href="/{{ i[0] }}/0">{{ escape(i[1]) }}</a> </li> 
        {% end %} 
        </ul>
    </body>
</html>"""
)

image_template = template.Template(
"""<html>
    <head>
        <title>PyComicCast</title>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <style type="text/css">
            img.content {max-width:100%;}
            div.content {text-align:center;}
            div.navi {text-align:center;}
        </style>
    </head>
    <body>
    <div class="content">
        <a href="/{{archive}}/{{image + 1}}"><img class="content" src="/{{archive}}/{{image}}/image"/></a>
    </div>
    <br />
    <br />
    <div class="navi">
        <a href="/{{archive}}/{{image - 1}}">Previous</a> 
        <a href="/">Return</a> 
        <a href="/{{archive}}/{{image + 1}}">Next</a>
    </div>
    </body>
</html>"""
)

file_objs = {}

def get_file_list():
    return [i for i in os.listdir(work_dir) if os.path.splitext(i)[1].lower() in supported_archive] 

def get_file_obj(index):
    name = get_file_list()[index]
    if not name in file_objs:
        if name.endswith(".rar"):
            obj = rarfile.RarFile(os.path.join(work_dir, name))
        elif name.endswith(".zip"):
            obj = zipfile.ZipFile(os.path.join(work_dir, name))
        else:
            raise Exception, "Not supported archive file!"
        img_list = [i for i in obj.namelist() if os.path.splitext(i)[1].lower() in supported_image]
        img_list.sort()
        file_objs[name] = (obj, img_list)
    return file_objs[name]



class RootHandler(web.RequestHandler):
    def get(self):
        self.write(list_template.generate(names=enumerate(get_file_list())))

class ImagePageHandler(web.RequestHandler):
    def get(self, archive, image):
        image = int(image)
        archive = int(archive)
        max_index = len(get_file_obj(archive)[1])
        if image < 0 or image >= max_index:
            self.redirect("/")
            return
        self.write(image_template.generate(archive=archive,image=image))

class ImageHandler(web.RequestHandler):
    def get(self, archive, image):
        image = int(image)
        archive = int(archive)
        obj = get_file_obj(archive)
        mimetype  = mimetypes.guess_type(obj[1][image])
        img = obj[0].open(obj[1][image])

        self.set_header("Content-Type", mimetype[0])
        while True:
            data = img.read(2048)
            if not data:
                break
            self.write(data)


application = web.Application([
    (r"/", RootHandler),
    (r"/(\d+)/(-?\d+)", ImagePageHandler),
    (r"/(\d+)/(-?\d+)/image", ImageHandler)
    ])

if __name__=="__main__":
    if len(sys.argv) >= 2:
        work_dir = sys.argv[1]
    application.listen(8888)
    try:
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print "Exiting..."
