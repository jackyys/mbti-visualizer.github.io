from flask import Flask, request
import requests
import os
import json

app = Flask(__name__, )


mbti_dimensions = ['EI', 'NS', 'FT', 'JP']
mbti_dimension_names = ['Extraversion-Introversion', 'Intuition-Sensing', 'Thinking-Feeling', 'Judging-Perceiving']
opposites = {'E': 'I', 'I': 'E', 'S': 'N', 'N': 'S', 'T': 'F', 'F': 'T', 'P': 'J', 'J': 'P'}

def getProfile(id):
    url = f'https://api.personality-database.com/api/v1/profile/{id}'
    return requests.get(url).json()

def getProfiles(query, limit = 50, offset=0):
    url = f'https://api.personality-database.com/api/v1/new_search'
    params = {
        'query': query,
        'offset': offset,
        'limit': limit,
    }
    element = requests.get(url, params)
    if element == None:
        return None
    return requests.get(url, params).json()

def getMbti(id):
    profile = getProfile(id)
    if profile == None:
        return []
    votes = profile['breakdown_systems']['1']
    total = 0
    counts = [0] * 4

    for vote in votes:
        value, count = vote['myValue'], vote['theCount']
        for i in range(4):
            assert(value[i] in mbti_dimensions[i])
            if value[i] != mbti_dimensions[i][0]:
                counts[i] += count
        total += count
    return [counts[i] / total for i in range(4)]

def download_image(url):
    # download image and save it in images/
    response = requests.get(url)
    local_url = 'static/images/' + url.split('/')[-1]
    print(local_url)
    with open(local_url, 'wb') as f:
        f.write(response.content)
    return local_url

@app.route("/search/")
def searchN():
    # search n = limit profiles and filter
    query = request.args['query']
    filter = ''
    limit = 50
    if 'filter' in request.args:
        filter = request.args['filter']
    if 'limit' in request.args:
        limit = int(request.args['limit'])
    
    result_json = []

    profiles_json = getProfiles(query, limit)
    # if not os.path.exists('./static/images'):
    #     print('Creating images directory')
    #     os.mkdir('static/images')
    for profile in profiles_json['profiles']:
        # print(profile['id'], profile['personality_type'])
        flag = True
        for ch in filter:
            if opposites[ch] in profile['personality_type']:
                flag = False
                break
        
        if flag:
            data_mbti = getMbti(profile['id'])
            if len(data_mbti) != 4:
                continue
            for i in range(4):
                profile[mbti_dimensions[i]] = data_mbti[i]
            
            result_json.append(profile)
            profile['image_url'] = '/' + download_image(profile.pop('profile_image_url'))
            profile['type'] = profile.pop('personality_type')[:4]
            profile['name'] = profile.pop('mbti_profile')
        print(profile)
    print("total: ", len(result_json))
    return json.dumps(result_json)


# @app.route("/total/")
# def searchTillN():
#     # search until n = limit profiles are found
#     search = request.args['search']
#     filter = ''
#     limit = 50
#     if 'filter' in request.args:
#         filter = request.args['filter']
#     if 'limit' in request.args:
#         limit = int(request.args['limit'])

#     start = 0
#     count = 0
#     result_json = []

#     while count < limit:
#         profiles_json = getProfiles(search, limit, start)
#         if (len(profiles_json['profiles']) == 0):
#             break
#         for profile in profiles_json['profiles']:
#             # print(profile['id'], profile['personality_type'])
#             flag = True
#             for ch in filter:
#                 if opposites[ch] in profile['personality_type']:
#                     flag = False
#                     break
            
#             if flag:
#                 data_mbti = getMbti(profile['id'])
#                 if len(data_mbti) != 4:
#                     continue
#                 for i in range(4):
#                     profile[mbti_dimensions[i]] = data_mbti[i]
                
#                 result_json.append(profile)
#                 profile['local_image_url'] = download_image(profile['profile_image_url'])
#                 count += 1
#             if (count >= limit):
#                 break

#             print(profile)
#         start += limit
#     print("total: ", count)
#     return json.dumps(result_json)
