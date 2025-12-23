python -m venv .venv  

.\.venv\Scripts\activate


pip install -r .\requirements.txt   
python -m spacy download en_core_web_sm

Need to add hugging face api token HF_TOKEN in .env file


python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser


python manage.py runserver          

