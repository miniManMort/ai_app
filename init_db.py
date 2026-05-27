from models import init_db


if __name__ == '__main__':
    init_db(seed=True)
    print('Initialized users.db with sample users: alice, bob')
