import unittest

from docs_app.service import DocumentService, NotFound, Session
from docs_app.store import Store


class DocumentServiceTest(unittest.TestCase):
    def setUp(self):
        self.store = Store()
        self.service = DocumentService(self.store)
        self.alice = self.store.add_user(org_id=1)
        self.bob = self.store.add_user(org_id=1)
        self.as_alice = Session(self.alice.id)
        self.as_bob = Session(self.bob.id)

    def test_owner_can_read_a_new_document(self):
        doc = self.service.create_document(self.as_alice, "Plan", "draft")
        self.assertEqual(self.service.get_document(self.as_alice, doc.id).body, "draft")

    def test_list_returns_the_owners_documents_in_id_order(self):
        first = self.service.create_document(self.as_alice, "A", "")
        second = self.service.create_document(self.as_alice, "B", "")
        self.assertEqual([d.id for d in self.service.list_documents(self.as_alice)], [first.id, second.id])

    def test_owner_can_update(self):
        doc = self.service.create_document(self.as_alice, "Plan", "draft")
        self.service.update_document(self.as_alice, doc.id, "final")
        self.assertEqual(self.service.get_document(self.as_alice, doc.id).body, "final")

    def test_owner_can_delete(self):
        doc = self.service.create_document(self.as_alice, "Plan", "draft")
        self.service.delete_document(self.as_alice, doc.id)
        with self.assertRaises(NotFound):
            self.service.get_document(self.as_alice, doc.id)

    def test_unknown_id_is_not_found(self):
        with self.assertRaises(NotFound):
            self.service.get_document(self.as_alice, 999)

    def test_another_users_document_is_not_found(self):
        doc = self.service.create_document(self.as_alice, "Plan", "draft")
        with self.assertRaises(NotFound):
            self.service.get_document(self.as_bob, doc.id)

    def test_another_users_documents_are_not_listed(self):
        self.service.create_document(self.as_alice, "Plan", "draft")
        self.assertEqual(self.service.list_documents(self.as_bob), [])


if __name__ == "__main__":
    unittest.main()
