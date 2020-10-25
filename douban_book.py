import requests
from bs4 import BeautifulSoup
import mysql.connector
import re 
 
def create_db():
    mydb = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    passwd = 'DKY159754',
    auth_plugin = 'mysql_native_password'
    )   
    mycursor = mydb.cursor()
    mycursor.execute('CREATE DATABASE douban_book')
    mycursor.close()
    mydb.close   

def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE top250 (title VARCHAR(255), star FLOAT, people FLOAT, quote VARCHAR(255), author VARCHAR(255), translator VARCHAR(255), presser VARCHAR(255), date VARCHAR(255), price FLOAT, url VARCHAR(255))')

def get_pages_link(conn):
    # 插入到数据库
    cursor = conn.cursor()
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36',
        'Connection': 'keep-alive'
    }
 
    for item in range(0, 250, 25):
        url = "https://book.douban.com/top250?start={}".format(item)
        web_data = requests.get(url, headers=header)
        soup = BeautifulSoup(web_data.content, 'lxml')
        for book in soup.select('#wrapper table'):
 
            url = book.find_all('a')[1]['href']  # 链接
            title = book.find_all('a')[1]['title'] 
            pub_info = book.find('p').text
            pub_info_split = pub_info.split('/')
            if len(pub_info_split) == 4:
                [author, presser, date, _price] = [i.strip() for i in pub_info_split]
                translator = None
            if len(pub_info_split) == 5:
                [author, translator, presser, date, _price] = [i.strip() for i in pub_info_split]
            star = book.select('.star.clearfix > span')[1].text  # 评分
            _people = book.select('.star.clearfix > span')[2].text 
            people = re.findall(re.compile(r'\(\n *(\d*)人评价\n *\)'), _people)[0]
            price = re.findall(re.compile(r'(\d+\.*\d*)'), _price)[0]
            
            try:
                quote = book.select('.inq')[0].text
            except:
                print('没有quote')
                quote = None
            data = {
                '书名': title,
                '评分': star,
                '评价人数': people,
                '名言': quote,
                '作者': author,
                '翻译': translator,
                '出版社': presser,
                '日期': date,
                '价格': price,
                'url': url,
            }
            sql = 'insert into top250(title,star,people,quote,author,translator,presser,date,price,url) values ("%s",%f,%f,"%s","%s","%s","%s","%s",%f,"%s")' % (
                title, float(star), int(people), quote, author, translator, presser, date, float(price), url)
            cursor.execute(sql)
            conn.commit()
 
            print(data)
            # print(book)
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
    conn = mysql.connector.connect(user='root', password='DKY159754', database = 'douban_book', auth_plugin = 'mysql_native_password')
    cursor = conn.cursor()
    try:
        create_table(conn)
    except:
        _input = input('Table already exists. Drop it? Y/n: ')
        if _input == 'y' or 'Y':
            print('Dropping...')
            cursor.execute('Drop top250')
    get_pages_link(conn)