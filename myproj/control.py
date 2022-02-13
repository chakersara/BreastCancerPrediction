from re import search
import re
from flask import (redirect, render_template, request,session,jsonify)
from flask.helpers import url_for
import flask_whooshalchemy3 as wa
from flask_admin.contrib.sqla import ModelView
from flask_cors import CORS, cross_origin
from flask_login import LoginManager, UserMixin
from sqlalchemy.sql.elements import or_
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash, generate_password_hash
from app import createApp, createBD
from service import Service


s=Service()
app=createApp()

@app.route("/")
def index():
    return render_template("index.html",lenlinkTup=s.youtubeLinks(),articles=Posts.query.order_by(Posts.ordre.asc()).all())

@app.route('/docteurs')
def docteurs():
    return render_template("docteurs.html",liste=s.gouvs,medListe=s.getAllMedTab())


@app.route("/docteurs/ville=<name>")
def docteurVille(name):
    return render_template("docteurs.html",liste=s.gouvs,medListe=s.getMedVille(name.split("&")))

@app.route("/docteurs/spec=<spc>")
def docteurSpec(spc):
    return render_template("docteurs.html",liste=s.gouvs,medListe=s.getMedSpec(spc.split("&")))

@app.route("/docteurs/ville=<ville>/spec=<spc>")
def docteurVilleSpec(ville,spc):
    return render_template("docteurs.html",liste=s.gouvs,medListe=s.getMedVilleSpec(ville.split("&"),spc.split("&")))

@app.route("/form",methods=["POST",'GET'])
def formMed():
    dictDOC={"Carcinologie médicale":"carc",'Gynécologie obstétrique':'genyco'}
    if request.method=="POST":
        getGouv=[gouv for gouv in s.gouvLow() if request.form.get(gouv)!=None]
        specChecked=[dictDOC.get(spec) for spec in ('Carcinologie médicale','Gynécologie obstétrique') if request.form.get(spec)!=None]
        if  not getGouv and not  specChecked:
            return redirect("/docteurs")
        if getGouv and specChecked:
            return redirect("/docteurs/ville={}/spec={}".format("&".join(getGouv),"&".join(specChecked)))
        if getGouv and not specChecked :
            return redirect("/docteurs/ville={}".format("&".join(getGouv)))
        if specChecked and not getGouv:
            return redirect("/docteurs/spec={}".format("&".join(specChecked)))

def redirect_url(default='admin'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)



cors=CORS(app)     
@app.route("/api/chatbot/<string:ref>")
@cross_origin('*')
def chatbotAPI(ref):
    return s.chatBot(ref)

#admin
db=createBD(app)
gouvernorats=list(map(lambda x:x[0],db.session.execute("select distinct gouvernorat from med")))
login = LoginManager()

#db.Model.metadata.reflect(db.engine)

class Docteurs(db.Model):
    #__table__ = db.Model.metadata.tables['med']
    __tablename__="med"
    __table_args__ = {'extend_existing': True}
    id=db.Column(db.Integer,primary_key=True)
    nom=db.Column(db.String(100),nullable=False)
    specialite=db.Column(db.String(200),nullable=False)
    modeExercice=db.Column(db.String(100))
    adresse=db.Column(db.Text)
    telephone=db.Column(db.String(200))
    gouvernorat=db.Column(db.String(20),nullable=False)
    maps=db.Column(db.Text)

    def __init__(self,nom,specialite,modeExercice,adresse,telephone,gouvernoart):
       self.nom=nom
       self.specialite=specialite
       self.adresse=adresse
       self.gouvernorat=gouvernoart
       self.telephone=telephone
       self.modeExercice=modeExercice


class Sm:  
    def DocFilter_nom_modeex_adresse_tel(self,search):
        return Docteurs.nom.like(search),Docteurs.telephone.like(search),Docteurs.adresse.like(search),\
                        Docteurs.modeExercice.like(search)
    def keysDoc(self):
        return tuple(db.session.execute("select * from med").keys())[:-1]
    def docById(self,id):
        return Docteurs.query.filter_by(id=id).first()
    def all_gouvs(self):
        return list(map(lambda elem:elem[0],db.session.query(Docteurs.gouvernorat).distinct().all()))
    def all_spec(self):
        return list(map(lambda elem:elem[0],db.session.query(Docteurs.specialite).distinct().all()))
    def docByGouv(self,gouv):
        return Docteurs.query.filter_by(gouvernorat=gouv).all()
    def DocGouv(self,gouv):
        return Docteurs.query.filter_by(gouvernorat=gouv).all()
    def DocSpec(self,spec):
        return Docteurs.query.filter_by(specialite=spec).all()
    def DocSpecQuery(self,spec):
        return Docteurs.query.filter_by(specialite=spec)
    def DocGouvSpec(self,gouv,spec):
        return Docteurs.query.filter_by(specialite=spec,gouvernorat=gouv).all()
    def color(self,nb):
        if nb<=5:
            return 'rgba(255, 0, 0, 0.368)'
        if nb<=10:
            return 'rgba(255, 255, 0, 0.391)'
        if nb<=15:
            return 'rgba(32, 32, 231, 0.375)'
        return 'rgba(0, 128, 0, 0.375)'
    def all_DocGouv(self):
        gouvs,nbDoc,colors=[],[],[]
        for gouv in self.all_gouvs():
            gouvs.append(gouv)
            nb=len(self.DocGouv(gouv))
            nbDoc.append(nb)
            colors.append(self.color(nb))
        return gouvs,nbDoc,colors
    def all_DocSpec(self):
        specs,nbDoc=[],[]
        for spc in self.all_spec():
            specs.append(spc)
            nbDoc.append(len(self.DocSpec(spc)))
        return specs,nbDoc
    def all_DocGyn(self):
        return [len(self.DocGouvSpec(gouv,'Gynécologie obstétrique')) for gouv in self.all_gouvs() ]
        
    def all_docCanc(self):
        return [len(self.DocGouvSpec(gouv,'Carcinologie médicale')) for gouv in self.all_gouvs() ]

    def addDoc(self,nom,specialite,modeExercice,adresse,telephone,gouvernorat):
        db.session.add(Docteurs(nom,specialite,modeExercice,adresse,telephone,gouvernorat))
        db.session.commit()
    def getFormAttDoc(self,form):
        return form.get('nom'),form.get('spec'),form.get("modeex",""),\
                form.get("adresse",""),form.get("tel",""),form.get("gouv")
    def updateDoc(self,ent,nom,specialite,modeExercice,adresse,telephone,gouvernorat):
        ent.nom,ent.specialite,ent.modeExercice,ent.adresse,ent.telephone,ent.gouvernorat=\
            nom,specialite,modeExercice,adresse,telephone,gouvernorat
        db.session.commit()
    def addAdmin(self,email,username,password,role):
        db.session.add(AdminModel(email,username,password,role))
        db.session.commit()
    def AdminByEmail(self,email):
        return AdminModel.query.filter_by(email=email).first()
    def AdminByUsername(self,username):
        return(AdminModel.query.filter_by(username=username).first())
    def AdminById(self,id):
         return(AdminModel.query.filter_by(id=id).first())
    def AdminSQLtoEnt(self,ent):
        return AdminModel(self,ent.name,ent.username,ent.password,ent.role)
    def deleteEnty(self,ent):
        db.session.delete(ent)
        db.session.commit()




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

class AdminModel(UserMixin, db.Model):
    __tablename__ = 'admins'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True,nullable=False)
    username = db.Column(db.String(100),unique=True,nullable=False)
    password = db.Column(db.Text)
    role=db.Column(db.String(20))

    def __init__(self,email,username,password,role):
        self.email=email
        self.username=username
        self.password=generate_password_hash(password)
        self.role=role
        
class MyModelView(ModelView):
    def is_accessible(self):
        if 'logged_in' in session:
            return True
        else:
            abort(403)
        
"""db.create_all()
db.session.add(AdminModel("test@gmail.com","test123","testtest","superadmin"))
db.session.commit()"""

"""admin=Admin(app)
admin.add_view(MyModelView(Docteurs,db.session))
admin.add_view(MyModelView(Posts,db.session))"""

@app.route('/admin/index')
def admin():
    try:
        if 'logged_in' in session:
            nbCar,nbGy=Sm().all_docCanc(),Sm().all_DocGyn()
            specNames,specNum=Sm().all_DocSpec()
            labels,values,colors=Sm().all_DocGouv()
            return render_template("dashboard/pages/charts/chartjs.html",user=session['username'],roleUser=session['role'],valuesChart=values,labelsChart=labels,colors=colors,\
                specNames=specNames,specNum=specNum,nbCar=nbCar,nbGy=nbGy)
        else:
            abort(403)
    except Exception as ex:
        print(ex)
        abort(403)

@app.route("/admin/login",methods=["POST","GET"])
def login():
    roles_dic={'admin':"Administrateur","superadmin":"Super Administrateur"}
    if request.method=="POST":
        getUsernameBD=AdminModel.query.filter_by(username=request.form.get("username")).first()
        if getUsernameBD!=None:
            if check_password_hash(getUsernameBD.password,request.form.get("password")):
                session['logged_in']=True
                session['username']=getUsernameBD.username
                session['role']=roles_dic.get(getUsernameBD.role,"Administrateur")
                return redirect(url_for('admin'))
                #return redirect('/admin')
        return render_template("login.html",failed=True)
    return render_template("login.html")

@app.route("/admin/medecins",methods=["GET","POST"])
@app.route("/admin/medecins",methods=["GET","POST"])
def tables():    
    if 'logged_in' in session:
        keys=Sm().keysDoc()
        page = request.args.get('page', 1, type=int)
        query=Docteurs.query
        values=query.paginate(page=page, per_page=15)
        try:
            if request.method=="GET":
                search="%{}%".format(request.args.get("search"))
                searchSpec=request.args.get('spec')
                if  searchSpec.startswith('Toute') or searchSpec==None :
                    query=Docteurs.query.filter(or_(*Sm().DocFilter_nom_modeex_adresse_tel(search)))
                    values = query.paginate(page=page, per_page=15)
                else :
                    query=Docteurs.query.filter(or_(*Sm().DocFilter_nom_modeex_adresse_tel(search)),Docteurs.specialite==searchSpec)
                    values = query.paginate(page=page, per_page=15)
                return render_template("dashboard/pages/tables/basic-table.html",user=session['username'],roleUser=session['role'],th=keys,values=values,total=len(query.all()))

        except Exception as ex:
            print(ex)

        return render_template("dashboard/pages/tables/basic-table.html",user=session['username'],roleUser=session['role'],th=keys,values=values,total=len(query.all()))
    else:
        abort(403)


@app.route("/admin/posts/")
@app.route("/admin/posts")
def posts():    
    if 'logged_in' in session:
        keys=tuple(db.session.execute("select * from posts").keys())[1:]
        page = request.args.get('page', 1, type=int)
        values = Posts.query.paginate(page=page, per_page=3)
        total=len(Posts.query.all())
        return render_template("dashboard/pages/tables/posts.html",user=session['username'],roleUser=session['role'],th=keys,values=values,total=total)
    else:
        abort(403)

@app.route("/admin/admins/")
@app.route("/admin/admins")
def adminsTable():    
    if 'logged_in' in session:
        keys=tuple(db.session.execute("select * from admins").keys())[1:]
        page = request.args.get('page', 1, type=int)
        values = AdminModel.query.paginate(page=page, per_page=6)
        total=len(AdminModel.query.all())
        return render_template("dashboard/pages/tables/admins.html",user=session['username'],roleUser=session['role'],th=keys,values=values,total=total)
    else:
        abort(403)


@app.route("/admin/deleteDoc/<id>")
def deleteDoc(id):
    if 'logged_in' in session:
        doc=Docteurs.query.filter_by(id=id).first()
        Sm().deleteEnty(doc)
        return redirect(redirect_url())
    return abort(403)

@app.route("/admin/update_docteur/<id>",methods=["POST","GET"])
def updateDoc(id):
    if 'logged_in' in session:
        if request.method=="POST":
            print("salut")
            form=request.form
            formAtt,doc=Sm().getFormAttDoc(form),Sm().docById(id)
            Sm().updateDoc(doc,*formAtt)
            return redirect(redirect_url())
        return render_template("dashboard/pages/forms/updateDoc.html",\
            user=session['username'],roleUser=session['role'],spec=Sm().all_spec(),\
                med=Sm().docById(id),gouv=Sm().all_gouvs())
    return abort(403)

@app.route("/admin/ajout_docteur",methods=["POST",'GET'])
def addDoc():
    if 'logged_in' in session:
        if request.method=="POST":
            specialite=Sm().all_spec()
            form=request.form
            if 'spec' not in form:
                return render_template("dashboard/pages/forms/addDocteur.html",user=session['username'],roleUser=session['role'],gouv=gouvernorats,spec=specialite,failed=True,success=False)
            formAtt=Sm().getFormAttDoc(form)
            Sm().addDoc(*formAtt)
            return render_template("dashboard/pages/forms/addDocteur.html",user=session['username'],roleUser=session['role'],gouv=gouvernorats,spec=specialite,failed=False,success=True)
        return render_template("dashboard/pages/forms/addDocteur.html",user=session['username'],roleUser=session['role'],gouv=gouvernorats,spec=Sm().all_spec(),failed=False)

    return abort(403)


@app.route("/admin/ajout_administrateur",methods=["POST",'GET'])
def addAdmin():
    if 'logged_in' in session:
        if request.method=="POST":
            form=request.form
         
            if form.get("mdp")!=form.get("mdp2"):
                return render_template("dashboard/pages/forms/addAdmin.html",user=session['username'],roleUser=session['role'],gouv=gouvernorats,failed=True,message="Les deux mots de passe ne sont pas identiques.")
            if len(form.get("mdp"))<8:
                return render_template("dashboard/pages/forms/addAdmin.html",user=session['username'],\
                    roleUser=session['role'],gouv=gouvernorats,failed=True,message="Le mot de passe doit comporter au moins 8 caractères.")
            if  Sm().AdminByEmail(form["email"])!=None:
                return render_template("dashboard/pages/forms/addAdmin.html",user=session['username'],\
                    roleUser=session['role'],gouv=gouvernorats,failed=True,message="Adresse e-mail déjà utilisée.")
            if Sm().AdminByUsername(form["username"])!=None:
                 return render_template("dashboard/pages/forms/addAdmin.html",user=session['username'],\
                    roleUser=session['role'],gouv=gouvernorats,failed=True,message="Nom d'utilisateur déjà utilisé.")
            Sm().addAdmin(form["email"],form['username'],form["mdp"],form['role'])
            return render_template("dashboard/pages/forms/addAdmin.html",user=session['username'],\
                    roleUser=session['role'],gouv=gouvernorats,success=True)   
        return render_template("dashboard/pages/forms/addAdmin.html",user=session['username'],roleUser=session['role'],gouv=gouvernorats,failed=False)
    return abort(403)


@app.route("/admin/delete_admin/<id>")
def deleteAdmin(id):
    if 'logged_in' in session:
        Sm().deleteEnty(Sm().AdminById(id))
        return redirect(redirect_url())
    return abort(403)


@app.route("/admin/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route('/predict',methods=["POST",'GET'])
def prediction():
    if request.method=="POST":
        if s.predictBCC(*tuple(request.form.values())) ==1:
           return render_template("predict.html",malade=True)
        else:
            return render_template("predict.html",nonmalade=True)
    return render_template("predict.html")

if __name__=="__main__":
    app.run(debug=True,port=8099)
    
    



