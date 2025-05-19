import unittest
from src.structures.linked_list import LinkedList, Node

class TestLinkedList(unittest.TestCase):

    def test_empty_list(self):
        ll = LinkedList()
        self.assertTrue(ll.is_empty())
        self.assertEqual(len(ll), 0)
        self.assertIsNone(ll.head)
        self.assertEqual(ll.get_all(), [])
        self.assertIsNone(ll.search("data"))

    def test_append(self):
        ll = LinkedList()
        ll.append(1)
        self.assertFalse(ll.is_empty())
        self.assertEqual(len(ll), 1)
        self.assertEqual(ll.head.data, 1)
        self.assertIsNone(ll.head.next)
        self.assertEqual(ll.get_all(), [1])

        ll.append(2)
        self.assertEqual(len(ll), 2)
        self.assertEqual(ll.head.next.data, 2)
        self.assertIsNone(ll.head.next.next)
        self.assertEqual(ll.get_all(), [1, 2])

    def test_prepend(self):
        ll = LinkedList()
        ll.prepend(1)
        self.assertEqual(ll.head.data, 1)
        self.assertIsNone(ll.head.next)
        self.assertEqual(ll.get_all(), [1])

        ll.prepend(2)
        self.assertEqual(ll.head.data, 2)
        self.assertEqual(ll.head.next.data, 1)
        self.assertEqual(ll.get_all(), [2, 1])

    def test_insert_after(self):
        ll = LinkedList()
        ll.append(1)
        ll.append(3)
        ll.insert_after(ll.head, 2)
        self.assertEqual(ll.get_all(), [1, 2, 3])

        ll.insert_after(Node(4), 5) 
        self.assertEqual(ll.get_all(), [1, 2, 3])

    def test_delete(self):
        ll = LinkedList()
        ll.append(1)
        ll.append(2)
        ll.append(3)

        ll.delete(2)
        self.assertEqual(ll.get_all(), [1, 3])
        self.assertEqual(len(ll), 2)

        ll.delete(1)
        self.assertEqual(ll.get_all(), [3])
        self.assertEqual(len(ll), 1)

        ll.delete(3)
        self.assertTrue(ll.is_empty())
        self.assertEqual(len(ll), 0)

        ll.append(1)
        ll.delete(4)
        self.assertEqual(ll.get_all(), [1])

    def test_search(self):
        ll = LinkedList()
        ll.append(1)
        ll.append(2)
        ll.append(3)

        self.assertIsNotNone(ll.search(2))
        self.assertEqual(ll.search(2).data, 2)
        self.assertIsNone(ll.search(4))

    def test_len(self):
        ll = LinkedList()
        self.assertEqual(len(ll), 0)
        ll.append(1)
        self.assertEqual(len(ll), 1)
        ll.append(2)
        self.assertEqual(len(ll), 2)
        ll.delete(1)
        self.assertEqual(len(ll), 1)
        ll.delete(2)
        self.assertEqual(len(ll), 0)

    def test_str(self):
        ll = LinkedList()
        self.assertEqual(str(ll), "")
        ll.append(1)
        self.assertEqual(str(ll), "1")
        ll.append(2)
        self.assertEqual(str(ll), "1 -> 2")
        ll.append(3)
        self.assertEqual(str(ll), "1 -> 2 -> 3")

if __name__ == '__main__':
    unittest.main()