from unittest import TestCase
from Repository import Repository


class TestRepository(TestCase):

    def setUp(self) -> None:
        self.repository = Repository()

    def test_repository(self):
        self.repository.boot("Z:\\930450_MiasMagicComicBook\\Production\\Film")
        self.assertEqual(self.repository.root.name, "Film")

        # Testing search map correctness
        film = self.repository.search("Film")
        e01 = self.repository.search("E01")
        e01_sq010 = self.repository.search("E01_SQ010")
        self.assertEqual(self.repository.root, film)
        self.assertEqual(self.repository.root.children[0], e01)
        self.assertEqual(self.repository.root.children[0].children[0], e01_sq010)
        with self.assertRaises(FileExistsError):
            self.repository.search("HelloWorld")

        # Testing depth naming
        for i in self.repository.root.children:
            self.assertEqual("E01", i.name)
            for f in i.children:
                self.assertEqual("E01_SQ010", f.name)
                for j in f.children:
                    self.assertEqual("E01_SQ010_SH010", j.name)
                    break
                break
            break

        # Testing depth typing
        for i in self.repository.root.children:
            self.assertEqual("episode", i.type)
            for f in i.children:
                self.assertEqual("seq", f.type)
                for j in f.children:
                    self.assertEqual("shot", j.type)
                    break
                break
            break
