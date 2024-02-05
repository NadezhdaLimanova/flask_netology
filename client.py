import requests
#
#
response = requests.post(
    "http://127.0.0.1:5000/user",
    json={
        "name": "J3",
        "email": "jh@exame1.com",
        "password": "sejggggj",
    },
)
print(response.status_code)
print(response.text)
# #
with open('token.txt', 'r') as file:
    token = file.read().strip()
headers = {'Authorization': token}

# response = requests.post(
#     "http://127.0.0.1:5000/login",
#     json={
#         "name": "J3",
#         "email": "jh@exame1.com",
#         "password": "sejggggj",
#     },
# )
# print(response.status_code)
# print(response.text)
#
# response = requests.delete(
#     "http://127.0.0.1:5000/user",
# headers=headers
# )
# print(response.status_code)
# print(response.text)
#
# response = requests.post(
#     "http://127.0.0.1:5000/adv",
#     json={
#         "author": "J2",
#         "title": "jfhjfjfooj",
#         "description": "sjjjyi",
#     }, headers=headers,
# )
# print(response.status_code)
# print(response.text)

# response = requests.get(
#     "http://127.0.0.1:5000/user",
#     headers=headers
# )
# print(response.status_code)
# print(response.text)

# response = requests.patch(
#     "http://127.0.0.1:5000/adv/1",
#     json={
#         "title": "hsuths",
#         "author": "J2",
#
#     },
#     headers=headers,
# )
# print(response.status_code)
# print(response.text)
# #
# response = requests.get(
#     "http://127.0.0.1:5000/adv/10",
#     headers=headers
# )
#
# print(response.status_code)
# print(response.text)
# #
# response = requests.delete(
#     "http://127.0.0.1:5000/adv/1",
#     headers=headers
# )
# print(response.status_code)
# print(response.text)



