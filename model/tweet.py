import re

# regular expression for hashtags;
# must start with "#" and contain at least 1 or more character matching the pattern in brackets
TAG_REGEX = "#[a-zA-Z0-9-_]+"


# a class which wraps all important fields
class Tweet:
    # a constructor with 4 input fields
    # and "tags" is optional, which is an empty array by default
    def __init__(self, author, time, message, tags=[]):
        self.author = author
        self.time = time
        self.message = message
        self.tags = tags

        # if tags is default or an empty array run this command
        if len(self.tags) == 0:
            self.__parse_tags(self.message)

    # a private function, which only visible within this class
    # it parses message against the regular expression and extracts tags into a "set" (all duplicate tags are removed)
    def __parse_tags(self, message):
        self.tags = set(re.findall(TAG_REGEX, message))

    # a function used to convert object into array which is useful for database insert
    # here we merge our set of tags into 1 line because I decided that it would be easier to store everything in 1 table
    def to_param_query(self):
        obj = [self.time, self.author, self.message, ''.join(self.tags)]
        return obj

    # overriding default representation function behavior to print more readable object
    def __repr__(self):
        return str(self.__dict__)
