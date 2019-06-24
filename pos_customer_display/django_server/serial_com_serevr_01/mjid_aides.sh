// install python2.7 sur windows et ajouter le path sur Variable envir (et pip aussi)
pip install django==1.11.21
pip install django-cors-headers
//settings.py
//INSTALLED_APPS = (
//    ...
//   'corsheaders',
//    ...
//)


//----------
python manage.py runserver