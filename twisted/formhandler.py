from twisted.web import http

def renderHomePage(request):
    colors = 'red', 'blue', 'green'
    flavors = 'vanilla', 'chocolate', 'strawberry', 'coffee'
    request.write("""
    <html>
    <head>
        <title>Form Test</html>
    </head>
    <body>
        <form action='posthandler' method='post'>
        Your name:
        <p>
            <input type='text' name='name'>
        </p>
        What's your favorite color?
        <p>
        """)
    for color in colors:
        request.write(
                "<input type='radio' name='color' value='%s'>%s<br />" % (color, color.capitalize()))
    request.write("""
    </p>
    What kinds of ice cream do you like?
    <p>
    """)
    for flavor in flavors:
        request.write(
                "<input type='checkbox' name='flavor' value='%s'>%s<br />" % (flavor, flavor.capitalazie())
    request.write("""
    </p>
    <input type='submit' />
    </form>
    </body>
    </html>
    """)
    request.finish()

def handlePost(request):
    request.write("""
    <html>
    <head>
    <title>Posted form datagg</title>
    </head>
    <body>
    <h1>Form Data</h1>
    """)

