from model.api_key import ApiKey


# string comparison
# comparing 2 strings as numbers first we compare length
# otherwise comparison of the 2 strings will give us a wrong answer:
# 123
# 23
# second string `23` will be higher because it has greater first symbol
# because length is not taken into account, in this method it is fixed
def str_number_is_greater(str1, str2):
    if len(str1) > len(str2):
        return True

    if len(str1) < len(str2):
        return False

    return str1 > str2


def read_api_key(file):
    api_key = ApiKey()
    # read from file (with statement will close the file after the reading is done)
    with open(file) as f:
        content = f.readlines()
    # get strip all lines (i.e. removing white spaces from both ends 'asbc ' -> 'asbc')
    content = [x.strip() for x in content]

    # find returns -1 if the word is not found
    # thus searching for all required keys
    for token in content:
        if token.find("consumer_key=") != -1:
            api_key.consumer_key = token[12:]
        if token.find("consumer_secret=") != -1:
            api_key.consumer_secret = token[15:]
        if token.find("access_token_key=") != -1:
            api_key.access_token_key = token[16:]
        if token.find("access_token_secret=") != -1:
            api_key.access_token_secret = token[19:]

    return api_key
