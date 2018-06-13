import unittest

from corvid.util.geom import Box


class TestBox(unittest.TestCase):
    def setUp(self):
        # 1 and 2 overlap in y but not x
        # 1 and 3 overlap in x but not y  [1 contains 3]
        self.box1 = Box(llx=-1.0, lly=-0.5, urx=1.0, ury=0.5)
        self.box2 = Box(llx=1.1, lly=-1.0, urx=2.0, ury=0.0)
        self.box3 = Box(llx=0.0, lly=0.6, urx=0.5, ury=0.9)

    def test_shape(self):
        self.assertEqual(self.box1.height, 1.0)
        self.assertEqual(self.box1.width, 2.0)

    def test_is_overlap(self):
        self.assertFalse(Box.is_x_overlap(self.box1, self.box1))
        self.assertFalse(Box.is_x_overlap(self.box1, self.box2))
        self.assertTrue(Box.is_x_overlap(self.box1, self.box3))

        self.assertFalse(Box.is_y_overlap(self.box1, self.box1))
        self.assertTrue(Box.is_y_overlap(self.box1, self.box2))
        self.assertFalse(Box.is_y_overlap(self.box1, self.box3))

    def test_min_x_dist(self):
        self.assertAlmostEqual(Box.min_x_dist(self.box1, self.box2), 0.1)
        with self.assertRaises(Exception):
            Box.min_x_dist(self.box1, self.box3)

    def test_min_y_dist(self):
        self.assertAlmostEqual(Box.min_y_dist(self.box1, self.box3), 0.1)
        with self.assertRaises(Exception):
            Box.min_y_dist(self.box1, self.box2)

    def test_compute_bounding_box(self):
        box = Box.compute_bounding_box(boxes=[self.box1, self.box2, self.box3])
        self.assertEqual(box.ll.x, -1.0)
        self.assertEqual(box.ll.y, -1.0)
        self.assertEqual(box.ur.x, 2.0)
        self.assertEqual(box.ur.y, 0.9)
