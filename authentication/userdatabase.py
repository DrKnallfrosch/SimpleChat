from typing import Tuple
import mariadb
import docker
import time

class UserDatabase:
    def __init__(self, database: str = 'USER'):
        self.database = database
        self.__startup()
        self.conn = mariadb.connect(
            host="localhost",
            user='root',
            password='12345',
            port=3304)
        self.cursor = self.conn.cursor()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.container.stop()

    def __startup(self):
        self.client = docker.from_env()
        exist = False
        containerlist = []

        for container in self.client.containers.list(all=True):
            containerlist.append(container.name)
            if "mariadb-simplechat" in container.name:
                if container.status == "running":
                    break
                elif container.status == "exited":
                    container.start(); time.sleep(6)
                    break
        if "mariadb-simplechat" in containerlist:
            exist = True

        if not exist:
            self.container = self.client.containers.run(
                "mariadb:latest",
                name="mariadb-simplechat",
                environment={
                    "MYSQL_USER": "root",
                    "MYSQL_ROOT_PASSWORD": "12345"},
                network="bridge",
                ports={"3306/tcp": 3304},
                detach=True)
            time.sleep(6)
        self.container = self.client.containers.get("mariadb-simplechat")

    def open(self, table_name: str = "users", columns: Tuple = ("username text", "password varchar(64)")):
        self.cursor.execute("CREATE DATABASE IF NOT EXISTS %s;" % self.database)
        self.cursor.execute("USE %s;" % self.database)
        self.cursor.execute("CREATE TABLE IF NOT EXISTS %s (id int auto_increment not null primary key);" % table_name)
        for column in columns:
            self.cursor.execute("ALTER TABLE %s ADD IF COLUMN NOT EXISTS %s;" % (table_name, column))

    def close(self):
        self.cursor.close()
        self.conn.close()
        self.container.stop()
        self.container.close()

if __name__ == "__main__":
    with UserDatabase() as db:
        db.open()
