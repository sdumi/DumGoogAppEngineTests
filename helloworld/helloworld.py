import jinja2
import os

import cgi
import datetime
import urllib
import webapp2

from google.appengine.ext import db
from google.appengine.api import users

# using the templates
jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class Greeting(db.Model):
    """Models an individual Guestbook entry with an author, content and date."""
    author = db.UserProperty()
    content = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)

def guestbook_key(guestbook_name=None):
    """Contstruct a Datastore key for a Guestbook entity with guestbook_name."""
    return db.Key.from_path('Guestbook', guestbook_name or 'default_guestbook')

class MainPage(webapp2.RequestHandler):
    def get(self):
        guestbook_name = self.request.get('guestbook_name')
        greetings_query = Greeting.all().ancestor(
            guestbook_key(guestbook_name)).order('-date')
        greetings = greetings_query.fetch(10)

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        template_values = {
            'greetings':greetings,
            'url': url,
            'url_linktext':url_linktext,
            }
        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))


class Guestbook(webapp2.RequestHandler):
    def post(self):
        guestbook_name = self.request.get('guestbook_name')
        greeting = Greeting(parent=guestbook_key(guestbook_name))
        if users.get_current_user():
            greeting.author = users.get_current_user()
        greeting.content = self.request.get('content')
        greeting.put()
        self.redirect('/?'+urllib.urlencode({'guestbook_name':guestbook_name}))

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/sign', Guestbook)],
                               debug=True)
