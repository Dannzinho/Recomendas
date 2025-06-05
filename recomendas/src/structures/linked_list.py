class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        last_node = self.head
        while last_node.next:
            last_node = last_node.next
        last_node.next = new_node

    def prepend(self, data):
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node

    def insert_after(self, prev_node, data):
        if not prev_node:
            print("O nó anterior não existe.")
            return
        new_node = Node(data)
        new_node.next = prev_node.next
        prev_node.next = new_node

    def delete(self, product_id_to_delete):
        current_node = self.head
        
        if current_node and hasattr(current_node.data, 'product_id') and current_node.data.product_id == product_id_to_delete:
            self.head = current_node.next
            current_node = None
            return

        prev_node = None
        while current_node and (not hasattr(current_node.data, 'product_id') or current_node.data.product_id != product_id_to_delete):
            prev_node = current_node
            current_node = current_node.next

        if current_node is None:
            return
        
        if prev_node:
            prev_node.next = current_node.next
        else:
            self.head = current_node.next
            
        current_node = None

    def search(self, key):
        current_node = self.head
        while current_node:

            if hasattr(current_node.data, 'product_id') and current_node.data.product_id == key:
                return current_node

            elif current_node.data == key:
                return current_node
            current_node = current_node.next
        return None

    def get_all(self):
        elements = []
        current_node = self.head
        while current_node:
            elements.append(current_node.data)
            current_node = current_node.next
        return elements

    def is_empty(self):
        return self.head is None

    def __len__(self):
        count = 0
        current_node = self.head
        while current_node:
            count += 1
            current_node = current_node.next
        return count

    def __str__(self):
        nodes = []
        current = self.head
        while current:
            nodes.append(str(current.data))
            current = current.next
        return ' -> '.join(nodes)

    def get_last_item(self):
        if not self.head:
            return None
        current_node = self.head
        while current_node.next:
            current_node = current_node.next
        return current_node.data