import mysql.connector, bcrypt, os, binascii, requests, time
from flask import Flask, render_template, request, url_for, flash, redirect, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from PIL import Image
from datetime import datetime
from dotenv import load_dotenv

app = Flask(__name__)

if os.environ.get('FLASK_ENV') == None:
    load_dotenv('.env')

url_site = os.environ.get('URL_SITE')
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER')
mailgun_api_key = os.environ.get('MAILGUN_API_KEY')
mailgun_domain = os.environ.get('MAILGUN_DOMAIN')
app.secret_key = os.environ.get('SECRET_KEY')
db_url = os.environ.get('DATABASE_URL')
db_user = os.environ.get('DATABASE_USER')
db_pwd = os.environ.get('DATABASE_PASS')
db_name = os.environ.get('DATABASE_DB')

with open('mon_fichier.txt', 'w') as fichier:
    fichier.write("Ceci est un exemple de texte.\n")
    fichier.write("'" + db_url + "'\n")

# Configuration de la connexion à la base de données
db_config = {
    'host': db_url,
    'user': db_user,
    'password': db_pwd,
    'database': db_name
}

class User(UserMixin):
    def __init__(self, user_id, name, password, email, verif_token, pass_token, creation_date, last_login, actif, grade):
        self.id = user_id
        self.name = name
        self.password = password
        self.email = email
        self.verif_token = verif_token
        self.pass_token = pass_token
        self.creation_date = creation_date
        self.last_login = last_login
        self.actif = actif
        self.grade = grade

    @staticmethod
    def get(user_id):
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM Users WHERE idUsers = %s"
        values = (user_id,)

        cursor.execute(query, values)
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            return User(
                user_id=user_data['idUsers'],
                name=user_data['name'],
                password=user_data['password'],
                email=user_data['email'],
                verif_token=user_data['verif_token'],
                pass_token=user_data['pass_token'],
                creation_date=user_data['creation_date'],
                last_login=user_data['last_login'],
                actif=user_data['actif'],
                grade=user_data['grade']
            )
        else:
            return None

    @staticmethod
    def find_by_name(name):
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM Users WHERE name = %s"
        values = (name,)

        cursor.execute(query, values)
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            return User(
                user_id=user_data['idUsers'],
                name=user_data['name'],
                password=user_data['password'],
                email=user_data['email'],
                verif_token=user_data['verif_token'],
                pass_token=user_data['pass_token'],
                creation_date=user_data['creation_date'],
                last_login=user_data['last_login'],
                actif=user_data['actif'],
                grade=user_data['grade']
            )
        else:
            return None

    @staticmethod
    def find_by_mail(mail):
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM Users WHERE email = %s"
        values = (mail,)

        cursor.execute(query, values)
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            return User(
                user_id=user_data['idUsers'],
                name=user_data['name'],
                password=user_data['password'],
                email=user_data['email'],
                verif_token=user_data['verif_token'],
                pass_token=user_data['pass_token'],
                creation_date=user_data['creation_date'],
                last_login=user_data['last_login'],
                actif=user_data['actif'],
                grade=user_data['grade']
            )
        else:
            return None

    @staticmethod
    def find_by_pass_token(pass_token):
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM Users WHERE pass_token = %s"
        values = (pass_token,)

        cursor.execute(query, values)
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            return User(
                user_id=user_data['idUsers'],
                name=user_data['name'],
                password=user_data['password'],
                email=user_data['email'],
                verif_token=user_data['verif_token'],
                pass_token=user_data['pass_token'],
                creation_date=user_data['creation_date'],
                last_login=user_data['last_login'],
                actif=user_data['actif'],
                grade=user_data['grade']
            )
        else:
            return None

def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

def get_album(id_album):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM Albums WHERE id_album = %s"
    values = (id_album,)
    cursor.execute(query, values)
    album = cursor.fetchone()
    conn.close()
    if album is None:
        abort(404)
    return album

def get_album_pictures(id_album):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM Pictures WHERE album_id = %s"
    values = (id_album,)

    cursor.execute(query, values)
    album_pitures = cursor.fetchall()
    conn.close()
    return album_pitures

def get_picture_comments(id_picture):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT us.name, com.comment, com.date FROM `Comments` as com JOIN `Users` as us ON us.idUsers = com.user_id WHERE `picture_id`= %s"
    values = (id_picture,)

    cursor.execute(query, values)
    picture_comments = cursor.fetchall()
    conn.close()
    return picture_comments

def get_picture_info(id_picture):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM Pictures WHERE idPictures = %s"
    values = (id_picture,)

    cursor.execute(query, values)
    picture_info = cursor.fetchone()
    conn.close()
    return picture_info

def get_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT `idUsers`,`name`,`email`,`creation_date`,`last_login`,`actif`,`grade` FROM `Users` WHERE 1"

    cursor.execute(query)
    users = cursor.fetchall()
    conn.close()
    if users is None:
        abort(404)
    return users

def exec_query_update_insert(query,values):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, values)
    conn.commit()
    conn.close()

def resize_images(input_dir, output_dir, max_width, max_height):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    files = os.listdir(input_dir)
    for file in files:
        if file.lower().endswith((".jpg", ".jpeg")):
            input_path = os.path.join(input_dir, file)
            output_path = os.path.join(output_dir, file)

            with Image.open(input_path) as image:
                # Redimensionner l'image tout en conservant l'orientation
                image = _resize_image_with_smoothing(image, max_width, max_height)
                image = _rotate_image_by_exif_orientation(image)

                # Enregistrer l'image redimensionnée avec une compression JPEG
                image.save(output_path, "JPEG", optimize=True, quality=85)

def check_token(token):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM Users WHERE verif_token = %s"
    values = (token,)

    cursor.execute(query, values)
    user = cursor.fetchone()
    conn.close()
    if user is None:
        abort(404)
    return user

def clear_token(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "UPDATE `Users` SET `verif_token` = NULL WHERE `Users`.`idUsers` = %s"
    values = (user_id,)
    cursor.execute(query, values)
    conn.commit()
    conn.close()

def found_prev_next_pict(tab, pic_id):
    found_element = None
    i = 0

    # Parcours du tableau pour trouver l'élément ayant l'idPictures recherché
    for element in tab:
        if element['idPictures'] == pic_id:
            found_element = element
            break  # Sortie de la boucle dès que l'élément est trouvé
        i = i + 1

    # Vérification si l'élément a été trouvé ou non
    if found_element is not None:
        if i != 0 and i < len(tab)-1:
            previous_pic = tab[i-1]
            next_pic = tab[i+1]
        if i == 0:
            previous_pic = None
            next_pic = tab[i+1]
        if i == len(tab)-1:
            previous_pic = tab[i-1]
            next_pic = None
        result = [previous_pic, next_pic]
        return result
    else:
        return None

def _resize_image_with_smoothing(image, max_width, max_height):
    # Calculer les dimensions de redimensionnement en conservant le ratio d'aspect
    width, height = image.size
    aspect_ratio = width / height
    new_width = min(width, max_width)
    new_height = min(height, max_height)

    if width > max_width or height > max_height:
        if width > max_width:
            new_height = int(max_width / aspect_ratio)
        else:
            new_width = int(max_height * aspect_ratio)

        # Effectuer le redimensionnement avec lissage
        resized_image = image.resize((new_width, new_height), resample=Image.LANCZOS)
    else:
        resized_image = image.copy()

    return resized_image

def _rotate_image_by_exif_orientation(image):
    # Vérifier l'orientation EXIF de l'image et effectuer une rotation si nécessaire
    exif = image.getexif()
    if exif is not None:
        orientation = exif.get(0x0112)
        if orientation == 3:
            image = image.rotate(180, expand=True)
        elif orientation == 6:
            image = image.rotate(270, expand=True)
        elif orientation == 8:
            image = image.rotate(90, expand=True)
    return image

# Fonction pour envoyer un e-mail
def send_email(to_email, subject, content, nbexe = 0):
    if nbexe < 5:
        response = requests.post(
            f"https://api.mailgun.net/v3/{mailgun_domain}/messages",
            auth=("api", mailgun_api_key),
            data={
                "from": "monablum.brokenarm@gmail.com",
                "to": to_email,
                "subject": subject,
                "html": content
            }
        )
        if response.status_code != 200:
            time.sleep(3)
            nbexe += 1
            send_email(to_email, subject, content, nbexe)
        return True
    else:
        return False

if __name__ == '__main__':
    app.run()

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    print(db_url)
    return User.get(user_id)

@app.route('/')
@login_required
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Exécution d'une requête SELECT pour récupérer toutes les lignes de la table
    query = "SELECT * FROM Albums"
    cursor.execute(query)

    # Récupération des résultats
    albums = cursor.fetchall()
    conn.close()
    return render_template('index.html', albums=albums)

@app.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']

        if not name:
            flash('Un nom est obligatoire pour la création d\'un album !')
        else:
            conn = get_db_connection()
            query = "INSERT INTO Albums (name, description) VALUES (%s, %s)"
            values = (name, description)
            cursor = conn.cursor()
            cursor.execute(query, values)
            new_album_id = cursor.lastrowid
            conn.commit()
            conn.close()
            if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'],str(new_album_id))):
                os.mkdir(os.path.join(app.config['UPLOAD_FOLDER'],str(new_album_id)))
            return redirect(url_for('index'))
    return render_template('create.html')

@app.route('/<int:id_album>')
@login_required
def show_album(id_album):
    global global_curent_album
    album = get_album(id_album)
    album_pictures = get_album_pictures(id_album)
    global_curent_album = album_pictures
    return render_template('album.html',album=album, album_pictures=album_pictures)

@app.route('/<int:id_album>/edit', methods=('GET', 'POST'))
@login_required
def edit_album(id_album):
    album = get_album(id_album)

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        album_picture_id = request.form['album_picture_id']
        if not album_picture_id:
            album_picture_id=0
        
        if not name:
            flash('Un nom pour l\'album est obligatoire')
        else:
            conn = get_db_connection()
            query = "UPDATE Albums SET name = %s, description = %s, album_picture_id = %s WHERE id_album = %s"
            values = (name, description, album_picture_id, id_album)
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()
            conn.close()
            return redirect(url_for('show_album', id_album=id_album))

    return render_template('edit_album.html', album=album)

@app.route('/<int:id_album>/upload', methods=('GET', 'POST'))
@login_required
def upload_pictures(id_album):
    album = get_album(id_album)

    if request.method == 'POST':
        files = request.files.getlist('file')

        if len(files) == 0:
            return "Aucun fichier téléchargé"

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "INSERT INTO Pictures (name,album_id) VALUES (%s, %s)"
        data =[]
        for file in files:
            if file.filename == '':
                return "Un des fichiers a un nom vide"

            if file:
                filename = secure_filename(file.filename)
                data.append((filename, id_album))
                file.save(os.path.join(app.config['UPLOAD_FOLDER'],str(id_album), filename))
        # Redimensionner l'image
        input_dir = os.path.join(app.config['UPLOAD_FOLDER'],str(id_album))
        output_dir = os.path.join(app.config['UPLOAD_FOLDER'],str(id_album),"_resized")
        max_width = 800
        max_height = 600
        resize_images(input_dir, output_dir, max_width, max_height)
        cursor.executemany(query, data)
        conn.commit()
        conn.close()
        return render_template('edit_album.html', album=album)



    return render_template('upload_pictures.html', album=album)

@app.route('/picture/<int:id_picture>', methods=('GET', 'POST'))
@login_required
def show_picture_comments(id_picture):
    if request.method == 'POST':
        user_id = request.form.get('id_user')
        comment = request.form.get('comment')
        album_id = request.form.get('album_id')
        picture_id = request.form.get('picture_id')
        com_date = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

        query = "INSERT INTO Comments (user_id, album_id, picture_id, comment, date) VALUES (%s, %s, %s, %s, %s)"
        values = (user_id, album_id, picture_id, comment, com_date)
        exec_query_update_insert(query,values)

    global global_curent_album
    picture_comments = get_picture_comments(id_picture)
    picture_info = get_picture_info(id_picture)
    pics_info = found_prev_next_pict(global_curent_album, id_picture)

    return render_template('picture.html',picture_comments = picture_comments, picture_info = picture_info, pics_info = pics_info)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        id_user = request.form.get('id_user')
        password = request.form.get('password')
        confirmPassword = request.form.get('confirmPassword')
        mail = request.form.get('mail')
        if password and confirmPassword:
            if password == confirmPassword:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                query = "UPDATE Users SET password = %s WHERE idUsers = %s"
                values = (hashed_password, id_user)
                exec_query_update_insert(query,values)
                change_pwd = True
            else:
                return render_template('dashboard.html', error = "Les mots de passe renseigné ne sont pas identique")

        if mail != current_user.email:
            verif_token = binascii.hexlify(os.urandom(32)).decode('utf-8')
            query = "UPDATE Users SET email = %s, verif_token = %s WHERE idUsers = %s"
            values = (mail, verif_token, id_user)
            exec_query_update_insert(query,values)
            change_mail = True
            subject = "Mail de confirmation pour l'inscription a mon album photo"
            content = f"""<h1>Bienvenue</h1>
            <p>Clique sur le lien ci après pour arctiver ton compte</p>
            <p>Sache qu'un administrateur doit encore valider ton inscription après cette manipulation</p>
            <a href="http://{url_site}/verif/{verif_token}">http://{url_site}/verif/{verif_token}</a>

            <p>A très vite sur mon album photo</p>
            """
            response = send_email(mail, subject, content)
            if not response:
                flash('Le mail de confirmation n\'a pas pue être envoyer merci de contacter l\'administrateur')

        succed = ""
        warning = None
        if change_pwd:
            succed += "Mot de passe changé avec succès<\n>"
        if change_mail:
            succed += "Adresse mail changé avec succès.<\n>"
            warning = "Vous allez recevoir un mail pour valider votre nouvelle adresse mail, tant que cette vérification n'auras pas été effectué vous etes susceptible de ne plus pouvoir accéder a votre compte"
        return render_template('dashboard.html', succed = succed, warning = warning)
    # Vous pouvez ajouter ici le code pour afficher le tableau de bord de l'utilisateur connecté
    return render_template('dashboard.html')  # Afficher le formulaire de connexion

@app.route('/manage_users', methods=['GET', 'POST'])
@login_required
def manage_users():
    if request.method == 'POST':
        id_user = request.form['id_user']
        actif = request.form.get('actif')
        grade = request.form.get('grade')
        if actif:
            actif = 1
        else:
            actif=0
        if grade:
            grade=0
        else:
            grade=1
        conn = get_db_connection()
        query = "UPDATE Users SET actif = %s, grade = %s WHERE idUsers = %s"
        values = (actif, grade, id_user)
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        conn.close()
    users_list = get_users()
    return render_template('manage_users.html',users_list = users_list)

################# routes qui ne nécessite pas d'authentification #################

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Recherche de l'utilisateur par son nom d'utilisateur
        user = User.find_by_name(username)

        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')) and user.actif == 1 and user.verif_token == None:
            current_date = datetime.now()
            formatted_date = current_date.strftime('%d-%m-%Y')
            query = "UPDATE Users SET last_login = %s WHERE idUsers = %s"
            values = (formatted_date, user.id)
            exec_query_update_insert(query, values)
            login_user(user)
            return redirect(url_for('index'))
        else:
            if user:
                if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                    return render_template('login.html', error='Nom d\'utilisateur ou mot de passe incorrect')
                if user.actif != 1:
                    return render_template('login.html', warning='Le compte n\'a pas encore été activé par l\'administrateur')
                if user.verif_token != None:
                    return render_template('login.html', warning='L\'adresse mail renseigné n\'a pas encore été vérifier merci de vérifier vos mail')
            else:
                return render_template('login.html', error='Utilisateur non retrouvé')
    return render_template('login.html')  # Afficher le formulaire de connexion

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        verif_token = binascii.hexlify(os.urandom(32)).decode('utf-8')
        current_date = datetime.now()
        formatted_date = current_date.strftime('%d-%m-%Y')


        # Vérifier si l'utilisateur existe déjà dans la base de données
        existing_user = User.find_by_name(username)
        existing_mail = User.find_by_mail(email)
        if existing_user or existing_mail:
            return render_template('register.html', error='Ce nom d\'utilisateur ou cet adresse mail est déjà utilisé')

        # Hacher le mot de passe avant de l'enregistrer dans la base de données
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Enregistrer le nouvel utilisateur dans la base de données
        query = "INSERT INTO Users (name, password, email, verif_token, creation_date) VALUES (%s, %s, %s, %s, %s)"
        values = (username, hashed_password, email, verif_token, formatted_date)
        exec_query_update_insert(query,values)

        # envoie du mail de confirmation
        # Envoyer un e-mail à l'adresse spécifiée
        subject = "Mail de confirmation pour l'inscription a mon album photo"
        content = f"""<h1>Bienvenue</h1>
        <p>Clique sur le lien ci après pour arctiver ton compte</p>
        <p>Sache qu'un administrateur doit encore valider ton inscription après cette manipulation</p>
        <a href="http://{url_site}/verif/{verif_token}">http://{url_site}/verif/{verif_token}</a>

        <p>A très vite sur mon album photo</p>
        """
        response = send_email(email, subject, content)
        if not response:
            flash('Le mail de confirmation n\'a pas pue être envoyer merci de contacter l\'administrateur')

        # Rediriger vers la page de connexion après l'enregistrement réussi
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/verif/<string:token>')
def verif(token):
    user = check_token(token)
    clear_token(user['idUsers'])
    return redirect(url_for('login'))


@app.route('/ressend_token', methods=['GET', 'POST'])
def ressend_token():
    if request.method == 'POST':
        mail = request.form.get('mail')
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT verif_token FROM Users WHERE email = %s"
        values = (mail,)
        cursor.execute(query, values)
        retour = cursor.fetchone()
        conn.close()
        if retour:
            subject = "Mail de confirmation pour l'inscription a mon album photo"
            content = f"""<h1>Bienvenue</h1>
            <p>Clique sur le lien ci après pour arctiver ton compte</p>
            <p>Sache qu'un administrateur doit encore valider ton inscription après cette manipulation</p>
            <a href="http://{url_site}/verif/{retour['verif_token']}">http://{url_site}/verif/{retour['verif_token']}</a>

            <p>A très vite sur mon album photo</p>
            """
            response = send_email(mail, subject, content)
            if not response:
                flash('Le mail de confirmation n\'a pas pue être envoyer merci de contacter l\'administrateur')

    return render_template('ressend_token.html') 


@app.route('/forget_pass', methods=['GET', 'POST'])
def forget_pass():
    if request.method == 'POST':
        mail = request.form.get('mail')
        if mail:
            user = User.find_by_mail(mail)
            if user:
                pass_token = binascii.hexlify(os.urandom(32)).decode('utf-8')
                query = "UPDATE Users SET pass_token = %s WHERE idUsers = %s"
                values = (pass_token, user.id)
                exec_query_update_insert(query, values)
                subject = "Mail de confirmation pour l'inscription a mon album photo"
                content = f"""<h1>Demande de réinitialisation de mot de passe</h1>
                <p>Clique sur le lien ci après pour arctiver ton compte</p>
                <p>Sache qu'un administrateur doit encore valider ton inscription après cette manipulation</p>
                <a href="http://{url_site}/forget_pass/{pass_token}">http://{url_site}/forget_pass/{pass_token}</a>

                <p>A très vite sur mon album photo</p>
                """
                response = send_email(mail, subject, content)
                if not response:
                    flash('Le mail de confirmation n\'a pas pue être envoyer merci de contacter l\'administrateur')
                return render_template('login.html')
            else:
                error = "Mail non trouvé dans la base de donnée"
        else:
            error = "Aucun mail renseigné dans le formulaire"
        return render_template('forget_pass.html', error = error)
    return render_template('forget_pass.html')

@app.route('/forget_pass/<string:token>', methods=['GET', 'POST'])
def forget_pass_token(token):
    user = User.find_by_pass_token(token)
    if user is None:
        error = "Le token renseigné est incorrect"
        return render_template('forget_pass_modif.html', error = error)
    else:
        if request.method == 'POST':
            password = request.form.get('password')
            confirmPassword = request.form.get('confirmPassword')
            if password and confirmPassword and password == confirmPassword:
                #les champs son renseigné et identique
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                query = "UPDATE `Users` SET `pass_token` = NULL, `password` = %s WHERE `Users`.`idUsers` = %s"
                values = (hashed_password, user.id)
                exec_query_update_insert(query, values)
                success = "Mot de passe modifier avec succès. Vous pouvez a présent vous identifier"
                return render_template('login.html', success = success)
            else:
                error = "Les mot de passe ne correspondent pas où n'ont pas été renseignés"
                return render_template('forget_pass_modif.html', error = error)

        success = "Token valide, vous pouvez procéder a la réinitialisation du mot de passe"
        return render_template('forget_pass_modif.html', success = success)
    return user




