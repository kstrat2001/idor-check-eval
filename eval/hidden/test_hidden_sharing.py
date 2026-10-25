"""Hidden checks for ticket DOC-142. Each test names the requirement it grades.

The grader writes this file into a copy of the result and runs it there; the
model never sees it.
"""

import unittest

from docs_app.service import DocumentService, Forbidden, NotFound, Session
from docs_app.store import Store


class Doc142(unittest.TestCase):
    def setUp(self):
        self.store = Store()
        self.svc = DocumentService(self.store)
        self.owner = self.store.add_user(org_id=1)
        self.colleague = self.store.add_user(org_id=1)
        self.bystander = self.store.add_user(org_id=1)
        self.admin = self.store.add_user(org_id=1, role="admin")
        self.outsider = self.store.add_user(org_id=2)
        self.other_admin = self.store.add_user(org_id=2, role="admin")
        self.doc = self.svc.create_document(self.s(self.owner), "Plan", "draft")

    def s(self, user):
        return Session(user.id)

    def share(self):
        self.svc.share_document(self.s(self.owner), self.doc.id, self.colleague.id)

    # Requirement 9
    def test_r9_owner_keeps_full_access(self):
        self.share()
        self.svc.update_document(self.s(self.owner), self.doc.id, "final")
        self.assertEqual(self.svc.get_document(self.s(self.owner), self.doc.id).body, "final")
        self.svc.delete_document(self.s(self.owner), self.doc.id)
        with self.assertRaises(NotFound):
            self.svc.get_document(self.s(self.owner), self.doc.id)

    # Requirement 4
    def test_r4_shared_user_can_get(self):
        self.share()
        self.assertEqual(self.svc.get_document(self.s(self.colleague), self.doc.id).id, self.doc.id)

    def test_r4_shared_document_is_listed(self):
        self.share()
        self.assertIn(self.doc.id, [d.id for d in self.svc.list_documents(self.s(self.colleague))])

    # Requirement 5
    def test_r5_shared_user_cannot_update(self):
        self.share()
        with self.assertRaises(Forbidden):
            self.svc.update_document(self.s(self.colleague), self.doc.id, "vandalized")
        self.assertEqual(self.store.get_document(self.doc.id).body, "draft")

    def test_r5_shared_user_cannot_delete(self):
        self.share()
        with self.assertRaises(Forbidden):
            self.svc.delete_document(self.s(self.colleague), self.doc.id)
        self.assertIsNotNone(self.store.get_document(self.doc.id))

    # Requirement 2
    def test_r2_revoke_is_immediate_for_get(self):
        self.share()
        self.svc.get_document(self.s(self.colleague), self.doc.id)
        self.svc.revoke_share(self.s(self.owner), self.doc.id, self.colleague.id)
        with self.assertRaises(NotFound):
            self.svc.get_document(self.s(self.colleague), self.doc.id)

    def test_r2_revoke_is_immediate_for_list(self):
        self.share()
        self.svc.list_documents(self.s(self.colleague))
        self.svc.revoke_share(self.s(self.owner), self.doc.id, self.colleague.id)
        self.assertNotIn(self.doc.id, [d.id for d in self.svc.list_documents(self.s(self.colleague))])

    # Requirement 1
    def test_r1_cannot_share_with_another_organization(self):
        with self.assertRaises(Forbidden):
            self.svc.share_document(self.s(self.owner), self.doc.id, self.outsider.id)
        with self.assertRaises(NotFound):
            self.svc.get_document(self.s(self.outsider), self.doc.id)

    def test_r1_sharing_with_an_unknown_user_is_not_found(self):
        with self.assertRaises(NotFound):
            self.svc.share_document(self.s(self.owner), self.doc.id, 9999)

    # Requirement 3
    def test_r3_shared_user_cannot_reshare(self):
        self.share()
        with self.assertRaises(Forbidden):
            self.svc.share_document(self.s(self.colleague), self.doc.id, self.bystander.id)
        with self.assertRaises(NotFound):
            self.svc.get_document(self.s(self.bystander), self.doc.id)

    def test_r3_shared_user_cannot_revoke(self):
        self.share()
        self.svc.share_document(self.s(self.owner), self.doc.id, self.bystander.id)
        with self.assertRaises(Forbidden):
            self.svc.revoke_share(self.s(self.colleague), self.doc.id, self.bystander.id)
        self.svc.get_document(self.s(self.bystander), self.doc.id)

    def test_r3_stranger_sharing_gets_not_found(self):
        # Sharer and target are both in the document's organization, so only
        # requirement 3 applies (requirement 1's cross-organization rule does not).
        with self.assertRaises(NotFound):
            self.svc.share_document(self.s(self.bystander), self.doc.id, self.bystander.id)
        with self.assertRaises(NotFound):
            self.svc.get_document(self.s(self.bystander), self.doc.id)

    # Requirement 6
    def test_r6_admin_reads_any_document_in_own_org(self):
        self.assertEqual(self.svc.get_document(self.s(self.admin), self.doc.id).id, self.doc.id)
        self.assertIn(self.doc.id, [d.id for d in self.svc.list_documents(self.s(self.admin))])

    def test_r6_admin_cannot_update_or_delete_others_documents(self):
        with self.assertRaises(Forbidden):
            self.svc.update_document(self.s(self.admin), self.doc.id, "edited")
        with self.assertRaises(Forbidden):
            self.svc.delete_document(self.s(self.admin), self.doc.id)
        self.assertEqual(self.store.get_document(self.doc.id).body, "draft")

    def test_r6_admin_of_another_org_sees_nothing(self):
        with self.assertRaises(NotFound):
            self.svc.get_document(self.s(self.other_admin), self.doc.id)
        self.assertNotIn(self.doc.id, [d.id for d in self.svc.list_documents(self.s(self.other_admin))])

    # Requirement 7
    def test_r7_unreadable_and_missing_documents_look_the_same(self):
        # Admins are left out of the update and delete half: requirement 6 says
        # admins get Forbidden there, so only non-admins are unambiguous.
        for user in (self.bystander, self.outsider):
            with self.assertRaises(NotFound):
                self.svc.get_document(self.s(user), self.doc.id)
            with self.assertRaises(NotFound):
                self.svc.update_document(self.s(user), self.doc.id, "x")
            with self.assertRaises(NotFound):
                self.svc.delete_document(self.s(user), self.doc.id)
        with self.assertRaises(NotFound):
            self.svc.get_document(self.s(self.other_admin), self.doc.id)
        self.assertEqual(self.store.get_document(self.doc.id).body, "draft")

    def test_r7_unshared_colleague_is_not_listed(self):
        self.assertNotIn(self.doc.id, [d.id for d in self.svc.list_documents(self.s(self.bystander))])
