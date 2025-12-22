from app.app import create_app

app = create_app('desenvolvimento')

if __name__ == '__main__':
    app.run()
