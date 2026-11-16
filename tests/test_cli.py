from app.auth.service import find_user
from app.constants import Role


def test_create_admin_command(app):
    runner = app.test_cli_runner()
    answers = "\n".join(["Brian", "Brian Lin", "a-strong-password", "a-strong-password"]) + "\n"

    result = runner.invoke(args=["create-admin"], input=answers)

    assert result.exit_code == 0
    admin = find_user("brian")
    assert admin.role == Role.ADMIN
    assert admin.display_name == "Brian Lin"
    assert admin.must_change_password is False
    assert admin.check_password("a-strong-password")


def test_create_admin_asks_again_after_bad_answers(app):
    runner = app.test_cli_runner()
    answers = "\n".join(["x", "brian", "Brian Lin", "short", "short", "long-enough-password", "long-enough-password"]) + "\n"

    result = runner.invoke(args=["create-admin"], input=answers)

    assert result.exit_code == 0
    assert "Use 3 to 30 characters" in result.output
    assert "Use at least 8 characters." in result.output
    assert find_user("brian").check_password("long-enough-password")
