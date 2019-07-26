import requests
import json
import datetime
import logging
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings

from collections import Counter
from .models import Query, QueryResult



@csrf_exempt
def get_links(request):
    """Funkcja przyjmuje frazę i zwraca 10 linków, 10 najczęśćiej występujacych słów
    oraz liczbę wyników. Jeśli użytkownik poda tą samą frazę w czasie mniejszym niż
    podano w settings.TIME_LIMIT funkcja zwróci wynik z bazy
    
    Arguments:
        request(HTTPRequest): {"query": fraza która ma zostać wyszukana}
    
    Returns:
        (JsonResponse): {items(List): lista linków, 
            most_occur(List): lista najczęściej występujacych słów, 
            total_results(Int): liczba wyników}
    """

    logging.basicConfig(filename=settings.LOG_FILENAME, level=logging.DEBUG)
    try:        
        query = request.POST.get('query')
    except KeyError:    
        logging.exception('nie podano wymaganego parametru')
        return JsonResponse({"message": "nie podano wymaganego parametru"}, status=400, safe=False)
    except:
        logging.exception('nieznany błąd podczas pobierania frazy')
        return JsonResponse({"message": "nieznany błąd"}, status=500, safe=False)

    ip = get_client_ip(request)
    data = {"items": [], "most_occur": []}

    try:
        same_query = Query.objects.filter(query=query, ip=ip).order_by('id')
    except:
        logging.exception('nieznany błąd podczas sprawdzania czy dany użytkownik wykonał takie zapytanie')
        return JsonResponse({"message": "nieznany błąd"}, status=500, safe=False)

    if same_query:
        last_query = same_query.last()
        if check_data(last_query.date):
            # To samo zapytanie oraz limit czasowy nie został przekroczony
            try:
                query_result = QueryResult.objects.filter(query = last_query).order_by('ordinal_number')
            except:
                logging.exception('nieznany błąd podczas pobierania danych do zapytania z bazy')
                return JsonResponse({"message": "nieznany błąd"}, status=500, safe=False)
            
            data['total_results'] = last_query.total_result
            for item in query_result:
                data['items'].append(item.link)
                data['most_occur'].append(item.word)
            return JsonResponse(data, safe=False)
    #  Inne zapytanie lub limit czasowy został przekroczony
    payload = {'q': query, 'cx': settings.CX,
    'key': settings.KEY}
    try:
        # W razie przekroczenia dziennego limitu (100) można użyć drugiej wersji
        # r = requests.get("https://www.googleapis.com/customsearch/v1/siterestrict", params=payload)
        r = requests.get("https://www.googleapis.com/customsearch/v1", params=payload)
        response =  json.loads(r.text)
        logging.debug(response)
        data['total_results'] = int(response['queries']['request'][0]['totalResults'])

        words_tmp = ''
        for item in response['items']:
            data['items'].append(item['link'])
            words_tmp+= item['title'] + ' '
            words_tmp+= item['snippet'] + ' '
    except KeyError:
        logging.exception('silnik przeglądarki zwrócił błąd')
        return JsonResponse({"message": "silnik przeglądarki zwrócił błąd"}, status=500, safe=False)
    except:
        logging.exception('silnik przeglądarki zwrócił błąd')
        return JsonResponse({"message": "nieznany błąd"}, status=500, safe=False)

    words = words_tmp.split()
    Count = Counter(words)
    most_occur = Count.most_common(10)
    for word in most_occur:
        data['most_occur'].append(word[0])
    try:
        data_query = Query()
        data_query.query = query
        data_query.ip = ip
        data_query.total_result = data['total_results']
        data_query.save()

        for x in range(10):
            QueryResult.objects.create(
                query=data_query,
                word=data['most_occur'][x],
                link=data['items'][x],
                ordinal_number=x+1
            )
    except:
        logging.exception('błąd podczas zapisu wyniku zapytania do bazy')
        return JsonResponse({"message": "nieznany błąd"}, status=500, safe=False)       

    return JsonResponse(data, safe=False)


def get_client_ip(request):
    """Funkcja zwraca ip użytkownika
    
    Arguments:
        request(HTTPRequest) 
    
    Returns:
        (String): ip użytkownika 
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def check_data(time):
    """Funkcja spawdza czy czas podany jako argument plus limit czasowy 
    jest mniejszy od aktualnego czasu 
    
    Arguments:
        time (Datetime)
    
    Returns:
        (Bool): True jeśli czas podany w argumencie plus limit czasowy 
        jest większy od aktualnego czasu w przeciwnym wypadku False
    """
    time_now = datetime.datetime.now()
    return (time + datetime.timedelta(seconds=settings.TIME_LIMIT)) > time_now
