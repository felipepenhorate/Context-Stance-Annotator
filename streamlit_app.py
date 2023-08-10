import json
import streamlit as st
import pickle

import streamlit_nested_layout

from copy import deepcopy
from io import StringIO
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


st.title("Ferramenta de Rotulação de dados ")
uploaded_file = st.file_uploader("Escolha um arquivo", type="json")

if "labeled_data" not in st.session_state:
    st.session_state["labeled_data"] = {}


def change_labeled_data(comment, level):
    st.session_state["labeled_data"][level] = ":ok:"


def create_marking(comment, level):
    inner_cols = st.columns([1, 1])
    pos_news = None
    pos_before = None
    labels = ["A favor", "Contra", "Neutro"]
    with inner_cols[0]:
        if hasattr(comment, "pos_news"):
            default_idx = labels.index(comment.pos_news)
        else:
            default_idx = 0
        pos_news = st.selectbox(
            "Posicionamento a notícia",
            labels,
            key="sel_" + level + "_news",
            on_change=change_labeled_data,
            args=[comment, level],
            index=default_idx,
        )
    with inner_cols[1]:
        if hasattr(comment, "pos_before"):
            default_idx = labels.index(comment.pos_before)
        else:
            default_idx = 0
        pos_before = st.selectbox(
            "Posicionamento ao comentário anterior",
            labels,
            key="sel_" + level + "_before",
            on_change=change_labeled_data,
            args=[comment, level],
            index=default_idx,
        )
    return pos_news, pos_before


def create_comment_data(comment, comment_label):
    pos_news, pos_before = create_marking(comment, comment_label)
    comment.pos_news = pos_news
    comment.pos_before = pos_before
    if st.session_state["labeled_data"][comment_label] == ":ok:":
        comment.labeled = True
    get_sublist(comment, comment_label)


def get_sublist(comment, current_label):
    for i, sub_comment in enumerate(comment.replies):
        comment_label = current_label + "_" + str(i)
        if comment_label not in st.session_state["labeled_data"]:
            if hasattr(sub_comment, "labeled"):
                st.session_state["labeled_data"][comment_label] = ":ok:"
            else:
                st.session_state["labeled_data"][comment_label] = ":warning:"
        with st.expander(
            f"**{sub_comment.author}**: {sub_comment.body} {st.session_state['labeled_data'][comment_label]}",
            expanded=True,
        ):
            create_comment_data(sub_comment, comment_label)


def build_comment_tree(initial_comments, current_label):
    for i, comment in enumerate(initial_comments):
        comment_label = current_label + "_" + str(i)
        if comment_label not in st.session_state["labeled_data"]:
            if hasattr(comment, "labeled"):
                st.session_state["labeled_data"][comment_label] = ":ok:"
            else:
                st.session_state["labeled_data"][comment_label] = ":warning:"
        with st.expander(
            f"**{comment.author}**: {comment.body} {st.session_state['labeled_data'][comment_label]}",
            expanded=False,
        ):
            create_comment_data(comment, comment_label)


if uploaded_file is not None:
    # urls_dict_new = pickle.load(uploaded_file)

    # submission_data = urls_dict_new[0]["data"]["brasil"]
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    string_data = stringio.read()
    json_data = json.loads(string_data)
    submission_data = load_submission_from_json(json_data)
    st.markdown(f"## {submission_data.title}")
    st.markdown(submission_data.selftext)
    st.markdown("Notícia: " + submission_data.url)

    st.write("Comentários: ")

    build_comment_tree(submission_data.get_comments(), "1")

    st.download_button(
        "Download Marcações",
        data=json.dumps(submission_data.to_json()),
        file_name="data.json",
    )
