#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import re
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                        autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model): #defining blog object
    subject = db.StringProperty(required = True) # requires a title and content to make instance of Post class
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True) # auto sets created to date/time


    def render(self):
        self._render_text = self.content.replace('/n', '<br>')
        return render_str("newpost.html", posts=posts)

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        blog_id = int(id)
        blog_post = Blog.get_by_id(blog_id)

        if blog_post:

            self.response.write(blog_post.subject)
            self.response.write(blog_post.content)
            self.response.write(blog_post.created)
            #self.redirect(webapp2.Route('/blog/<id:\d+>')
        else:
            self.response.write("Please request an existing blog post")

class BlogFront(Handler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM Blog ORDER BY created desc LIMIT 5")
        self.render('front.html', posts=posts)

class NewPost(Handler):
    def get(self):
        self.render("newpost.html")

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            b = Blog(subject=subject, content=content)
            b.put()
            Blog_redir = b.key().id()
            self.redirect('/blog/' + str(Blog_redir))
            #/blog/{{ p.key().id()
            #probably some jazz here about redirecting to the permalink page
        else:
            error = "You must provide subject and content!"
            self.render("newpost.html", subject=subject, content=content, error=error)

class PostPage(Handler):
    def get(self):
        self.render("newpost.html")


    # def post(self):
    #     title = self.request.get("title")
    #     art = self.request.get("art")
    #
    #     if title and art:
    #         a = Art(title = title, art = art) #created done automatically
    #         a.put() #saves the instance in the db
    #
    #         self.redirect("/")
    #     else:
    #         error = "we need both a title and some artwork!"
            # self.render_front(title, art, error)
class BlogRedirect(Handler):
    def get(self):
        self.redirect("/blog")

app = webapp2.WSGIApplication([
    ('/', BlogRedirect),
    ('/blog', BlogFront),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
    ('/blog/newpost', NewPost),
    ('/blog/postpage', PostPage)
],
 debug=True)
