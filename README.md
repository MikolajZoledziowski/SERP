# SERP

Wymagania frontend:
zainstalowany node.js oraz npm
Po pobraniu kodów w folderze frontend/serp uruchamiamy komende npm install. 
Po pomyślnym zainstalowaniu uruchamiamy server poleceniem npm run dev.
Domyślnie serwer wystartuje na porcie 8080, jeśli będzie zajęty wystartuje na innym wolnym.

Wymagania backend:
W folerze /backend komendą pip install -r requirements.txt instalujemy wymagane pakiety.
Uruchamiamy serwere poleceniem python manage.py runsever.
Serwer uruchomi się na porcie 8000, jeżeli zostanie uruchomiony na innym porcie należy ten port podać
w pliku frontend/serp/config/index.js w dev: proxyTable.

Baza danych to PostgreSQL

W pliku settings.py w zmiennej TIME_LIMIT ustawiany jest limit czasowy poniżej którego temu samemu użytkownikowi
na to samo zapytanie zwracany jest wynik z bazy. Limit podawany jest w sekundach.
W zmiennej LOG_FILENAME podawana jest ścieżka do plików z logami.

Jeśli przeglądarka nie będzie działać a w pliku z logami pojawi się informacja o przekroczonym dziennym limicie 
można użyć drugiej wersji. W tym celu należy odkomentować linię 69 w core/views.py a zakomentować 70.
