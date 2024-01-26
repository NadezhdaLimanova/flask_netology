import requests

response = requests.post(
    "http://127.0.0.1:5000/user",
    json={
        "name": "John Doe1",
        "email": "john@doeexample1.com",
        "password": "securepassword1",
    },
)
print(response.status_code)
print(response.text)


# response = requests.get(
#     "http://127.0.0.1:5000/adv/1",
# )
#
# print(response.status_code)
# print(response.text)

# response = requests.get(
#     "http://127.0.0.1:5000/adv/10",
# )
#
# print(response.status_code)
# print(response.text)
#
# response = requests.post(
#     "http://127.0.0.1:5000/adv",
#     json={
#         "header": "adv_1",
#         "text": "text1",
#         "author": "author1",
#         "password": "123456",
#     },
# )
#
# print(response.status_code)
# print(response.text)
#
# response = requests.patch(
#     "http://127.0.0.1:5000/adv/2",
#     json={
#         "text": "text23433",
#     },
# )
#
# print(response.status_code)
# print(response.text)
#
#
# response = requests.delete(
#     "http://127.0.0.1:5000/adv/2",)
#
#
# print(response.status_code)
# print(response.text)
#
# response = requests.get(
#     "http://127.0.0.1:5000/adv/2",
# )
#
# print(response.status_code)
# print(response.text)

