import json
import streamlit as st
import pickle

import streamlit_nested_layout
from submission_graph import load_submission_from_json
from io import StringIO

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
