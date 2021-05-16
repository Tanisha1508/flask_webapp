#original name of this file was flask_webapp.py---->changed to run.py
from flask_webapp import app #this app exists in __init__.py
if __name__=="__main__":
    app.run(debug=True)


#ctrl shift R for hard refresh--clear cache
# template inheritence so that we don't have to reapeat the code and just write the unique code
# a block is the part in template which the children templates can override
# so we create a block in layout.html

#28.08