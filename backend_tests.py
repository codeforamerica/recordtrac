import unittest

from public_records_portal import notifications, db_helpers

# Here's our "unit tests".
class BackEndTests(unittest.TestCase):

    def testShouldNotify(self):
        self.failIf(notifications.should_notify('jrivers@oaklandnet.com'))
    def testShouldNotNotify(self):
        self.failUnless(notifications.should_notify('nneditch@oaklandnet.com'))
    def testGetObjectWrongParams(self):
    	self.failIf(db_helpers.get_obj("fake object", "not an ID"))
    def testGetObject(self):
    	self.failUnless(db_helpers.get_obj("Request", 10))
    def testGetStaffRecipients(self):
        self.failUnless(notifications.get_staff_recipients(db_helpers.get_obj("Request", 10)))


def main():
    unittest.main()

if __name__ == '__main__':
    main()