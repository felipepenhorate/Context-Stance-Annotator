from copy import deepcopy
import json


class Comment:
    def __init__(self, attributes):
        self.id = attributes["id"]
        self.name = attributes["name"]
        self.ups = attributes["ups"]
        self.downs = attributes["downs"]
        if not isinstance(attributes["author"], str):
            self.author = attributes["author"].name if attributes["author"] else ""
        else:
            self.author = attributes["author"]
        self.score = attributes["score"]
        self.body = attributes["body"]
        self.parent_id = attributes["parent_id"]
        self.replies = None
        self.depth = attributes["depth"]
        self.permalink = attributes["permalink"]
        self.created_utc = attributes["created_utc"]
        if "labeled" in attributes:
            self.labeled = attributes["labeled"]
        if "pos_news" in attributes:
            self.pos_news = attributes["pos_news"]
        if "pos_before" in attributes:
            self.pos_before = attributes["pos_before"]

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "ups": self.ups,
            "downs": self.downs,
            "author": self.author,
            "score": self.score,
            "body": self.body,
            "depth": self.depth,
            "created_utc": self.created_utc,
        }

    def to_json(self):
        to_return_json = deepcopy(self.__dict__)
        to_return_json["replies"] = [
            reply.to_json() for reply in to_return_json["replies"]
        ]
        return to_return_json


class Submission:
    def __init__(self, submission):
        attributes = submission.__dict__
        self.id = attributes["id"]
        self.name = attributes["name"]
        self.ups = attributes["ups"]
        self.downs = attributes["downs"]
        if not isinstance(attributes["author"], str):
            self.author = attributes["author"].name if attributes["author"] else ""
        else:
            self.author = attributes["author"]
        self.score = attributes["score"]
        self.url = attributes["url"]
        self.permalink = attributes["permalink"]
        self.num_comments = attributes["num_comments"]
        self.upvote_ratio = attributes["upvote_ratio"]
        self.selftext = attributes["selftext"]
        self.title = attributes["title"]
        self.comments = sub_comments(submission.comments)

    def get_comments(self):
        return self.comments

    def __get_sublist(self, comment):
        sub_comments = set()

        for sub_comment in comment.replies:
            sub_comments.add(sub_comment)
            sub_list = self.__get_sublist(sub_comment)
            for aux in sub_list:
                sub_comments.add(aux)

        return sub_comments

    def list(self):
        comments = set()
        for comment in self.comments:
            comments.add(comment)
            sub_list = self.__get_sublist(comment)
            for aux in sub_list:
                comments.add(aux)
        return list(comments)

    def to_json(self):
        to_return_json = deepcopy(self.__dict__)
        to_return_json["comments"] = [
            reply.to_json() for reply in to_return_json["comments"]
        ]
        return to_return_json


def sub_comments(comments):
    replies = []

    for comment in comments:
        new_comment = Comment(comment.__dict__)
        childs = sub_comments(comment.replies)
        new_comment.replies = childs
        replies.append(new_comment)
    return replies


def load_submission_from_json(d):
    class obj(object):
        def __init__(self, dict_):
            self.__dict__.update(dict_)

    temp_obj = json.loads(json.dumps(d), object_hook=obj)
    submission_data = Submission(temp_obj)
    return submission_data
