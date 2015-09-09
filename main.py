import jinja2
import os
import urllib
import webapp2
from google.appengine.api import users
from google.appengine.ext import ndb

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

# Copied from Udacity lectures
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class StageOne(Handler):
    def get(self):
        self.render("stage_one.html")

class StageTwo(Handler):
    def get(self):
        self.render("stage_two.html")

class StageThree(Handler):
    def get(self):
        self.render("stage_three.html")

class StageFour(Handler):
    def get(self):
        self.render("stage_four.html")

DEFAULT_BULLETINBOARD_NAME = 'stage_four'

def bulletinboard_key(bulletinboard_name=DEFAULT_BULLETINBOARD_NAME):
    """Constructs a Datastore key for a Bulletinboard entity.

    We use bulletinboard_name as the key.
    """
    return ndb.Key('Bulletinboard', bulletinboard_name)

# Copied from Udacity's wallbook example. Eliminated name for simplicity.
class Author(ndb.Model):
    """Sub model for representing an author."""
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)

# Copied from Udacity's wallbook example
class Greeting(ndb.Model):
    """A main model for representing an individual Bulletinboard entry."""
    author = ndb.StructuredProperty(Author)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

# Largely borrowed from Google's example code
class MainPage(Handler):
    """Builds the main page including the bulletin board"""
    def get(self):
# Mark's error variable from the Udacity webcast
        error = self.request.get('error','')
        bulletinboard_name = self.request.get('bulletinboard_name',
                                          DEFAULT_BULLETINBOARD_NAME)

# Query Datastore for comments ordered by date ascending
# store the results in comments_query
        greetings_query = Greeting.query(
            ancestor=bulletinboard_key(bulletinboard_name)).order(-Greeting.date)

#Fetch comments from our query, store them in the variable comments
        greetings_to_fetch = 20
        greetings = greetings_query.fetch(greetings_to_fetch)

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

# Parameters to pass to the template
        template_values = {
            'user': user,
            'greetings': greetings,
            'bulletinboard_name': urllib.quote_plus(bulletinboard_name),
            'url': url,
            'url_linktext': url_linktext,
            'error': error,
        }

# Render our page
        template = jinja_env.get_template('IPND_notes.html')
        self.write(template.render(template_values))

#largely borrowed from Google's example code
class BulletinBoard(Handler):
    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each
        # Greeting is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        bulletinboard_name = self.request.get('bulletinboard_name',
                                          DEFAULT_BULLETINBOARD_NAME)
        greeting = Greeting(parent=bulletinboard_key(bulletinboard_name))

# If the user is logged in instantiate the Author class
        if users.get_current_user():
            greeting.author = Author(
                    identity=users.get_current_user().user_id(),
                    email=users.get_current_user().email())

        greeting.content = self.request.get('content')
# Validate content exists and is not blank, if so put to Datastore
        if greeting.content and greeting.content.isspace() == False:
            greeting.put()
            self.redirect('/')
        else:
# Mark's error message from the Udacity webcase
            self.redirect('/?error=Error, please input text!')


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/stage1', StageOne),
                               ('/stage2', StageTwo),
                               ('/stage3', StageThree),
                               ('/stage4', StageFour),
                               ('/sign', BulletinBoard)
                               ],
                              debug=True)
