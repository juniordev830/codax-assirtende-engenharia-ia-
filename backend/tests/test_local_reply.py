import unittest

from app.main import local_reply


class LocalReplyGreetingTests(unittest.TestCase):
    def test_recognizes_greeting_as_a_whole_word(self):
        reply = local_reply("Oi, tudo bem?")
        self.assertIn("modo local", reply)

    def test_does_not_treat_substring_inside_coisas_as_greeting(self):
        reply = local_reply("Quero dicas sobre coisas de Python")
        self.assertIn("Para verificar a versão do Python", reply)

    def test_non_greeting_git_question_uses_git_guidance(self):
        reply = local_reply("Como verifico o status do git?")
        self.assertIn("git status", reply)


if __name__ == "__main__":
    unittest.main()
