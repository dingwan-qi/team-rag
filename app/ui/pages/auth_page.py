"""Login and registration page."""

from __future__ import annotations

import streamlit as st

from app.services.user_service import AuthResult, UserService


def ensure_authenticated() -> dict[str, str] | None:
    user = st.session_state.get("current_user")
    token = st.session_state.get("auth_token")
    if user and token:
        return user

    st.title("TeamRAG")
    st.subheader("登录后使用课程资料智能问答")

    login_tab, register_tab = st.tabs(["登录", "注册"])
    with login_tab:
        _render_login_form()
    with register_tab:
        _render_register_form()
    return None


def _render_login_form() -> None:
    with st.form("login_form"):
        username = st.text_input("用户名", key="login_username")
        password = st.text_input("密码", type="password", key="login_password")
        submitted = st.form_submit_button("登录", type="primary")
    if not submitted:
        return
    try:
        result = UserService().login(username, password)
    except ValueError as exc:
        st.error(str(exc))
        return
    _store_auth_result(result)
    st.success("登录成功")
    _rerun()


def _render_register_form() -> None:
    with st.form("register_form"):
        username = st.text_input("用户名", key="register_username")
        password = st.text_input("密码", type="password", key="register_password")
        password_confirm = st.text_input("确认密码", type="password")
        submitted = st.form_submit_button("注册并登录", type="primary")
    if not submitted:
        return
    if password != password_confirm:
        st.error("两次输入的密码不一致")
        return
    try:
        result = UserService().register(username, password)
    except ValueError as exc:
        st.error(str(exc))
        return
    _store_auth_result(result)
    st.success("注册成功，已自动登录")
    _rerun()


def _store_auth_result(result: AuthResult) -> None:
    st.session_state.auth_token = result.token
    st.session_state.current_user = {
        "id": result.user.id,
        "username": result.user.username,
    }
    st.session_state.messages = []
    st.session_state.memory_loaded_user_id = None


def _rerun() -> None:
    if hasattr(st, "rerun"):
        st.rerun()
        return
    st.experimental_rerun()
