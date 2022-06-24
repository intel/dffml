https://www.thethingsnetwork.org/community/portland-or/

```console
$ curl 'https://account.thethingsnetwork.org/api/v2/users' \
  -H 'Accept: application/json' \
  -H 'Accept-Language: en-US,en;q=0.9' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/json;charset=UTF-8' \
  -H 'Cookie: _ga=GA1.2.1356603822.1654447492; _gid=GA1.2.1081437781.1654447492' \
  -H 'Origin: https://account.thethingsnetwork.org' \
  -H 'Referer: https://account.thethingsnetwork.org/register' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  --data-raw '{"email":"name@example.com","username":"name","password":"jsdfjoj38909e3j1"}' \
  --compressed
```

Email validation link: https://account.thethingsnetwork.org/users/emails/validate_email/727252716457186abdecf41ad796b37af9c?email=name%40example.com&recipient=name%40example.com