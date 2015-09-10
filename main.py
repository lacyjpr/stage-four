import jinja2
import os
import urllib
import webapp2
from google.appengine.api import users
from google.appengine.ext import ndb

# Initialize jinja.
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

# Copied from Udacity lectures.
class Handler(webapp2.RequestHandler):
    """Main Handler for the app"""
    def write(self, *a, **kw):
        """Writes to the browser."""
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        """Use jinja to get the template, return rendered template object"""
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        """Renders template to the browser."""
        self.write(self.render_str(template, **kw))

class StageOne(Handler):
    """Renders stage_one to the browser"""
    def get(self):
        self.render("stage_one.html")

class StageTwo(Handler):
    """Renders stage_two to the browser"""
    def get(self):
        self.render("stage_two.html")

class StageThree(Handler):
    """Renders stage_three to the browser"""
    def get(self):
        self.render("stage_three.html")

class StageFour(Handler):
    """Renders stage_four to the browser"""
    def get(self):
        self.render("stage_four.html")

DEFAULT_BULLETINBOARD_NAME = 'stage_four'

# Copied from Udacity's wallbook example.
def bulletinboard_key(bulletinboard_name=DEFAULT_BULLETINBOARD_NAME):
    """Constructs a Datastore key for a Bulletinboard entity.

    We use bulletinboard_name as the key.
    """
    return ndb.Key('Bulletinboard', bulletinboard_name)

# Copied from Udacity's wallbook example.
class Author(ndb.Model):
    """Sub model for representing an author."""
    identity = ndb.StringProperty(indexed=True)
    name = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)

# Copied from Udacity's wallbook example.
class Comment(ndb.Model):
    """A main model for representing an individual Bulletinboard entry."""
    author = ndb.StructuredProperty(Author)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

# Largely borrowed from Google's example code.
class MainPage(Handler):
    """Builds the main page including the bulletin board"""
    def get(self):
        # Mark's error variable from the Udacity webcast.
        error = self.request.get('error','')
        bulletinboard_name = self.request.get('bulletinboard_name',
                                          DEFAULT_BULLETINBOARD_NAME)

        # Query Datastore for comments ordered by date descending.
        # Store the results in comments_query.
        comments_query = Comment.query(
            ancestor=bulletinboard_key(bulletinboard_name)).order(-Comment.date)

        # Fetch comments from our query, store them in the variable comments.
        comments_to_fetch = 20
        comments = comments_query.fetch(comments_to_fetch)

        # Check if the user is logged in to Google. If so, use their user info
        # and give them the option to log out.
        # If not, give them the option to log in.
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        # Key: Value pairs to pass to the template.
        template_values = {
            'user': user,
            'comments': comments,
            'bulletinboard_name': urllib.quote_plus(bulletinboard_name),
            'url': url,
            'url_linktext': url_linktext,
            'error': error,
        }

        # Render our page with the values above.
        template = jinja_env.get_template('IPND_notes.html')
        self.write(template.render(template_values))

# Largely borrowed from Google's example code.
class BulletinBoard(Handler):
    """Takes input from the form and adds it to Datastore"""
    def post(self):
        # We set the same parent key on the 'Comment' to ensure each
        # Comment is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        bulletinboard_name = self.request.get('bulletinboard_name',
                                          DEFAULT_BULLETINBOARD_NAME)
        comment = Comment(parent=bulletinboard_key(bulletinboard_name))

        # If the user is logged in, instantiate the Author class.
        if users.get_current_user():
            comment.author = Author(
                    identity=users.get_current_user().user_id(),
                    name=users.get_current_user().nickname(),
                    email=users.get_current_user().email())

        # Get the content of the comment.
        comment.content = self.request.get('content')

        # Validate content exists and is not blank, if so put to Datastore.
        if comment.content and comment.content.isspace() == False:
            comment.put()
            self.redirect('/')
        else:
        # Mark's error message from the Udacity webcast.
            self.redirect('/?error=Error, please input text!')

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/stage1', StageOne),
                               ('/stage2', StageTwo),
                               ('/stage3', StageThree),
                               ('/stage4', StageFour),
                               ('/post', BulletinBoard)
                               ],
                              debug=True)
