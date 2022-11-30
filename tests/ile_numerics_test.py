from machine_common_sense.config_manager import Vector3d

from ideal_learning_env.numerics import (
    MinMaxFloat,
    MinMaxInt,
    VectorFloatConfig,
    VectorIntConfig,
    retrieve_all_vectors
)


def test_retrieve_all_vectors_ints():
    output = retrieve_all_vectors(VectorIntConfig(x=0, y=1, z=2))
    assert output == [Vector3d(x=0, y=1, z=2)]

    output = retrieve_all_vectors([VectorIntConfig(x=0, y=1, z=2)])
    assert output == [Vector3d(x=0, y=1, z=2)]

    output = retrieve_all_vectors(VectorIntConfig(x=0, y=1, z=[2, 3]))
    assert output == [
        Vector3d(x=0, y=1, z=2),
        Vector3d(x=0, y=1, z=3)
    ]

    output = retrieve_all_vectors(VectorIntConfig(x=[-1, 0], y=1, z=[2, 3]))
    assert output == [
        Vector3d(x=-1, y=1, z=2),
        Vector3d(x=-1, y=1, z=3),
        Vector3d(x=0, y=1, z=2),
        Vector3d(x=0, y=1, z=3)
    ]

    output = retrieve_all_vectors(VectorIntConfig(x=0, y=1, z=MinMaxInt(2, 5)))
    assert output == [
        Vector3d(x=0, y=1, z=2),
        Vector3d(x=0, y=1, z=3),
        Vector3d(x=0, y=1, z=4),
        Vector3d(x=0, y=1, z=5)
    ]

    output = retrieve_all_vectors(
        VectorIntConfig(x=[-1, 0], y=1, z=MinMaxInt(2, 5))
    )
    assert output == [
        Vector3d(x=-1, y=1, z=2),
        Vector3d(x=-1, y=1, z=3),
        Vector3d(x=-1, y=1, z=4),
        Vector3d(x=-1, y=1, z=5),
        Vector3d(x=0, y=1, z=2),
        Vector3d(x=0, y=1, z=3),
        Vector3d(x=0, y=1, z=4),
        Vector3d(x=0, y=1, z=5)
    ]

    output = retrieve_all_vectors([
        VectorIntConfig(x=0, y=1, z=2),
        VectorIntConfig(x=3, y=4, z=5),
        VectorIntConfig(x=6, y=7, z=8),
    ])
    assert output == [
        Vector3d(x=0, y=1, z=2),
        Vector3d(x=3, y=4, z=5),
        Vector3d(x=6, y=7, z=8)
    ]

    output = retrieve_all_vectors([
        VectorIntConfig(x=[-1, 0], y=1, z=MinMaxInt(2, 3)),
        VectorIntConfig(x=MinMaxInt(10, 11), y=20, z=[30, 40])
    ])
    assert output == [
        Vector3d(x=-1, y=1, z=2),
        Vector3d(x=-1, y=1, z=3),
        Vector3d(x=0, y=1, z=2),
        Vector3d(x=0, y=1, z=3),
        Vector3d(x=10, y=20, z=30),
        Vector3d(x=10, y=20, z=40),
        Vector3d(x=11, y=20, z=30),
        Vector3d(x=11, y=20, z=40)
    ]


def test_retrieve_all_vectors_floats():
    output = retrieve_all_vectors(VectorFloatConfig(x=0, y=1, z=2))
    assert output == [Vector3d(x=0, y=1, z=2)]

    output = retrieve_all_vectors([VectorFloatConfig(x=0, y=1, z=2)])
    assert output == [Vector3d(x=0, y=1, z=2)]

    output = retrieve_all_vectors(VectorFloatConfig(x=0, y=1, z=[2, 3]))
    assert output == [
        Vector3d(x=0, y=1, z=2),
        Vector3d(x=0, y=1, z=3)
    ]

    output = retrieve_all_vectors(
        VectorFloatConfig(x=[-1, 0], y=1, z=[2, 2.1])
    )
    assert output == [
        Vector3d(x=-1, y=1, z=2),
        Vector3d(x=-1, y=1, z=2.1),
        Vector3d(x=0, y=1, z=2),
        Vector3d(x=0, y=1, z=2.1)
    ]

    output = retrieve_all_vectors(
        VectorFloatConfig(x=0, y=1, z=MinMaxFloat(2, 3))
    )
    assert output == [
        Vector3d(x=0, y=1, z=2),
        Vector3d(x=0, y=1, z=2.1),
        Vector3d(x=0, y=1, z=2.2),
        Vector3d(x=0, y=1, z=2.3),
        Vector3d(x=0, y=1, z=2.4),
        Vector3d(x=0, y=1, z=2.5),
        Vector3d(x=0, y=1, z=2.6),
        Vector3d(x=0, y=1, z=2.7),
        Vector3d(x=0, y=1, z=2.8),
        Vector3d(x=0, y=1, z=2.9),
        Vector3d(x=0, y=1, z=3)
    ]

    output = retrieve_all_vectors(
        VectorFloatConfig(x=[-1, 0], y=1, z=MinMaxFloat(2, 2.2))
    )
    assert output == [
        Vector3d(x=-1, y=1, z=2),
        Vector3d(x=-1, y=1, z=2.1),
        Vector3d(x=-1, y=1, z=2.2),
        Vector3d(x=0, y=1, z=2),
        Vector3d(x=0, y=1, z=2.1),
        Vector3d(x=0, y=1, z=2.2)
    ]

    output = retrieve_all_vectors([
        VectorFloatConfig(x=0, y=1, z=2),
        VectorFloatConfig(x=3, y=4, z=5),
        VectorFloatConfig(x=6, y=7, z=8),
    ])
    assert output == [
        Vector3d(x=0, y=1, z=2),
        Vector3d(x=3, y=4, z=5),
        Vector3d(x=6, y=7, z=8)
    ]

    output = retrieve_all_vectors([
        VectorFloatConfig(x=[-1, 0], y=1, z=MinMaxFloat(2, 2.1)),
        VectorFloatConfig(x=MinMaxFloat(10, 10.1), y=20, z=[30, 40])
    ])
    assert output == [
        Vector3d(x=-1, y=1, z=2),
        Vector3d(x=-1, y=1, z=2.1),
        Vector3d(x=0, y=1, z=2),
        Vector3d(x=0, y=1, z=2.1),
        Vector3d(x=10, y=20, z=30),
        Vector3d(x=10, y=20, z=40),
        Vector3d(x=10.1, y=20, z=30),
        Vector3d(x=10.1, y=20, z=40)
    ]
