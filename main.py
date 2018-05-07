import webapp2
import os
import jinja2

from google.appengine.ext import db

#initialize jinja 2
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                        autoescape = True)
#extended RequestHandler class, functions borrowed from Udacity's CS253
class Handler(webapp2.RequestHandler):
    #writes any arguments passed into it, useful for in-function calls
    def write(self,*a,**kw):
        self.response.out.write(*a, **kw)
    #renders template str specified, passing into that any kw params called
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    #calls write with the templated html returned from render_str
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))
    # used to pass additional arguments into .render; can set to query or
    # simply pass in needed defaults or additional arguments
    def render_front(self, template="", title="", body="", error="",
                    query=False, **kw):

        if query:
            posts = db.GqlQuery('SELECT * from Post '
                                'ORDER BY created DESC '
                                'LIMIT 5')
            self.render(template, posts=posts)
        else:
            self.render(template, title=title, body=body, error=error, **kw)

# creates a class of Post objects used to save posts in datastore
class Post(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

# redirects '/' and '/blog/' to '/blog'
class OopsHandler(Handler):
    def get(self):
        self.redirect('/blog')

# renders "blog.html" by passing to render_front, sets query flag
class BlogHandler(Handler):

    def get(self):
        self.render_front("blog.html", query=True)

class ViewPostHandler(Handler):
    # displays a single post, or redirects to '/blog' if bad input
    def get(self, id):
        post = Post.get_by_id(int(id))
        if post:
            posts = [post]
            self.render("blog.html", posts= posts)
        else:
            self.redirect('/blog')


class PostHandler(Handler):
    #on initial get, renders template
    def get(self):
        self.render_front("newpost.html")

    #checks for incomplete form, errors if so, or redirects to permalink
    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            p = Post(title=title, body=body)
            p.put()
            #redirects to permalink using id key of p as the address
            self.redirect('/blog/' + str(p.key().id()))

        else:
            error = "we need both a title and a body!"
            self.render_front("newpost.html",title=title, body=body, error = error)



app = webapp2.WSGIApplication([
    ('/', OopsHandler),
    ('/blog', BlogHandler),
    #tests a route against a named regex that checks for digits
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
    ('/blog/', OopsHandler),
    ('/blog/newpost', PostHandler)

], debug=True)
