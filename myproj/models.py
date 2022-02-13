from control import db,app
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin,LoginManager
from flask import session

#admin
db.Model.metadata.reflect(db.engine)

class Docteurs(db.Model,UserMixin):

    __table__ = db.Model.metadata.tables['med']

    def __repr__(self):
        return self.DISTRICT
class Posts(db.Model):
    __table_args__ = {'extend_existing': True}
    id=db.Column('post_id',db.Integer,primary_key=True)
    titre=db.Column(db.String(100),nullable=False,unique=True)
    text=db.Column(db.Text,nullable=False)
    image=db.Column(db.Text)
    ordre=db.Column(db.Integer,nullable=False,unique=True)

    def __init__(self,id,titre,text,image,ordre) :
        self.id=id
        self.titre=titre
        self.text=text
        self.image=image
        self.ordre=ordre





class MyModelView(ModelView):
    def is_accessible(self):
        return True if "logged_in" in session else abort(403)


admin=Admin(app)
admin.add_view(MyModelView(Docteurs,db.session))
admin.add_view(MyModelView(Posts,db.session))
