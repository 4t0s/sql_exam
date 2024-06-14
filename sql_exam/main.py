import psycopg2

class DB_Manager:
    def __init__(self, dbname, host, port, user, password):
        self.dbname: str = dbname
        self.host: str = host
        self.port: int = port
        self.user: str = user
        self.password: str = password
        self.connection: psycopg2.extensions.connection = None
        self.cursor: psycopg2.extensions.cursor = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(dbname=self.dbname,
                                               host=self.host,
                                               port=self.port,
                                               user=self.user,
                                               password=self.password)
            print("Connected successfully")
        except Exception as e:
            print(f"Connection refused: {e}")
        else:
            self.cursor = self.connection.cursor()

    def insert(self, table_name, **kwargs):
        columns = ', '.join([column for column in kwargs.get('columns', [])])
        values = ', '.join([f"'{column}'" if type(column) == str else f"{
                           column}" for column in kwargs.get('values', [])])
        query = f"INSERT INTO {table_name} ({columns}) values ({values})"
        try:
            self.cursor.execute(query=query)
            self.connection.commit()
        except Exception as error:
            print(f"Something gone wrong: {error}")

    def select(self, table_name, **kwargs):
        if kwargs.get('columns', False):
            if type(kwargs.get('columns')) == str:
                columns = kwargs.get('columns')
                query = f"SELECT {columns} from {table_name}"
            else:
                columns = ', '.join(
                    [column for column in kwargs.get('columns', [])])
                query = f"SELECT {columns} from {table_name}"
        else:
            query = f"SELECT * from {table_name}"
        try:
            self.cursor.execute(query=query)
            fetchall = self.cursor.fetchall()
            if fetchall != []:
                return fetchall
            else:
                self.cursor.fetchone()
        except Exception as e:
            print(f"Something gone wrong: {e}")

    def delete(self, table_name, id):
        if id:
            query = f"DELETE FROM {table_name} WHERE id={id}"
            try:
                self.cursor.execute(query)
                self.connection.commit()
            except Exception as e:
                print(f"Something gone wrong: {e}")
        else:
            print("You must provide id to delete something")

    def update(self, table_name, id, **kwargs):
        columns = kwargs.get('columns', [])
        values = kwargs.get('values', [])
        if len(columns) != len(values):
            print("Number of columns and values must be equal")
        sub_query = ""
        for idx in range(len(columns)):
            sub_query += f"{columns[idx]} = '{values[idx]}'"
            if not (idx == (len(columns) - 1)):
                sub_query+=", "
            print(sub_query)
        query = f"UPDATE {table_name} SET {sub_query} WHERE id = {id}"
        try:
            self.cursor.execute(query=query)
            self.connection.commit()
        except Exception as error:
            print(f"Something gone wrong: {error}")
            
    def just_query(self, queri):
        try:
            self.cursor.execute(query = queri)
            self.connection.commit()
        except Exception as e:
            print(f'Something have went wrong: {e}')        
            
    def fetchall(self):
        return self.cursor.fetchall()
            
class User(DB_Manager):
    def __init__(self, name, subscription):
        super().__init__(self.insert(), self.select(), self.delete(), self.update())
        self.name = name
        self.subscription = subscription
        
    def make_subscription(self):
        self.insert('users', name = self.name, subscription = self.subscription)
        
class Magazine(User):
    def __init__(self, name, description, price, publisher):
        super().__init__(self.insert(), self.select(), self.delete(),self.update(), self.subscription)
        self.name = name
        self.description = description
        self.price = price
        self.publisher = publisher
        
    def make_magazine(self):
        self.insert('magazine', name = self.name, description = self.description, price = self.price, publisher = self.publisher)
        
    def make_release(self, release_name, number_of_releases):
        number_of_releases += 1
        self.insert('release', name = release_name, number_of_release = number_of_releases, magazine = self.subscription)
database = DB_Manager("postgres", "localhost",
                            5432, "postgres", "postgres")
database.connect()

def select_magazine():
    
    magazine_names = database.just_query('select name from magazine')
    magazine_names = database.fetchall()
    magazine_id = database.just_query('select id from magazine')
    magazine_id = database.fetchall()
    magazine_price = database.just_query('select price from magazine')
    magazine_price = database.fetchall()
    for id in magazine_id:
        print(f"{id[0]}.")
    for name in magazine_names:
        print(f'    {name[0]} ')
    for price in magazine_price:
        print(f'    {price[0]}')

while True:
    choice = int(input("1. Create user 2. Create Magazine 3. Add new release : "))
    try:
        match choice:
            case 1:
                name = input("Enter your name: ")
                select_magazine()
                id = int(input("Enter the number of the magazine you would like to subscript to: "))
                user = User(name, id)
                user.make_subscription()
            case 2:
                name = input('Write the name of your magazine: ')
                publisher = input('Write the publisher of this magazine')
                description = input('What is your magazine about? :')
                price = int(input('Enter the price of your magazine: '))
                magazine = Magazine(name, description, price, publisher)
                magazine.make_magazine()
            case 3:
                select_magazine()
                id = int(input('Enter the number of the magazine that your release will be connected to: '))
                release_name = input('Write the name of your release: ')
                number_of_releases = database.just_query(f'select count(number_of_release) as count from release group by name having name = {release_name}')
                magazine_info = database.just_query(f'select name, description, price, publisher from magazine where id = {id}')
                magazine = Magazine(magazine_info[0], magazine_info[1], magazine_info[2], magazine_info[3])
                magazine.make_release(release_name, number_of_releases)
    except Exception as e:
        print('              You might have been made a mistake  or you just want to quit but idc so i just stop the code completely      ')
        print(f'{e}')
        break
            
            