from fastapi_mail.config import ConnectionConfig


def test_configuration(mail_config):
    conf = ConnectionConfig(**mail_config)
    assert conf.MAIL_USERNAME == "example@test.com"
    assert conf.MAIL_PORT == 25






