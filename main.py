import os
import jinja2
import webapp2

template_dir = os.path.join(os.path.dirname(__file__), "templates")
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

class MainPage(Handler):
    def get(self):
        self.render("IPND_notes.html")

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

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/stage1', StageOne),
                               ('/stage2', StageTwo),
                               ('/stage3', StageThree),
                               ('/stage4', StageFour),
                               ],
                              debug=True)
