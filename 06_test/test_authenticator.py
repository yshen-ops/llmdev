import pytest
from authenticator import Authenticator

def test_register():
    auth = Authenticator()
    auth.register("username", "password")
    assert auth.users["username"] == "password"

def test_register_error():
    auth = Authenticator()
    auth.register("username", "password")
    with pytest.raises(ValueError, match="エラー: ユーザーは既に存在します。"):
        auth.register("username", "password")

def test_login():
    auth = Authenticator()
    auth.register("username", "password")
    assert auth.login("username", "password") == "ログイン成功"

def test_login_error():
    auth = Authenticator()
    with pytest.raises(ValueError, match="エラー: ユーザー名またはパスワードが正しくありません。"):
        assert auth.login("username", "password") == "ログイン成功"

