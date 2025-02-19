from flask import Flask,session, render_template, request, redirect,flash,send_file, url_for,send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import tempfile
import logging
import pandas as pd
import os
import sqlite3
import csv
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'
# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'  # Single database for both
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Folder to store uploaded images
app.config['ALLOWED_EXTENSIONS'] = {'png','pdf', 'jpg', 'jpeg', 'gif'}
db = SQLAlchemy(app)

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# ===========================
# Student Details Model
# ===========================

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(200), nullable=True)  # Store the path to the uploaded file
    usn = db.Column(db.String(20), nullable=False)
    dob = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    cetrank = db.Column(db.String(100), nullable=True)
    comedk = db.Column(db.String(100), nullable=True)
    aadhaarnumber = db.Column(db.String(12), nullable=False)
    dayscholar = db.Column(db.String(20), nullable=False)
    branch = db.Column(db.String(100), nullable=False)
    presentaddress = db.Column(db.String(200), nullable=False)
    permanentaddress = db.Column(db.String(200), nullable=False)
    mobilenumber = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), nullable=False)

# ===========================
# Parent Details Model
# ===========================

class Parent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    father_photo = db.Column(db.String(100), nullable=False)
    father_name = db.Column(db.String(100), nullable=False)
    father_occupation = db.Column(db.String(100), nullable=False)
    father_mobile = db.Column(db.String(10), nullable=False)
    father_email = db.Column(db.String(100), nullable=True)
    mother_photo = db.Column(db.String(100), nullable=False)
    mother_name = db.Column(db.String(100), nullable=False)
    mother_occupation = db.Column(db.String(100), nullable=False)
    mother_mobile = db.Column(db.String(10), nullable=False)
    guardian_photo = db.Column(db.String(100), nullable=False)
    guardian_name = db.Column(db.String(100), nullable=False)
    guardian_occupation = db.Column(db.String(100), nullable=False)
    guardian_mobile = db.Column(db.String(10), nullable=False)


class AcademicDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school = db.Column(db.String(200), nullable=False)
    year = db.Column(db.String(4), nullable=False)
    classs = db.Column(db.String(50), nullable=False)
    tenth_file= db.Column(db.String(200), nullable=False)
    college = db.Column(db.String(200), nullable=False)
    passyear = db.Column(db.String(4), nullable=False)
    grade = db.Column(db.String(50), nullable=False)
    puc_file = db.Column(db.String(200), nullable=False)
    hobby = db.Column(db.String(200), nullable=False)
    achieve = db.Column(db.String(200), nullable=False)
    awards_file = db.Column(db.String(200), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

   

# Create the database tables for both models

#============
#login routes
#============
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('optionfield'))
        else:
            flash('Invalid username or password')
            return render_template('login.html', username=username)  # Pass username to template

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Username or email already exists')
            return redirect(url_for('register'))

        new_user = User(username=username, email=email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')
#===================
#option fields
#===================

@app.route('/optionfield')
def optionfield():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('optionfield.html', username=session['username'])

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))



# ===========================
# Student Details Routes
# ===========================

@app.route('/form')
def form():
    return render_template('form.html')  # Student form

@app.route('/submit', methods=['POST'])
def submit_form():
    global filename
    if request.method == 'POST':
        # Get student form data
        name = request.form['name']
        photo = request.files['photo']
        usn = request.form['usn']
        dob = request.form['dob']
        gender = request.form['gender']
        cetrank = request.form['cetrank']
        comedk = request.form['comedk']
        aadhaarnumber = request.form['aadhaarnumber']
        dayscholar = request.form['dayscholar']
        branch = request.form['branch']
        presentaddress = request.form['presentaddress']
        permanentaddress = request.form['permanentaddress']
        mobilenumber = request.form['mobilenumber']
        email = request.form['email']

        # Handle image upload
        photo_path = None
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(photo_path)

        # Save student data to the database
        new_student = Student(
            name=name,
            photo=filename,
            usn=usn,
            dob=dob,
            gender=gender,
            cetrank=cetrank,
            comedk=comedk,
            aadhaarnumber=aadhaarnumber,
            dayscholar=dayscholar,
            branch=branch,
            presentaddress=presentaddress,
            permanentaddress=permanentaddress,
            mobilenumber=mobilenumber,
            email=email,
        )
        db.session.add(new_student)
        db.session.commit()
        flash("Student Details Submitted Successfully")
        return redirect('parentdetails')

@app.route('/display', methods=['GET', 'POST'])
def display():
    search_query = request.args.get('search', '')
    if search_query:
        # Adjust the filter logic based on your database field names
        students = Student.query.filter(Student.name.contains(search_query) | 
                                        Student.usn.contains(search_query) |
                                        Student.branch.contains(search_query)).all()
    else:
        students = Student.query.all()
        flash("Data doesnt Exists")
    return render_template('display.html', students=students, search_query=search_query)

from flask import url_for, redirect

@app.route('/delete/<int:id>')
def delete_student(id):
    student = Student.query.get(id)
    if student:
        print(f"Deleting student with ID {id}")
        if student.photo:
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], student.photo)
            if os.path.exists(photo_path):
                os.remove(photo_path)
                print(f"Deleted photo: {photo_path}")
        db.session.delete(student)
        db.session.commit()
        print(f"Deleted student {student.name}")
    else:
        print(f"Student with ID {id} not found.")
    return redirect(url_for('display'))  # Replace 'display_students' with the correct function name
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_student(id):
    student = Student.query.get(id)
    if request.method == 'POST':
        student.name = request.form['name']
        photo = request.files['photo']
        student.usn = request.form['usn']
        student.dob = request.form['dob']
        student.gender = request.form['gender']
        student.cetrank = request.form['cetrank']
        student.comedk = request.form['comedk']
        student.aadhaarnumber = request.form['aadhaarnumber']
        student.dayscholar = request.form['dayscholar']
        student.branch = request.form['branch']
        student.presentaddress = request.form['presentaddress']
        student.permanentaddress = request.form['permanentaddress']
        student.mobilenumber = request.form['mobilenumber']
        student.email = request.form['email']

        if photo and allowed_file(photo.filename):
            if student.photo:
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], student.photo)
                if os.path.exists(photo_path):
                    os.remove(photo_path)
            filename = secure_filename(photo.filename)
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(photo_path)
            student.photo = filename  

        db.session.commit()
        return redirect(url_for('display'))
    return render_template('update.html', student=student)

logging.basicConfig(level=logging.DEBUG)

@app.route('/download')
def download_all_data():
    try:
        # Create a temporary Excel file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        temp_file.close()  # Close to allow writing

        # Define the models and their names
        tables = {
            'Student': Student,
            'Parent': Parent,
            'AcademicDetails': AcademicDetails
        }
     
        # Use Pandas ExcelWriter to write data to separate sheets
        with pd.ExcelWriter(temp_file.name, engine='xlsxwriter') as writer:
            for sheet_name, model in tables.items():
                # Fetch data from the table
                data = model.query.all()
                logging.debug(f"Fetched data for table {sheet_name}: {data}")

                if not data:
                    logging.warning(f"No data found for table {sheet_name}")
                    continue
                
                # Get the column names (headers)
                headers = [column.name for column in model.__table__.columns]
                logging.debug(f"Headers for table {sheet_name}: {headers}")

                # Convert the data to a list of dictionaries
                data_dicts = [{column: getattr(row, column) for column in headers} for row in data]
                logging.debug(f"Data dicts for table {sheet_name}: {data_dicts}")

                # Create a Pandas DataFrame
                df = pd.DataFrame(data_dicts, columns=headers)

                # Write the DataFrame to a specific sheet
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        # Send the Excel file to the user
        return send_file(temp_file.name, as_attachment=True, download_name="all_data.xlsx")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return f"An error occurred: {e}", 500

# ===========================
# Parent Details Routes
# ===========================

@app.route('/parentdetails', methods=["GET", "POST"])
def parentdetails():
    if request.method == "POST":
        father_photo = request.files['father_photo']
        mother_photo = request.files['mother_photo']
        guardian_photo = request.files['guardian_photo']

        father_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], father_photo.filename)
        mother_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], mother_photo.filename)
        guardian_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], guardian_photo.filename)
        father_photo.save(father_photo_path)
        mother_photo.save(mother_photo_path)
        guardian_photo.save(guardian_photo_path)

        father_name = request.form['father_name']
        father_occupation = request.form['father_occupation']
        father_mobile = request.form['father_mobile']
        father_email = request.form['father_email']
        mother_name = request.form['mother_name']
        mother_occupation = request.form['mother_occupation']
        mother_mobile = request.form['mother_mobile']
        guardian_name = request.form['guardian_name']
        guardian_occupation = request.form['guardian_occupation']
        guardian_mobile = request.form['guardian_mobile']

        new_parent = Parent(
            father_photo=father_photo.filename,
            father_name=father_name,
            father_occupation=father_occupation,
            father_mobile=father_mobile,
            father_email=father_email,
            mother_photo=mother_photo.filename,
            mother_name=mother_name,
            mother_occupation=mother_occupation,
            mother_mobile=mother_mobile,
            guardian_photo=guardian_photo.filename,
            guardian_name=guardian_name,
            guardian_occupation=guardian_occupation,
            guardian_mobile=guardian_mobile
        )

        db.session.add(new_parent)
        db.session.commit()

        return redirect(url_for('acadetails'))

    return render_template("parentdetails.html")

@app.route("/family")
def family():
    search_query = request.args.get('search', '')  # Get the search query from URL
    if search_query:
        # Filter parents based on the search query
        parents = Parent.query.filter(
            (Parent.father_name.ilike(f"%{search_query}%")) | 
            (Parent.mother_name.ilike(f"%{search_query}%")) | 
            (Parent.guardian_name.ilike(f"%{search_query}%"))
        ).all()
    else:
        parents = Parent.query.all()
    return render_template("family.html", parents=parents, search_query=search_query)

@app.route("/update_parent/<int:id>", methods=["GET", "POST"])
def update_parent(id):
    parent = Parent.query.get_or_404(id)
    if request.method == "POST":
        parent.father_name = request.form['father_name']
        parent.father_occupation = request.form['father_occupation']
        parent.father_mobile = request.form['father_mobile']
        parent.father_email = request.form['father_email']
        parent.mother_name = request.form['mother_name']
        parent.mother_occupation = request.form['mother_occupation']
        parent.mother_mobile = request.form['mother_mobile']
        parent.guardian_name = request.form['guardian_name']
        parent.guardian_occupation = request.form['guardian_occupation']
        parent.guardian_mobile = request.form['guardian_mobile']

        # Handle file uploads for photos if changed
        father_photo = request.files['father_photo']
        mother_photo = request.files['mother_photo']
        guardian_photo = request.files['guardian_photo']

        if father_photo and allowed_file(father_photo.filename):
            father_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], father_photo.filename)
            father_photo.save(father_photo_path)
            parent.father_photo = father_photo.filename

        if mother_photo and allowed_file(mother_photo.filename):
            mother_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], mother_photo.filename)
            mother_photo.save(mother_photo_path)
            parent.mother_photo = mother_photo.filename

        if guardian_photo and allowed_file(guardian_photo.filename):
            guardian_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], guardian_photo.filename)
            guardian_photo.save(guardian_photo_path)
            parent.guardian_photo = guardian_photo.filename

        db.session.commit()
        return redirect(url_for('family'))
    
    return render_template("update_parent.html", parent=parent)


@app.route("/delete_parent/<int:id>")
def delete_parent(id):
    parent = Parent.query.get(id)
    if parent:
        # Remove photos from the file system
        father_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], parent.father_photo)
        mother_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], parent.mother_photo)
        guardian_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], parent.guardian_photo)

        for photo_path in [father_photo_path, mother_photo_path, guardian_photo_path]:
            if os.path.exists(photo_path):
                os.remove(photo_path)

        # Delete the parent record from the database
        db.session.delete(parent)
        db.session.commit()

    return redirect(url_for('family'))

#=========================================
#academic details route
#=========================================
@app.route('/acadetails', methods=['GET', 'POST'])
def acadetails():
    if request.method == 'POST':
        # Retrieve form data
        school = request.form['school']
        year = request.form['year']
        classs = request.form['classs']
        college = request.form['college']
        passyear = request.form['passyear']
        grade = request.form['grade']
        hobby = request.form.get('hobby', '')
        achieve = request.form.get('achieve', '')

        # Handle file uploads
        files = {}
        for key in ['tenth_file', 'puc_file', 'awards_file']:
            file = request.files.get(key)
            if file and allowed_file(file.filename):
                filename = file.filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace("\\", "/")
                file.save(file_path)
                files[key] = filename  # Save only the filename, not the full path
            else:
                files[key] = None

        # Create a new AcademicDetails entry
        new_entry = AcademicDetails(
            school=school,
            year=year,
            classs=classs,
            college=college,
            passyear=passyear,
            grade=grade,
            hobby=hobby,
            achieve=achieve,
            tenth_file=files.get('tenth_file'),
            puc_file=files.get('puc_file'),
            awards_file=files.get('awards_file')
        )

        # Add the new entry to the database
        db.session.add(new_entry)
        db.session.commit()

        return redirect(url_for('optionfield'))
    return render_template("acadetails.html")


@app.route('/acadisplay', methods=['GET', 'POST'])
def acadisplay():
    if request.method == 'POST':
        search_query = request.form.get('search', '').strip()
        # Filter records based on the search query
        records = AcademicDetails.query.filter(
            (AcademicDetails.school.ilike(f'%{search_query}%')) |
            (AcademicDetails.college.ilike(f'%{search_query}%')) |
            (AcademicDetails.hobby.ilike(f'%{search_query}%'))
        ).all()
    else:
        # Fetch all records if no search query
        records = AcademicDetails.query.all()

    return render_template('acadisplay.html', records=records)


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    # Serve uploaded files by passing the filename, no need for extra "/uploads/"
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/update_record/<int:id>', methods=['GET', 'POST'])
def update_record(id):
    record = AcademicDetails.query.get_or_404(id)

    if request.method == 'POST':
        # Update fields from form data
        record.school = request.form.get('school', record.school)
        record.year = request.form.get('year', record.year)
        record.classs = request.form.get('classs', record.classs)
        record.college = request.form.get('college', record.college)
        record.passyear = request.form.get('passyear', record.passyear)
        record.grade = request.form.get('grade', record.grade)
        record.hobby = request.form.get('hobby', record.hobby)
        record.achieve = request.form.get('achieve', record.achieve)

        # Handle file uploads if updated
        for key, field in [('tenth_file', 'tenth_file'), 
                           ('puc_file', 'puc_file'), 
                           ('awards_file', 'awards_file')]:
            file = request.files.get(key)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)  # Secure the filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)  # Save the file to the uploads folder
                setattr(record, field, filename)  # Update the record field with the filename

        # Save changes to the database
        try:
            db.session.commit()
            flash("Record updated successfully!", "success")
            return redirect(url_for('acadisplay'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "danger")
            return redirect(request.url)

    # Render the update form with the current record
    return render_template('acaupdate.html', record=record)

@app.route('/delete_record/<int:id>')
def delete_record(id):
    # Find the record by ID
    record = AcademicDetails.query.get_or_404(id)

    # Delete associated files from the filesystem
    for key in ['tenth_file', 'puc_file', 'awards_file']:
        file_path = getattr(record, key)
        if file_path and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], file_path)):
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file_path))

    # Delete the record from the database
    db.session.delete(record)
    db.session.commit()
    return redirect(url_for('acadisplay'))

if __name__ == "__main__":
    with app.app_context():
       db.create_all()
       app.run(host='0.0.0.0',port=5000,debug=True)
#===============================
#view details route
#===============================
