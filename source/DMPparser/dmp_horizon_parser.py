import re
import psycopg2
from DMPparser.horizon_parser import HorizonParser

class DMPHorizonParser():
    
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
            hp = HorizonParser(dmp_title, dmp_description, dmp_created, dmp_modified, dmp_id, pi_name, pi_mail, pi_orcid)
            hp.parse_question_1_1(processed_answers[0])
            hp.parse_question_1_2(processed_answers[1])
            hp.parse_question_1_3(processed_answers[2])
            hp.parse_question_1_4(processed_answers[3])
            hp.parse_question_1_5(processed_answers[4])
            hp.parse_question_1_6(processed_answers[5])
            hp.parse_question_1_7(processed_answers[6])
            hp.parse_question_2_1_1(processed_answers[7])
            hp.parse_question_2_1_3(processed_answers[9])
            hp.parse_question_2_1_4(processed_answers[10])
            hp.parse_question_2_1_5(processed_answers[11])
            hp.parse_question_2_1_6(processed_answers[12])
            hp.parse_question_2_2_1(processed_answers[13])
            hp.parse_question_2_2_1(processed_answers[14])
            hp.parse_question_2_2_3(processed_answers[15])
            hp.parse_question_2_2_4(processed_answers[16])
            hp.parse_question_2_2_5(processed_answers[17])
            hp.parse_question_2_3_1(processed_answers[18])
            hp.parse_question_2_3_2(processed_answers[19])
            hp.parse_question_2_4_1(processed_answers[20])
            hp.parse_question_2_4_2(processed_answers[21])
            hp.parse_question_2_4_3(processed_answers[22])
            hp.parse_question_2_4_4(processed_answers[23])
            hp.parse_question_2_4_5(processed_answers[24])
            hp.parse_question_3_1(processed_answers[25])
            hp.parse_question_3_2(processed_answers[26])
            hp.parse_question_3_3(processed_answers[27])
            hp.parse_question_4_1(processed_answers[28])
            hp.parse_question_5_1(processed_answers[29])
            hp.parse_question_6_1(processed_answers[30])
            return hp.generate()
            
        except (Exception) as error :
            print ("error", error)
        except (psycopg2.Error) as error:
            print ("Error while connecting to PostgreSQL", error)
        finally:
            #closing database connection.
            if(connection):
                cursor.close()
                connection.close()
                