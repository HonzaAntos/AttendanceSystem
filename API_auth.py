import requests


payload={'internalDeviceId':"0001", 'cardNumber':"3300820"}
print("===========>",payload)
authorization = requests.post(
        'https://api-dev-becvary.techcrowd.space/api/terminal/authorization', data=payload)
print("---------------post data---------------")
print(authorization.status_code)
print(authorization.text)
print(authorization.content)
print(authorization.request)
request_dict = authorization.json()
print(request_dict)
print(request_dict['accessToken'])
print("---------------------------------------")
global token
token = request_dict['accessToken']




getUser = requests.get(
"https://api-dev-becvary.techcrowd.space/api/terminal/user",headers={'Authorization':'Bearer {}'.format(token)})
print("---------------get data---------------")
print(getUser.status_code)
print(getUser.text)
request_dict_get = getUser.json()
global user_name
user_firstname = request_dict_get['user']['firstname']
user_lastname = request_dict_get['user']['lastname']
# user_card_logs = request_dict_get['cards.cardLogs']
print(user_firstname,user_lastname)
user_name = user_firstname + " " +user_lastname
print(user_name)

getCardId = requests.get(
        "https://api-dev-becvary.techcrowd.space/api/auth/logged-user",
        headers={'Authorization': 'Bearer {}'.format(token)})
print("---------------get data---------------")
print(getCardId.status_code)
print(getCardId.text)
request_dict_get_logged_user = getCardId.json()
global CardId
CardId = request_dict_get_logged_user['cards']['id']
print("-----------CARD ID FROM LOGGED USER-----------")
print(CardId)
print("----------------------------------------------")



{"id":40,
 "firstname":"Vladim\u00edr",
 "lastname":"\u0160ibrava",
 "email":null,
 "is_verified":true,
 "phone":null,
 "addressStreet":null,
 "addressCity":null,
 "addressPost":null,
 "addressCountry":null,
 "gpsLongitude":null,
 "gpsLatitude":null,
 "avatar":null,
 "gdprAgree":false,
 "newsAgree":false,
 "commentsAgree":false,
 "birthDate":null,
 "aboutMe":null,
 "gender":null,
 "lastLogin":null,
 "webAppEnabled":true,
 "mobileAppEnabled":true,
 "smsEnabled":true,
 "emailEnabled":true,
 "createdAt":"2023-01-05T16:19:38.000000Z","updatedAt":"2023-01-05T16:19:38.000000Z",
 "stripeId":null,
        "roles":[{"id":4,"name":"role.employer","translationName":"Zam\u011bstnanec"}],
        "cards":[{"id":5,"cardNumber":"4533615","userId":40,"createdAt":"2023-01-19T22:01:31.000000Z","updatedAt":"2023-01-19T22:01:31.000000Z",
        "cardLogs":[]}]}


{'id': 40, 'firstname': 'Vladimír', 'lastname': 'Šibrava', 'email': None,
 'is_verified': True, 'phone': None, 'addressStreet': None, 'addressCity': None,
 'addressPost': None, 'addressCountry': None, 'gpsLongitude': None, 'gpsLatitude': None,
 'avatar': None, 'gdprAgree': False, 'newsAgree': False, 'commentsAgree': False,
 'birthDate': None, 'aboutMe': None, 'gender': None, 'lastLogin': None, 'webAppEnabled':
  True, 'mobileAppEnabled': True, 'smsEnabled': True, 'emailEnabled': True,
 'createdAt': '2023-01-05T16:19:38.000000Z', 'updatedAt': '2023-01-05T16:19:38.000000Z',
 'stripeId': None,
 'roles': [{'id': 4, 'name': 'role.employer', 'translationName': 'Zaměstnanec'}],
 'cards': [{'id': 5, 'cardNumber': '4533615', 'userId': 40, 'createdAt': '2023-01-19T22:01:31.000000Z', 'updatedAt': '2023-01-19T22:01:31.000000Z', 'cardLogs': []}]}