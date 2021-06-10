import unittest

import event_queue
import plane_util as pu

class EventQueueTestCase(unittest.TestCase):

    def test_event_queue_terminates_in_trivial_case(self):
        A = pu.SaneCounter([pu.Point(x,y) for x,y in [(1, 2), (2, 3), (2, 3), (3, 5)]])
        B = pu.SaneCounter([pu.Point(x,y) for x,y in [(1, 2), (3, 18)]])
        queue = event_queue.EventQueue(A, B)
        for _ in range(100):
            if not queue:
                break
            self.assertIsInstance(queue.next_event(radius=3), event_queue.Event)
        self.assertFalse(bool(queue))
        
if __name__ == "__main__":
    unittest.main()
