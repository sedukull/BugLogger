import sqlalchemy

def connect(host,user,passwd,db,port):
    engine = sqlalchemy.create_engine("mysql+mysqldb://"+ user + ":" + passwd + "@" + host +"/"+db)
    m2 = sqlalchemy.MetaData(schema='cloud_bugs')
    '''
    bugs = sqlalchemy.Table('bugs',m2,autoload=True,autoload_with=engine)
    with engine.connect() as conn:
        conn.execute(bugs.insert(),{'bugid': 'CLOUDSTACK-5674', 'testname': "test_nic.TestAbc.test_1" , "component":"networks","version":4.3,"result":"failure","message" : "failed tc", "type":"bvt","hwtype":"kvm","trace":"abc", "state":"open","subject":"test_1 failed","trace":"test_1 failed"},
{'bugid': 'CLOUDSTACK-5675', 'testname': "test_nic.TestAbc.test_1" , "component":"networks","version":4.3,"result":"failure","message" : "failed tc", "type":"bvt","hwtype":"kvm", "state":"open","subject":"test_1 failed","trace":"test_1 failed"})
   '''

connect("localhost","root","password","cloud_bugs",3306)
