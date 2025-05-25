from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
import os
from datetime import datetime, date, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///personel.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))

class Personel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(100), nullable=False)
    soyad = db.Column(db.String(100), nullable=False)
    pozisyon = db.Column(db.String(100), nullable=False)
    maas = db.Column(db.Float, nullable=False)
    baslangic_tarihi = db.Column(db.Date, nullable=False)
    durum = db.Column(db.String(20), nullable=False)

class Giris(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    personel_id = db.Column(db.Integer, db.ForeignKey('personel.id'), nullable=False)
    giris_zamani = db.Column(db.DateTime, nullable=False)
    cikis_zamani = db.Column(db.DateTime, nullable=True)
    personel = db.relationship('Personel', backref=db.backref('girisler', lazy=True))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Kullanıcı adı veya şifre hatalı!', 'danger')
    return render_template('login.html')

@app.route('/kayit', methods=['GET', 'POST'])
def kayit():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password2 = request.form['password2']
        if password != password2:
            flash('Şifreler eşleşmiyor!', 'danger')
            return render_template('kayit.html')
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed_pw, first_name=first_name, last_name=last_name)
        try:
            db.session.add(user)
            db.session.commit()
            flash('Kayıt başarılı! Giriş yapabilirsiniz.', 'success')
            return redirect(url_for('login'))
        except:
            flash('Bu kullanıcı adı veya e-posta zaten kayıtlı!', 'danger')
    return render_template('kayit.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    toplam_personel = Personel.query.count()
    aktif_personel = Personel.query.filter_by(durum='Aktif').count()
    ortalama_maas = Personel.query.with_entities(db.func.avg(Personel.maas)).scalar() or 0
    ortalama_maas = f'{ortalama_maas:.2f}'
    son_personeller = Personel.query.order_by(Personel.id.desc()).limit(5).all()
    return render_template('dashboard.html', toplam_personel=toplam_personel, aktif_personel=aktif_personel, ortalama_maas=ortalama_maas, son_personeller=son_personeller)

@app.route('/personel', methods=['GET'])
@login_required
def personel():
    arama = request.args.get('arama', '')
    pozisyon = request.args.get('pozisyon', '')
    sorgu = Personel.query
    if arama:
        sorgu = sorgu.filter((Personel.ad.ilike(f'%{arama}%')) | (Personel.soyad.ilike(f'%{arama}%')))
    if pozisyon and pozisyon != 'Tüm Pozisyonlar':
        sorgu = sorgu.filter_by(pozisyon=pozisyon)
    personeller = sorgu.order_by(Personel.id.desc()).all()
    return render_template('personel.html', personeller=personeller, arama=arama, pozisyon=pozisyon)

@app.route('/personel/ekle', methods=['GET', 'POST'])
@login_required
def personel_ekle():
    if request.method == 'POST':
        ad = request.form['ad']
        soyad = request.form['soyad']
        pozisyon = request.form['pozisyon']
        maas = request.form['maas']
        baslangic_tarihi = request.form['baslangic_tarihi']
        durum = request.form['durum']
        yeni_personel = Personel(
            ad=ad,
            soyad=soyad,
            pozisyon=pozisyon,
            maas=float(maas),
            baslangic_tarihi=datetime.strptime(baslangic_tarihi, '%Y-%m-%d'),
            durum=durum
        )
        db.session.add(yeni_personel)
        db.session.commit()
        flash('Personel başarıyla eklendi!', 'success')
        return redirect(url_for('personel'))
    return render_template('personel_ekle.html')

@app.route('/personel/duzenle/<int:id>', methods=['GET', 'POST'])
@login_required
def personel_duzenle(id):
    personel = Personel.query.get_or_404(id)
    if request.method == 'POST':
        personel.ad = request.form['ad']
        personel.soyad = request.form['soyad']
        personel.pozisyon = request.form['pozisyon']
        personel.maas = float(request.form['maas'])
        personel.baslangic_tarihi = datetime.strptime(request.form['baslangic_tarihi'], '%Y-%m-%d')
        personel.durum = request.form['durum']
        db.session.commit()
        flash('Personel bilgileri güncellendi!', 'success')
        return redirect(url_for('personel'))
    return render_template('personel_duzenle.html', personel=personel)

@app.route('/personel/sil/<int:id>', methods=['POST'])
@login_required
def personel_sil(id):
    personel = Personel.query.get_or_404(id)
    db.session.delete(personel)
    db.session.commit()
    flash('Personel silindi!', 'success')
    return redirect(url_for('personel'))

@app.route('/personel/giris-cikis')
@login_required
def personel_giris_cikis():
    girisler = Giris.query.order_by(Giris.giris_zamani.desc()).all()
    toplam_personel = Personel.query.count()
    giris_yapan = Giris.query.filter(Giris.giris_zamani != None).count()
    cikis_yapan = Giris.query.filter(Giris.cikis_zamani != None).count()
    # Ortalama süre hesaplama
    sureler = [((g.cikis_zamani - g.giris_zamani).total_seconds() / 60) for g in girisler if g.cikis_zamani]
    if sureler:
        ortalama_sure = f"{int(sum(sureler)//len(sureler)//60)} saat {int(sum(sureler)//len(sureler)%60)} dakika"
    else:
        ortalama_sure = "-"
    return render_template('personel_giris_cikis.html', girisler=girisler, toplam_personel=toplam_personel, giris_yapan=giris_yapan, cikis_yapan=cikis_yapan, ortalama_sure=ortalama_sure)

@app.route('/raporlar')
@login_required
def raporlar():
    # Pozisyon dağılımı
    pozisyonlar = db.session.query(Personel.pozisyon, db.func.count(Personel.id)).group_by(Personel.pozisyon).all()
    pozisyon_labels = [p[0] for p in pozisyonlar]
    pozisyon_counts = [p[1] for p in pozisyonlar]

    # Maaş dağılımı
    maas_araliklari = ['< 10000', '10000 - 15000', '> 15000']
    maas_counts = [
        Personel.query.filter(Personel.maas < 10000).count(),
        Personel.query.filter(Personel.maas >= 10000, Personel.maas <= 15000).count(),
        Personel.query.filter(Personel.maas > 15000).count()
    ]

    # Son 6 ayda işe başlayanlar (ay bazında)
    aylar = []
    ay_sayilari = []
    bugun = datetime.today().replace(day=1)
    for i in range(5, -1, -1):
        ay = (bugun - timedelta(days=30*i)).replace(day=1)
        ay_str = ay.strftime('%B %Y')
        aylar.append(ay_str)
        ay_sayilari.append(Personel.query.filter(
            db.extract('year', Personel.baslangic_tarihi) == ay.year,
            db.extract('month', Personel.baslangic_tarihi) == ay.month
        ).count())

    # Pozisyona göre maaş raporu
    maas_raporu = db.session.query(
        Personel.pozisyon,
        db.func.avg(Personel.maas),
        db.func.min(Personel.maas),
        db.func.max(Personel.maas),
        db.func.count(Personel.id)
    ).group_by(Personel.pozisyon).all()

    return render_template(
        'raporlar.html',
        pozisyon_labels=pozisyon_labels,
        pozisyon_counts=pozisyon_counts,
        maas_araliklari=maas_araliklari,
        maas_counts=maas_counts,
        aylar=aylar,
        ay_sayilari=ay_sayilari,
        maas_raporu=maas_raporu
    )

@app.route('/personel/giris-ekle', methods=['GET', 'POST'])
@login_required
def giris_ekle():
    personeller = Personel.query.order_by(Personel.ad, Personel.soyad).all()
    if request.method == 'POST':
        personel_id = request.form['personel_id']
        giris_zamani = request.form['giris_zamani']
        giris_dt = datetime.strptime(giris_zamani, '%Y-%m-%dT%H:%M')
        yeni_giris = Giris(personel_id=personel_id, giris_zamani=giris_dt)
        db.session.add(yeni_giris)
        db.session.commit()
        flash('Giriş kaydı eklendi!', 'success')
        return redirect(url_for('personel_giris_cikis'))
    return render_template('giris_ekle.html', personeller=personeller)

@app.route('/personel/cikis-ekle', methods=['GET', 'POST'])
@login_required
def cikis_ekle():
    # Sadece çıkışı olmayan girişler listelensin
    girisler = Giris.query.filter_by(cikis_zamani=None).all()
    if request.method == 'POST':
        giris_id = request.form['giris_id']
        cikis_zamani = request.form['cikis_zamani']
        cikis_dt = datetime.strptime(cikis_zamani, '%Y-%m-%dT%H:%M')
        giris = Giris.query.get(giris_id)
        giris.cikis_zamani = cikis_dt
        db.session.commit()
        flash('Çıkış kaydı eklendi!', 'success')
        return redirect(url_for('personel_giris_cikis'))
    return render_template('cikis_ekle.html', girisler=girisler)

#if __name__ == '__main__':
 #   if not os.path.exists('personel.db'):
 #       with app.app_context():
  #          db.create_all()
 #   app.run(debug=True) 
import os
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
