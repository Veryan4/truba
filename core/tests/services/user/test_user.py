from pytest_mock import MockerFixture
from services.user import user


def test_add_user(mocker: MockerFixture):
  hashed_password = "09z8x7s63284hksa87aqs78d512"
  spy_get = mocker.patch('services.user.user.mongo.get', return_value=[])
  spy_set = mocker.patch('services.user.user.mongo.add_or_update',
                         return_value=True)
  mocker.patch('services.user.user.uuid.uuid4',
               return_value=mock_user().user_id)
  mocker.patch('services.user.user.pwd_context.hash',
               return_value=hashed_password)
  mocker.patch('services.user.email.send_user_init_email')

  assert user.add_user(mock_create_user())

  spy_get.assert_called_once_with("User", {"email": mock_create_user().email})

  current_user = {
      "user_id": mock_user().user_id,
      "username": mock_create_user().username,
      "email": mock_create_user().email,
      "hashed_password": hashed_password,
      "terms_consent": mock_create_user().terms_consent
  }
  spy_set.assert_called_once_with(current_user, "User")


def test_get_ids(mocker: MockerFixture):
  spy = mocker.patch('services.user.user.mongo.get',
                     return_value=[mock_user().user_id])

  assert user.get_ids() == [mock_user().user_id]

  spy.assert_called_once_with("User", {}, distinct="user_id")


def mock_user() -> user.User:
  return user.User(id="",
                   user_id="3d925894-7c07-4d70-be56-09f8e1f1071c",
                   username="Veryan",
                   email="info@truba.news",
                   terms_consent="2021-08-13T12:53:49.143Z")


def mock_create_user() -> user.CreateUser:
  return user.CreateUser(username="Veryan",
                         email="info@truba.news",
                         password="password",
                         terms_consent="2021-08-13T12:53:49.143Z")
