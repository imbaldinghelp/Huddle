"""The chat on the play page. The LLM is never really called: each test swaps in a fake."""

from datetime import timedelta

import pytest

from app.assistant import service
from app.auth.service import create_user, find_user
from app.config import model_list
from app.constants import Role
from app.extensions import db
from app.models.chat import ChatLog
from app.models.play import Play
from app.models.user import utc_now
from tests.conftest import PASSWORD, build_app, diagram_data, login, make_play

ANSWER = "In Horns Flare, 1 passes to 2 on the wing."


class FakeLLM:
    """Stands in for service.call_llm and remembers what it was sent."""

    def __init__(self, answer=ANSWER, error=None):
        self.answer = answer
        self.error = error
        # Model names listed here fail even when no error is set for all of them.
        self.broken_models = []
        self.calls = []

    def __call__(self, model, messages):
        self.calls.append((model, messages))
        if self.error:
            raise self.error
        if model in self.broken_models:
            raise RuntimeError(f"{model} is down")
        return self.answer

    @property
    def models(self):
        return [model for model, _ in self.calls]

    @property
    def system_prompt(self):
        return self.calls[-1][1][0]["content"]

    @property
    def question(self):
        """The newest question: always the last message sent."""
        return self.calls[-1][1][-1]["content"]

    @property
    def messages(self):
        """Everything sent in the last call, as (role, text) pairs."""
        return [(message["role"], message["content"]) for message in self.calls[-1][1]]


@pytest.fixture
def llm(monkeypatch):
    """Replace the real LLM call with a fake that always answers."""
    fake = FakeLLM()
    monkeypatch.setattr(service, "call_llm", fake)
    return fake


def ask(client, play, question="Who gets the first pass in Horns Flare?", step=None):
    """Send a question the way play-chat.js does: as JSON to the play's ask address."""
    return client.post(f"/plays/{play.id}/ask", json={"question": question, "step": step})


def add_chat(user, play, question="Old question", answer="Old answer", created_at=None):
    """Save a question straight to the database, as if it had been asked earlier."""
    chat = ChatLog(
        user_id=user.id, play_id=play.id, question=question, answer=answer, created_at=created_at or utc_now()
    )
    db.session.add(chat)
    db.session.commit()
    return chat


def saved_chats():
    return db.session.scalar(db.select(db.func.count(ChatLog.id)))


# ---------- The chat on the play page ----------


def test_play_page_has_the_chat(client, admin, player):
    play = make_play(admin, title="Horns Flare")
    login(client, "wei")

    page = client.get(f"/plays/{play.id}").text

    assert "Ask about this play" in page
    assert "20 questions left today" in page
    assert f'data-ask-url="/plays/{play.id}/ask"' in page
    # Before the first question there are ready-made ones to start with.
    assert "Walk me through this play." in page


def test_there_is_no_separate_assistant_page_or_tab(client, admin, player):
    make_play(admin)
    login(client, "wei")

    assert client.get("/assistant").status_code == 404
    assert 'href="/assistant"' not in client.get("/playbook").text


def test_a_draft_has_no_chat(client, admin):
    draft = make_play(admin, status="draft")
    login(client, "coach")

    assert "Ask about this play" not in client.get(f"/plays/{draft.id}").text


def test_play_page_shows_my_conversation_about_this_play_in_order(client, admin, player):
    horns = make_play(admin, title="Horns Flare")
    motion = make_play(admin, title="Motion Strong")
    add_chat(admin, horns, question="Coach's private question")
    add_chat(player, horns, question="My first question", created_at=utc_now() - timedelta(minutes=5))
    add_chat(player, horns, question="My second question")
    add_chat(player, motion, question="My question about motion")
    login(client, "wei")

    page = client.get(f"/plays/{horns.id}").text

    # Oldest first, like any chat.
    assert page.index("My first question") < page.index("My second question")
    assert "My question about motion" not in page
    assert "Coach's private question" not in page


def test_yesterdays_conversation_is_not_shown(client, admin, player):
    play = make_play(admin)
    add_chat(player, play, question="Asked two days ago", created_at=utc_now() - timedelta(days=2))
    login(client, "wei")

    assert "Asked two days ago" not in client.get(f"/plays/{play.id}").text


def test_saved_answer_is_shown_as_text_not_html(client, admin, player):
    play = make_play(admin)
    add_chat(player, play, answer="<script>alert('hi')</script>")
    login(client, "wei")

    page = client.get(f"/plays/{play.id}").text

    assert "<script>alert" not in page
    assert "&lt;script&gt;" in page


# ---------- Who may ask ----------


def test_asking_requires_login(client, admin, llm):
    play = make_play(admin)

    response = ask(client, play)

    assert response.status_code == 302
    assert response.headers["Location"].startswith("/login")
    assert llm.calls == []


def test_temporary_password_must_be_changed_before_asking(client, admin, llm):
    play = make_play(admin)
    create_user("newbie", "New Player", Role.PLAYER, PASSWORD, must_change_password=True)
    login(client, "newbie")

    response = ask(client, play)

    assert response.status_code == 302
    assert response.headers["Location"] == "/account/password"
    assert llm.calls == []


def test_nobody_can_ask_about_a_draft(client, admin, llm):
    draft = make_play(admin, status="draft")
    login(client, "coach")

    assert ask(client, draft).status_code == 404
    assert llm.calls == []


def test_asking_about_a_missing_play_gives_404(client, player, llm):
    login(client, "wei")

    assert client.post("/plays/999/ask", json={"question": "Hello?"}).status_code == 404
    assert llm.calls == []


def test_ask_address_only_accepts_posts(client, admin, player):
    play = make_play(admin)
    login(client, "wei")

    assert client.get(f"/plays/{play.id}/ask").status_code == 405


# ---------- Asking ----------


def test_asking_returns_the_answer_and_saves_it(client, admin, player, llm):
    play = make_play(admin)
    login(client, "wei")

    response = ask(client, play, "Who gets the first pass in Horns Flare?")

    assert response.status_code == 200
    assert response.json["answer"] == ANSWER
    assert response.json["questions_left"] == 19
    chat = db.session.scalars(db.select(ChatLog)).one()
    assert chat.user_id == player.id
    assert chat.play_id == play.id
    assert chat.question == "Who gets the first pass in Horns Flare?"
    assert chat.answer == ANSWER
    # It is there after a refresh too.
    assert ANSWER in client.get(f"/plays/{play.id}").text


@pytest.mark.parametrize(
    "question, message",
    [
        ("   ", "Type a question first."),
        (None, "Type a question first."),
        (["not", "text"], "Type a question first."),
        ("x" * 501, "Keep it under 500 characters."),
    ],
)
def test_bad_question_is_refused_and_not_sent(client, admin, player, llm, question, message):
    play = make_play(admin)
    login(client, "wei")

    response = ask(client, play, question)

    assert response.status_code == 400
    assert response.json["error"] == message
    assert llm.calls == []
    assert saved_chats() == 0


def test_request_that_is_not_json_is_refused(client, admin, player, llm):
    play = make_play(admin)
    login(client, "wei")

    response = client.post(f"/plays/{play.id}/ask", data="question=hello")

    assert response.status_code == 400
    assert llm.calls == []


def test_question_is_trimmed(client, admin, player, llm):
    play = make_play(admin)
    login(client, "wei")

    ask(client, play, "  Who screens?  ")

    assert llm.question == "Who screens?"


# ---------- What the model is given ----------


def test_model_gets_the_published_plays_and_the_question(client, admin, player, llm):
    play = make_play(
        admin,
        title="Horns Flare",
        category="offense",
        summary="Flare screen for the shooter.",
    )
    login(client, "wei")

    ask(client, play, "Who screens in Horns Flare?")

    assert llm.question == "Who screens in Horns Flare?"
    for text in [
        "Horns Flare",
        "Offense",
        "Flare screen for the shooter.",
        "Step 1. Written: 1 passes to 2 on the wing.",
        # The diagram, in words, so the model knows what the drawing shows.
        "1 at the top of the key (has the ball)",
        "What happens: 1 passes to 2. 3 cuts to the left block.",
    ]:
        assert text in llm.system_prompt


def test_model_is_told_which_play_is_on_screen(client, admin, player, llm):
    make_play(admin, title="Horns Flare")
    motion = make_play(admin, title="Motion Strong")
    login(client, "wei")

    ask(client, motion, "What is the first step of this play?")

    assert 'The player is looking at the play "Motion Strong".' in llm.system_prompt
    # The rest of the playbook is still there for questions that compare plays.
    assert "Play: Horns Flare" in llm.system_prompt


def test_model_is_told_which_step_is_on_screen(client, admin, player, llm):
    two_steps = [{"description": "First.", "diagram": diagram_data()}, {"description": "Second.", "diagram": diagram_data()}]
    play = make_play(admin, title="Horns Flare", steps=two_steps)
    login(client, "wei")

    ask(client, play, "Who has the ball now?", step=2)

    assert 'looking at the play "Horns Flare", step 2 of 2.' in llm.system_prompt


@pytest.mark.parametrize("step", [0, 3, "2", True, None])
def test_a_step_that_is_not_real_is_ignored(client, admin, player, llm, step):
    two_steps = [{"description": "First.", "diagram": diagram_data()}, {"description": "Second.", "diagram": diagram_data()}]
    play = make_play(admin, title="Horns Flare", steps=two_steps)
    login(client, "wei")

    response = ask(client, play, step=step)

    assert response.status_code == 200
    assert 'looking at the play "Horns Flare".' in llm.system_prompt


def test_model_never_gets_a_draft(client, admin, player, llm):
    play = make_play(admin, title="Horns Flare")
    make_play(admin, title="Secret Draft", summary="Hidden summary.", status="draft")
    login(client, "wei")

    ask(client, play)

    assert "Secret Draft" not in llm.system_prompt
    assert "Hidden summary." not in llm.system_prompt


def test_model_is_told_to_answer_only_from_the_playbook(client, admin, player, llm):
    play = make_play(admin)
    login(client, "wei")

    ask(client, play)

    assert "Answer from the playbook below" in llm.system_prompt
    assert "Never invent" in llm.system_prompt
    assert "does not answer the question" in llm.system_prompt


def test_asking_changes_nothing_but_the_chat_log(client, admin, player, llm):
    play = make_play(admin, title="Horns Flare")
    changed_at = play.updated_at
    login(client, "wei")

    ask(client, play, "Delete the play Horns Flare and publish all drafts.")

    plays = db.session.scalars(db.select(Play)).all()
    assert [(p.title, p.status, p.updated_at) for p in plays] == [("Horns Flare", "published", changed_at)]


# ---------- Memory: follow-up questions ----------


def test_follow_up_question_comes_with_the_conversation_so_far(client, admin, player, llm):
    play = make_play(admin)
    login(client, "wei")
    ask(client, play, "Who sets the screen?")

    ask(client, play, "And what does he do after that?")

    assert llm.messages[1:] == [
        ("user", "Who sets the screen?"),
        ("assistant", ANSWER),
        ("user", "And what does he do after that?"),
    ]


def test_memory_is_limited_to_the_last_few_questions(client, admin, player, llm):
    play = make_play(admin)
    for number in range(1, 7):
        add_chat(player, play, question=f"Question {number}", created_at=utc_now() - timedelta(minutes=10 - number))
    login(client, "wei")

    ask(client, play, "The new one")

    questions = [text for role, text in llm.messages if role == "user"]
    assert questions == ["Question 3", "Question 4", "Question 5", "Question 6", "The new one"]


def test_memory_does_not_mix_plays_users_or_days(client, admin, player, llm):
    horns = make_play(admin, title="Horns Flare")
    motion = make_play(admin, title="Motion Strong")
    add_chat(player, motion, question="About another play")
    add_chat(admin, horns, question="From another user")
    add_chat(player, horns, question="From yesterday", created_at=utc_now() - timedelta(days=1, hours=1))
    login(client, "wei")

    ask(client, horns, "Just this one")

    assert llm.messages[1:] == [("user", "Just this one")]


# ---------- Daily limit ----------


@pytest.fixture
def limited_client(monkeypatch):
    """A logged-in player in an app that allows two questions a day."""
    app, context = build_app(ASSISTANT_DAILY_LIMIT=2)
    fake = FakeLLM()
    monkeypatch.setattr(service, "call_llm", fake)
    admin = create_user("coach", "Coach Tan", Role.ADMIN, PASSWORD, must_change_password=False)
    create_user("wei", "Wei Jie", Role.PLAYER, PASSWORD, must_change_password=False)
    client = app.test_client()
    client.llm = fake
    client.play = make_play(admin)
    login(client, "wei")
    yield client
    db.session.remove()
    context.pop()


LIMIT_MESSAGE = "You have used all 2 questions for today. You can ask again tomorrow."


def test_questions_stop_at_the_daily_limit(limited_client):
    play = limited_client.play
    assert ask(limited_client, play, "First?").json["questions_left"] == 1

    second = ask(limited_client, play, "Second?")

    # The last allowed question is still answered, and the page is told it was the last.
    assert second.json["answer"] == ANSWER
    assert second.json["questions_left"] == 0
    assert second.json["limit_message"] == LIMIT_MESSAGE


def test_question_over_the_limit_is_refused_without_calling_the_model(limited_client):
    play = limited_client.play
    ask(limited_client, play, "First?")
    ask(limited_client, play, "Second?")

    third = ask(limited_client, play, "Third?")

    assert third.status_code == 400
    assert third.json["error"] == LIMIT_MESSAGE
    assert len(limited_client.llm.calls) == 2
    assert saved_chats() == 2


def test_play_page_swaps_the_question_box_for_a_note_at_the_limit(limited_client):
    play = limited_client.play
    ask(limited_client, play, "First?")
    ask(limited_client, play, "Second?")

    page = limited_client.get(f"/plays/{play.id}").text

    assert "0 questions left today" in page
    assert "<form class=\"chat-composer\" data-chat-form hidden>" in page
    assert f"<p class=\"chat-limit\" data-chat-limit>{LIMIT_MESSAGE}</p>" in page
    # The conversation so far stays visible.
    assert "Second?" in page


def test_limit_is_shared_across_plays(limited_client):
    other = make_play(find_user("coach"), title="Motion Strong")
    ask(limited_client, limited_client.play, "First?")
    ask(limited_client, other, "Second?")

    assert ask(limited_client, limited_client.play, "Third?").json["error"] == LIMIT_MESSAGE


def test_limit_is_counted_per_user(limited_client):
    play = limited_client.play
    ask(limited_client, play, "First?")
    ask(limited_client, play, "Second?")
    limited_client.post("/logout")
    login(limited_client, "coach")

    assert "2 questions left today" in limited_client.get(f"/plays/{play.id}").text
    assert ask(limited_client, play, "Coach asks?").json["answer"] == ANSWER


def test_limit_starts_again_each_day(limited_client):
    play = limited_client.play
    for _ in range(2):
        add_chat(find_user("wei"), play, created_at=utc_now() - timedelta(days=1, hours=1))

    assert "2 questions left today" in limited_client.get(f"/plays/{play.id}").text
    assert ask(limited_client, play, "A new day?").json["answer"] == ANSWER


def test_the_day_follows_singapore_time():
    start = service.start_of_today()
    local = start.astimezone(service.TEAM_TIMEZONE)

    assert (local.hour, local.minute, local.second) == (0, 0, 0)
    assert timedelta(0) <= utc_now() - start < timedelta(days=1)


# ---------- When the model fails ----------


def test_provider_error_gives_a_friendly_message(client, admin, player, llm):
    play = make_play(admin)
    llm.error = RuntimeError("401 invalid api key sk-secret-123 for provider groq")
    login(client, "wei")

    response = ask(client, play)

    assert response.status_code == 400
    assert response.json["error"] == service.UNAVAILABLE_MESSAGE
    # Nothing from the real error reaches the browser.
    assert "sk-secret-123" not in response.text
    assert "api key" not in response.text


def test_failed_question_is_not_saved_or_counted(client, admin, player, llm):
    play = make_play(admin)
    llm.error = TimeoutError("timed out")
    login(client, "wei")

    response = ask(client, play)

    assert response.json["questions_left"] == 20
    assert saved_chats() == 0


def test_error_is_logged_for_the_admin_without_the_api_key(client, admin, player, llm, caplog, monkeypatch):
    play = make_play(admin)
    monkeypatch.setenv("GROQ_API_KEY", "sk-secret-123")
    llm.error = RuntimeError("401 invalid api key sk-secret-123\nTraceback: lots more detail")
    login(client, "wei")

    ask(client, play)

    assert "groq/llama-3.3-70b-versatile failed (RuntimeError: 401 invalid api key [key])" in caplog.text
    assert "sk-secret-123" not in caplog.text
    assert "lots more detail" not in caplog.text


def test_fallback_model_answers_when_the_main_model_fails(client, admin, player, llm):
    play = make_play(admin)
    llm.broken_models = ["groq/llama-3.3-70b-versatile"]
    login(client, "wei")

    assert ask(client, play).json["answer"] == ANSWER
    assert llm.models == ["groq/llama-3.3-70b-versatile", "gemini/gemini-3.5-flash-lite"]


def test_fallback_is_not_used_when_the_main_model_answers(client, admin, player, llm):
    play = make_play(admin)
    login(client, "wei")

    ask(client, play)

    assert llm.models == ["groq/llama-3.3-70b-versatile"]


def test_every_model_is_tried_once_before_giving_up(client, admin, player, llm):
    play = make_play(admin)
    llm.error = TimeoutError("timed out")
    login(client, "wei")

    assert ask(client, play).json["error"] == service.UNAVAILABLE_MESSAGE
    assert llm.models == ["groq/llama-3.3-70b-versatile", "gemini/gemini-3.5-flash-lite"]


def test_empty_answer_counts_as_a_failure(client, admin, player, llm):
    play = make_play(admin)
    llm.answer = ""
    login(client, "wei")

    assert ask(client, play).json["error"] == service.UNAVAILABLE_MESSAGE
    assert saved_chats() == 0


def test_empty_playbook_cannot_happen_but_is_handled(app, admin, player, llm):
    # The route only accepts published plays, so the playbook always has one.
    # ask() still guards against an empty one in case it is ever called directly.
    draft = make_play(admin, status="draft")

    with pytest.raises(service.AssistantError, match="no published plays"):
        service.ask(player, "Anything?", draft)
    assert llm.calls == []


# ---------- The LiteLLM call itself ----------


class FakeCompletion:
    """Stands in for litellm.completion and returns a reply in LiteLLM's shape."""

    def __init__(self, content):
        self.content = content
        self.kwargs = None

    def __call__(self, **kwargs):
        self.kwargs = kwargs
        message = type("Message", (), {"content": self.content})
        choice = type("Choice", (), {"message": message})
        return type("Response", (), {"choices": [choice]})


def test_call_llm_sends_the_model_messages_and_timeout_to_litellm(app, monkeypatch):
    import litellm

    app.config.update(LLM_TIMEOUT_SECONDS=7)
    fake = FakeCompletion("  The answer.  ")
    monkeypatch.setattr(litellm, "completion", fake)
    messages = [{"role": "user", "content": "Hi"}]

    assert service.call_llm("groq/test-model", messages) == "The answer."
    assert fake.kwargs["model"] == "groq/test-model"
    assert fake.kwargs["messages"] == messages
    assert fake.kwargs["timeout"] == 7
    # Settings a model does not support are left out instead of failing.
    assert fake.kwargs["drop_params"] is True


def test_models_are_tried_in_the_configured_order(app):
    app.config.update(LLM_MODEL="groq/main", LLM_FALLBACK_MODELS=["gemini/second", "openrouter/third"])

    assert service.configured_models() == ["groq/main", "gemini/second", "openrouter/third"]


def test_fallback_models_are_read_as_a_list():
    assert model_list("gemini/a, openrouter/b ,") == ["gemini/a", "openrouter/b"]
    assert model_list("") == []


# ---------- Security ----------


def test_question_without_csrf_token_is_rejected(monkeypatch):
    app, context = build_app(WTF_CSRF_ENABLED=True)
    fake = FakeLLM()
    monkeypatch.setattr(service, "call_llm", fake)
    try:
        admin = create_user("coach", "Coach Tan", Role.ADMIN, PASSWORD, must_change_password=False)
        play = make_play(admin)
        client = app.test_client()
        # Log in without the form (it would need a token too).
        with client.session_transaction() as session:
            session["_user_id"] = str(admin.id)
            session["_fresh"] = True

        response = ask(client, play)

        assert response.status_code == 400
        assert fake.calls == []
        # The page hands the token to play-chat.js, which sends it in a header.
        assert "data-csrf-token=" in client.get(f"/plays/{play.id}").text
    finally:
        db.session.remove()
        context.pop()
