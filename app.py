from flask import Flask, render_template, request, redirect, url_for
import json, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
DATA_FILE = "rentals.json"
IMG_FOLDER = "static/images"
os.makedirs(IMG_FOLDER, exist_ok=True)

COMPANY = "Makuchete Developers"
EMAIL = "tinotendatarshmakuchete@gmail.com"

def load_data():
    if not os.path.exists(DATA_FILE): return []
    try:
        with open(DATA_FILE, 'r') as f: return json.load(f)
    except: return []

def save_data(d):
    with open(DATA_FILE, 'w') as f: json.dump(d, f, indent=2)

@app.route('/')
def home():
    houses = [h for h in load_data() if h.get('status','Available')=='Available']
    q = request.args.get('location','').lower()
    maxp = request.args.get('price','')
    if q: houses = [h for h in houses if q in h['location'].lower()]
    if maxp.isdigit(): houses = [h for h in houses if h['price'] <= int(maxp)]
    return render_template('index.html', houses=houses, company=COMPANY, email=EMAIL)

@app.route('/landlord', methods=['GET','POST'])
def landlord():
    if request.method=='POST':
        data=load_data()
        file = request.files.get('photo')
        img_name = "no_image.jpg"
        if file and file.filename:
            fname = secure_filename(file.filename)
            img_name = f"house_{len(data)+1}_{fname}"
            file.save(os.path.join(IMG_FOLDER, img_name))
        new_house={
            "id": len(data)+1,
            "location": request.form['location'],
            "price": int(request.form['price']),
            "rooms": request.form['rooms'],
            "phone": request.form['phone'],
            "amenities": request.form['amenities'],
            "image": img_name,
            "status": "Available"
        }
        data.append(new_house)
        save_data(data)
        return redirect(url_for('landlord'))
    return render_template('landlord.html', houses=load_data(), company=COMPANY, email=EMAIL)

@app.route('/toggle/<int:house_id>')
def toggle(house_id):
    data=load_data()
    for h in data:
        if h['id']==house_id:
            h['status'] = "Taken" if h['status']=="Available" else "Available"
    save_data(data)
    return redirect(url_for('landlord'))

if __name__=='__main__':
    app.run(host='0.0.0.0',port=10000)