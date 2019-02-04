from random import Random
import numpy as np
import gncgym.definitions as defs

seed = 21452353
rng = Random()
rng.seed(seed)

p1 = defs.Position(*[10 * rng.random() for _ in range(3)])
p2 = defs.Position(*[10 * rng.random() for _ in range(3)])
o1 = defs.Orientation(*[10 * rng.random() for _ in range(3)])
o2 = defs.Orientation(*[10 * rng.random() for _ in range(3)])
po1 = defs.Pose(*[10 * rng.random() for _ in range(6)])
po2 = defs.Pose(*[10 * rng.random() for _ in range(6)])
lv1 = defs.LinVel(*[10 * rng.random() for _ in range(3)])
lv2 = defs.LinVel(*[10 * rng.random() for _ in range(3)])
av1 = defs.AngVel(*[10 * rng.random() for _ in range(3)])
av2 = defs.AngVel(*[10 * rng.random() for _ in range(3)])
v1 = defs.Velocity(*[10 * rng.random() for _ in range(6)])
v2 = defs.Velocity(*[10 * rng.random() for _ in range(6)])


class TestDefinitions:
    def test_assumptions(self):
        """
        Some assumptions are made in this test, based on empirical experiments.
        """

        # Tuples are equal to named tuples if their contents are the same
        x = (*[10 * rng.random() for _ in range(3)],)
        xx = (*[10 * rng.random() for _ in range(6)],)
        assert x == defs.Position(*x)
        assert x == defs.Orientation(*x)
        assert xx == defs.Pose(*xx)
        assert x == defs.LinVel(*x)
        assert x == defs.AngVel(*x)
        assert xx == defs.Velocity(*xx)

    def test_add_for_all_types(self):
        for x, y in zip([p1, o1, po1, lv1, av1, v1], [p2, o2, po2, lv2, av2, v2]):
                assert defs.add(x, y) == tuple(np.array(x) + np.array(y))

    def test_sub_for_all_types(self):
        for x, y in zip([p1, o1, po1, lv1, av1, v1], [p2, o2, po2, lv2, av2, v2]):
            assert defs.sub(x, y) == tuple(np.array(x) - np.array(y))

    def test_dot_for_all_types(self):
        for x, y in zip([p1, o1, po1, lv1, av1, v1], [p2, o2, po2, lv2, av2, v2]):
            assert defs.dot(x, y) == float(np.array(x).dot(np.array(y)))

    def test_norm_for_all_types(self):
        for x, y in zip([p1, o1, po1, lv1, av1, v1], [p2, o2, po2, lv2, av2, v2]):
            assert defs.norm(x) == np.linalg.norm(x)
            assert defs.norm(y) == np.linalg.norm(y)

    def test_distance_for_all_types(self):
        for x, y in zip([p1, o1, po1, lv1, av1, v1], [p2, o2, po2, lv2, av2, v2]):
            assert defs.distance(x, y) == np.linalg.norm(np.array(x) - np.array(y))

    def test_normalise_for_all_types(self):
        for x, y in zip([p1, o1, po1, lv1, av1, v1], [p2, o2, po2, lv2, av2, v2]):
            Lx = np.linalg.norm(np.array(x))
            Ly = np.linalg.norm(np.array(y))
            assert defs.normalise(x) == tuple(np.array(x)/Lx)
            assert defs.normalise(y) == tuple(np.array(y)/Ly)
