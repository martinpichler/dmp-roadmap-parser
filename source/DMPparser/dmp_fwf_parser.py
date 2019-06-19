import re
import psycopg2
from DMPparser.fwf_parser import FWFParser

class DMPFWFParser():
    
    def __init__(self, user, password, host, port, database, dmpid):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self.dmpid = dmpid
        
    def cleanhtml(self, raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext
    
    def parse(self):
        try:
            connection = psycopg2.connect(user = self.user,
                                  password = self.password,
                                  host = self.host,
                                  port = self.port,
                                  database = self.database)
            cursor = connection.cursor()
            postgreSQL_select_Query = "select * from plans where identifier = %s order by updated_at"
            cursor.execute(postgreSQL_select_Query, (self.dmpid,))
            plans = cursor.fetchall()
            row = plans[-1]
            dmp_title = row[1]
            dmp_description = row[7]
            dmp_created = str(row[3])
            dmp_modified = str(row[4])
            dmp_id =  row[6]
            pi_name = row[8]
            pi_mail = row[15]
            pi_orcid = row[9]
    
            postgreSQL_select_Query = "SELECT * FROM answers a INNER JOIN questions q ON a.question_id = q.id WHERE a.plan_id = %s ORDER BY q.section_id, q.number"
            cursor.execute(postgreSQL_select_Query, (row[0],))
            answers = cursor.fetchall()
            processed_answers = []
            for answer in answers:
                processed_answer = self.cleanhtml(answer[1].replace("<br />","\n"))
                processed_answers.append(processed_answer)
            
            # parse actual data
            fwfp = FWFParser(dmp_title, dmp_description, dmp_created, dmp_modified, dmp_id, pi_name, pi_mail, pi_orcid)
            fwfp.parse_question_1_1(processed_answers[0])
            fwfp.parse_question_1_1_1(processed_answers[0])
            fwfp.parse_question_2_1(processed_answers[1])
            fwfp.parse_question_2_2(processed_answers[2])
            fwfp.parse_question_2_3(processed_answers[3])
            fwfp.parse_question_3_1(processed_answers[4])
            fwfp.parse_question_3_2(processed_answers[5])
            fwfp.parse_question_4_1(processed_answers[6])
            fwfp.parse_question_4_2(processed_answers[7])
            return fwfp.generate()
            
        except (Exception) as error :
            print ("error", error)
        except (psycopg2.Error) as error:
            print ("Error while connecting to PostgreSQL", error)
        finally:
            #closing database connection.
            if(connection):
                cursor.close()
                connection.close()
                