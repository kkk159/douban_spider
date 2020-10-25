import requests
from bs4 import BeautifulSoup
import mysql.connector
 
def create_db():
    mydb = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    passwd = 'DKY159754',
    auth_plugin = 'mysql_native_password'
    )   
    mycursor = mydb.cursor()
    mycursor.execute('CREATE DATABASE douban_movie')
    mycursor.close()
    mydb.close   

def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE top250 (score FLOAT,name VARCHAR(255),quote VARCHAR(255),people VARCHAR(255))')

def get_pages_link(conn):
    # 插入到数据库
    cursor = conn.cursor()
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36',
        'Connection': 'keep-alive'
    }
 
    for item in range(0, 250, 25):
        url = "https://movie.douban.com/top250?start={}".format(item)
        web_data = requests.get(url, headers=header)
        soup = BeautifulSoup(web_data.content, 'lxml')
        for movie in soup.select('#wrapper li'):
 
            #href = movie.select('.hd > a')[0]  # 链接
            href=movie.find('a')["href"]
            name = movie.select('.hd > a > span')[0].text  # 片名
            star = movie.select('.rating_num')[0].text  # 评分
            people = movie.select('.star > span')[3].text  # 评价人数
            try:
                quote = movie.select('.inq')[0].text
            except:
                print('没有quote哦')
                quote = None
            data = {
                # 'url': href,
                '评分': star,
                '片名': name,
                '名言': quote,
                '评价人数': people
            }
            sql = 'insert into top250(score,name,quote,people) values (%f,"%s","%s","%s")' % (
                float(star), name, quote, people)
            cursor.execute(sql)
            conn.commit()
 
            print(data)
            # print(movie)
        print('\n' + '-' * 50 + '\n')
    # 关闭数据库
    cursor.close()
    conn.close
 
 
if __name__ == '__main__':
    try:
        create_db()
    except:
        print('Database already exists.')
        pass
    conn = mysql.connector.connect(user='root', password='DKY159754', database = 'douban_movie', auth_plugin = 'mysql_native_password')
    cursor = conn.cursor()
    try:
        create_table(conn)
    except:
        _input = input('Table already exists. Clear it? Y/n: ')
        if _input == 'y' or 'Y':
            print('Clearing...')
            cursor.execute('DELETE FROM top250')
    get_pages_link(conn)