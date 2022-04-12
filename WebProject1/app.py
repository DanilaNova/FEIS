import os
from flask import Flask
from flask import send_file

app = Flask(__name__)
rootPath = ""

def setRootPath():
    rootPath = ""
    while(rootPath == ""):
        print("Type in root path:")
        path = os.path.abspath(input())
        if(len(path) <= 64 & os.path.isdir(path)):
            if(len(path) > 64):
                print("Warning: root path length is bigger than 64, are you sure you want to use it (Y/N)?\nPath: "+path)
                if(input().upper() == 'Y'):
                    rootPath = path
            elif(~os.path.isdir(path)):
                if(os.path.exists(path) & os.path.isfile(path)):
                    print("Warning: root path is reffering to a file, do you want to create new path(Y/N)?\nPath: "+path)
                else:
                    print("Warning: root path folder doesn't exists, do you want to create it(Y/N)?\nPath: "+path)
                if(input().upper() == 'Y'):
                    os.makedirs(rootPath)
                    rootPath = path
        else:
            rootPath = path
    with open('rootPath.txt', 'w') as file:
        file.write(rootPath)

if(os.path.isfile('rootPath.txt')):
    with open('rootPath.txt', 'r') as file:
        rootPath = os.path.abspath(file.read())

    if(len(rootPath) <= 64 & os.path.isdir(rootPath)):
        if(len(rootPath) > 64):
            print("Warning: root path length is bigger than 64, are you sure you want to use it (Y/N)?\nPath: "+rootPath)
            if(input().upper() != 'Y'):
                setRootPath()
        elif(~os.path.isdir(rootPath)):
            if(os.path.exists(rootPath) & os.path.isfile(rootPath)):
                print("Warning: root path is reffering to a file, do you want to create new path(Y/N)?\nPath: "+rootPath)
            else:
                print("Warning: root path folder doesn't exists, do you want to create it(Y/N)?\nPath: "+rootPath)
            if(input().upper() == 'Y'):
                os.makedirs(rootPath)
            else:
                setRootPath()
else:
    setRootPath()

app.static_folder = rootPath

@app.route("/<path:dir>/")
def page3(dir):
    page = '<title>Files</title>'
    path = os.path.join(rootPath, dir)
    if('..' in dir):
        page += '<h1>Safety error</h1>'
        page += '<p>Path cannot contain parent directory symbol(..)</p>'
    elif(os.path.isdir(path)):
        page += f'<h2>/{dir}</h2>'
        page += '<ul><li><a href="..">..</a></li>'
        for element in os.listdir(path):
            page += f'<li><a href="{element}">{element}</a></li>'
        page += '</ul>'
    elif(os.path.isfile(path)):
        page += f'<h2>/{dir}</h2>'
        page += '<p><a href="..">..</a></p>'
        if(path.endswith(".jpg")):
            page += f'<img src="/static/{dir}">'
        else:
            page += f'<a href="/static/{dir}" download>download</a>'
    else:
        page += '<h1>ERROR 404</h1>'
        page += f'<p>"/{dir}" does not exists</p>'
    return page

@app.route('/')
def page2():
    page = '<title>Files</title>'
    page += '<h2>/</h2>'
    page += '<ul>'
    print(os.listdir(rootPath))
    for element in os.listdir(rootPath):
        page += f'<li><a href="{element}">{element}<a></li>'
    page += '</ul>'
    return page

if __name__ == '__main__':
    app.run('localhost', 80)