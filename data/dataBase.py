from os import path
import sqlite3
from pprint import pp, pprint

class DataMed:
    
    def connection(self):
        con=None
        try:
            con=sqlite3.connect("docs.db")
        except sqlite3.Error as ex:
            print(ex)
        return con

    def requestTable(self,con):
        try:
            c=con.cursor()
            c.execute("""CREATE TABLE med (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nom VARCHAR(40) NOT NULL,
                            specialite VARCHAR(50) NOT NULL,
                            modeExercice VARCHAR(50),
                            adresse VARCHAR(100),
                            telephone VARCHAR(13),
                            gouvernorat VARCHAR(30),
                            maps text null
                            );""")
        except sqlite3.Error as ex:
            print(ex)


    def createTable(self):
        con=self.connection()
        if con!=None:
            self.requestTable(con)
        else:
            print("Connexion can't be created!".upper())


    def createIndexes(self):
        with self.connection() as con:
            c=con.cursor()
            c.execute('select * from med')
            columns=tuple(map(lambda x: x[0], c.description))
            for col in columns:
                c.execute("CREATE INDEX {} ON med({});".format("ind"+col,col))

    def __create_task(self,con,rqst,task):
        cur=con.cursor()
        if type(task) is tuple:
            cur.execute(rqst,task)
            print("TUPLE ADDED SUCCESSFULY!")
        elif type(task) is list:
            cur.executemany(rqst,task)
            print("LIST ADDED SUCCESSFULY!")
        else:
            if type(task) is int:
                cur.execute(rqst,(task,))
            else:
                print("TYPE INVALIDE!")
        con.commit()
        return cur.lastrowid

    def insert_data(self,con,task):
        rqst="insert into med (nom,specialite,modeExercice,adresse,telephone,gouvernorat) values (?,?,?,?,?,?);"
        self.__create_task(con,rqst,task)

    def delete_task_by_id(self,con,id):
        rqst='delete from med where id=?'
        self.__create_task(con,rqst,id)
        
    def delete_all_tasks(self,con):
        cur=con.cursor()
        cur.execute("delete from med")
        con.commit()

    def __showData(self,con,sql,task=None):
        try:
            cur=con.cursor()
            if not task:
                cur.execute(sql)
            else:
                cur.execute(sql,task)
            rowNames=list(map(lambda x: x[0], cur.description))
            returnRes=[]
            for row in cur.fetchall():
                dictTasks={}
                for elem in row:
                    dictTasks[rowNames[row.index(elem)]]=elem
                returnRes.append(dictTasks)
            return returnRes
        except sqlite3.Error as ex:
            print(ex)



    def show_all_tasks(self,con):
        return self.__showData(con,"select * from med")

    def show_data_condition(self,con,request,task):
        if type(task) is tuple:
            return self.__showData(con,request,task)            
        elif type(task) is list:
            return self.__showData(con,request,tuple(task))
        return self.__showData(con,request,(task,))


if __name__=="__main__":
    with DataMed().connection() as con:
        pass