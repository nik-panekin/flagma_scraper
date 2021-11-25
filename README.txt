Written with Python 3.8.10

The script scrapes https://flagma.ua/ site. It collects contact data for
each company from the specified category. The results are saved to a CSV file.

The scraping process requires dynamic IP change, for the site has anti-scrape
protection (IP ban). Therefore the script uses free TOR proxy. In order to
make things working the TOR Windows Expert Bundle should be downloaded and
installed from here:

https://www.torproject.org/download/tor/

And then the constant TOR_EXECUTABLE_PATH in ./utils/tor_proxy.py should be
modified accordingly.

How to use:
    python flagma_scraper.py

Feel free to use and modify it as needed.

For dependencies refer to requirements.txt.

Данный скрипт выполняет парсинг сайта https://flagma.ua/. Осуществляется сбор
контактной информации для всех компаний из заданной категории. Результат
сохраняется в файл CSV.

Процесс парсинга требует динамическую смену IP, поскольку сайт имеет защиту от
ботов (бан по IP при большом количестве запросов). Так что данный скрипт
использует свободные прокси-сервера сети TOR. Поэтому для корректной работы
скрипта необходимо установить TOR Windows Expert Bundle отсюда:

https://www.torproject.org/download/tor/

А затем соответствующим образом отредактировать константу TOR_EXECUTABLE_PATH
в файле ./utils/tor_proxy.py.

Формат запуска:
    python flagma_scraper.py

Используйте и/или модифицируйте данный программный код без ограничений.

Зависимости скрипта перечислены в файле requirements.txt.
