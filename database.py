import pymysql

#
def storageDatabase(selected_keys, name, objectName):
    
    
    db = pymysql.connect(host='127.0.0.1', port=3306, user='pi', passwd='blueberry', db='blueberry', charset='utf8')

    try:
        cursor = db.cursor()

        sql = "DELETE FROM shortcuts WHERE position = %s"
        cursor.execute(sql, (objectName))
            
        #storage all of keys
        for num in selected_keys:
            sql = "INSERT INTO shortcuts (label, t_keys, position) VALUES (%s, %s, %s)"
            cursor.execute(sql, (name, num, objectName))
            
        sql = "SELECT label FROM shortcuts WHERE position = %s"
        existObject = cursor.execute(sql, (objectName))
        
        if existObject == 0:
            result = 1
        else:
            result = 0
            
        db.commit()
    
    finally:
        db.close()

    return result

#
def setDatabase(objectName):
    
    db = pymysql.connect(host='127.0.0.1', port=3306, user='pi', passwd='blueberry', db='blueberry', charset='utf8')
    
    try:
        cursor = db.cursor()
        
        sql = "SELECT label FROM shortcuts WHERE position = %s"
        existObject = cursor.execute(sql, (objectName))
        
        if existObject == 0:
            result = 0
        else:
            result = cursor.fetchone()
            result = str(result)
            length = len(result)
            result = result[2:length-3]
        
        db.commit()
    finally:
        db.close()
        
    return result;

#
def keyDatabase(objectName, num):
    
    db = pymysql.connect(host='127.0.0.1', port=3306, user='pi', passwd='blueberry', db='blueberry', charset='utf8')
    
    try:
        cursor = db.cursor()
        num=num
        sql = "SELECT t_keys FROM shortcuts WHERE id IN (SELECT id+%s FROM shortcuts WHERE position = %s)"
        existObject = cursor.execute(sql, (num, objectName))
        
        if existObject == 0:
            result = 0
        else:
            result = cursor.fetchone()
            result = str(result)
            length = len(result)
            result = result[2:length-3]
        
        db.commit()
    finally:
        db.close()
        
    return result;

#
def countDatabase(objectName):
    
    db = pymysql.connect(host='127.0.0.1', port=3306, user='pi', passwd='blueberry', db='blueberry', charset='utf8')
    
    try:
        cursor = db.cursor()
        
        sql = "SELECT COUNT(*) FROM shortcuts WHERE position = %s"
        existObject = cursor.execute(sql, (objectName))
        
        if existObject == 0:
            result = 0
        else:
            result = cursor.fetchone()
            result = str(result)
            length = len(result)
            result = result[1:length-2]
            result=int(result)
        db.commit()
    finally:
        db.close()
        
    return result;

#
def startDatabase():

    db = pymysql.connect(host='127.0.0.1', port=3306, user='pi', passwd='blueberry', db='blueberry', charset='utf8')

    try:
        cursor = db.cursor()
    
        sql = "SELECT 1 FROM Information_schema.tables WHERE table_schema='blueberry' AND table_name='shortcuts'"
    
        #exist database(table) -> return 1
        #no database(table) -> return 0
        if cursor.execute(sql)==0:
            
            sql = '''
                    CREATE TABLE shortcuts (
                        id INT UNSIGNED NOT NULL AUTO_INCREMENT,
                        label VARCHAR(20) NOT NULL,
                        t_keys VARCHAR(6) NOT NULL,
                        position VARCHAR(13) NOT NULL,
                        PRIMARY KEY(id)
                    );
                '''
            # 실행하기
            cursor.execute(sql)

            #default key 등록
            # 0. MaxPage
            sql = "INSERT INTO shortcuts (label, t_keys, position) VALUES ('2', '0', '0')"
            cursor.execute(sql)
            # 1. copy
            sql = "INSERT INTO shortcuts (label, t_keys, position) VALUES ('copy', 'ctrl', 'pushButton_1')"
            cursor.execute(sql)
            sql = "INSERT INTO shortcuts (label, t_keys, position) VALUES ('copy', 'c', 'pushButton_1')"
            cursor.execute(sql)
            # 2. paste
            sql = "INSERT INTO shortcuts (label, t_keys, position) VALUES ('paste', 'ctrl', 'pushButton_2')"
            cursor.execute(sql)
            sql = "INSERT INTO shortcuts (label, t_keys, position) VALUES ('paste', 'v', 'pushButton_2')"
            cursor.execute(sql)
            # 3. select all
            sql = "INSERT INTO shortcuts (label, t_keys, position) VALUES ('all', 'ctrl', 'pushButton_3')"
            cursor.execute(sql)
            sql = "INSERT INTO shortcuts (label, t_keys, position) VALUES ('all', 'a', 'pushButton_3')"
            cursor.execute(sql)
            # 4. enter
            sql = "INSERT INTO shortcuts (label, t_keys, position) VALUES ('enter', 'enter', 'pushButton_4')"
            cursor.execute(sql)
            # 5. cut
            sql = "INSERT INTO shortcuts (label, t_keys, position) VALUES ('cut', 'ctrl', 'pushButton_5')"
            cursor.execute(sql)
            sql = "INSERT INTO shortcuts (label, t_keys, position) VALUES ('cut', 'x', 'pushButton_5')"
            cursor.execute(sql)
            # 6. task manager
            sql = "INSERT INTO shortcuts (label, t_keys, position) VALUES ('manager', 'ctrl', 'pushButton_6')"
            cursor.execute(sql)
            sql = "INSERT INTO shortcuts (label, t_keys, position) VALUES ('manager', 'shift', 'pushButton_6')"
            cursor.execute(sql)
            sql = "INSERT INTO shortcuts (label, t_keys, position) VALUES ('manager', 'esc', 'pushButton_6')"
            cursor.execute(sql)
            # 7. esc
            sql = "INSERT INTO shortcuts (label, t_keys, position) VALUES ('ESC', 'esc', 'pushButton_7')"
            cursor.execute(sql)
            # 8. abc
            sql = "INSERT INTO shortcuts (label, t_keys, position) VALUES ('abc', 'a', 'pushButton_8')"
            cursor.execute(sql)
            sql = "INSERT INTO shortcuts (label, t_keys, position) VALUES ('abc', 'b', 'pushButton_8')"
            cursor.execute(sql)
            sql = "INSERT INTO shortcuts (label, t_keys, position) VALUES ('abc', 'c', 'pushButton_8')"
            cursor.execute(sql)
            # 9. space
            sql = "INSERT INTO shortcuts (label, t_keys, position) VALUES ('space', 'space', 'pushButton_9')"
            cursor.execute(sql)

        db.commit()
    
    finally:
        db.close()

    return 0
