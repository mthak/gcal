CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

decorator = oauth2decorator_from_clientsecrets(
    CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/calendar',
    message=MISSING_CLIENT_SECRETS_MESSAGE)

service = build('calendar', 'v3')

class MainPage(webapp2.RequestHandler):
  @decorator.oauth_required
  def get(self):
    # index.html contains a form that calls my_form
    template = jinja_enviroment.get_template("index.html")
    self.response.out.write(template.render())

class MyRequestHandler(webapp2.RequestHandler):
  @decorator.oauth_aware
  def post(self):
    if decorator.has_credentials():

      # time_min and time_max are fetched from form, and processed to make them
      # rfc3339 compliant
      time_min = some_process(self.request.get(time_min))
      time_max = some_process(self.request.get(time_max))

      # Construct freebusy query request's body
      freebusy_query = {
        "timeMin" : time_min,
        "timeMax" : time_max,
        "items" :[
          {
            "id" : my_calendar_id
          }
        ]
      }

      http = decorator.http()
      request = service.freebusy().query(freebusy_query)
      result = request.execute(http=http)
    else:
      # raise error: no user credentials

app = webapp2.WSGIApplication([
    ('/', MainPage),     
    ('/my_form', MyRequestHandler),
    (decorator.callback_path, decorator.callback_handler())
], debug=True)

