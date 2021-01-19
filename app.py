import requests
from flask import Flask, render_template,url_for,request,redirect,flash
from flask_mysqldb import MySQL


app=Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['DEBUG']=True
app.config['TEMPLATE_AUTO_RELOAD '] = True

app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = 'weather'

database = MySQL(app)


#Get data from Database
@app.route('/')
def index():
    url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&APPID=5662ee1bf090bd1e53240c815e2402ee"
    cur = database.connection.cursor()
    cur.execute("SELECT * FROM city ORDER BY id DESC")
    all_data = cur.fetchall()
    database.connection.commit()

    weather_data=[]
    for city in all_data:
        address = city[1]
        print(city)
        r = requests.get(url.format(address)).json()

        weather ={
            'city' : address,
            'tempature' : r['main']['temp'],
            'description': r['weather'] [0] ['description'],
            'icon': r['weather'][0]['icon'],
        }
        weather_data.append(weather)

    return render_template('index.html', weather_data=weather_data)


# For Add City
@app.route('/submit_form', methods=['POST'])
def add_city():
    if request.method=='POST':
        city = request.form['city']
        if city:
            cur = database.connection.cursor()
            cur.execute('SELECT city_name FROM city WHERE city_name=%s',[city])
            existance = cur.fetchone()

            if not existance:
                url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&APPID=5662ee1bf090bd1e53240c815e2402ee"
                new_city = requests.get(url.format(city)).json()
                if new_city['cod']==200:
                    cur.execute('INSERT INTO city (city_name) VALUES (%s)',[city])
                    database.connection.commit()
                    flash('"{}"City added to the list.'.format(city))

                else:
                    flash('"{}" City is not exist in the World.'.format(city))
            else:
                flash('"{}" City is already exist here.'.format(city))

    return redirect('/')

#Delete any city by city name.
@app.route('/delete/<string:city_name>')
def delete_city(city_name):
    cur=database.connection.cursor()
    cur.execute('DELETE FROM city WHERE city_name=%s',[city_name])
    database.connection.commit()
    flash('"{}" City removed from here, Successfully.'.format(city_name))
    return redirect('/')


if __name__ == '__main__':
    app.run()