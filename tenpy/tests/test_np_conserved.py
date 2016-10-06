"""A collection of tests for tenpy.linalg.np_conserved"""

import tenpy.linalg.np_conserved as npc
import numpy as np
import numpy.testing as npt
import nose.tools as nst
import itertools as it

chinfo = npc.ChargeInfo([1, 2], ['number', 'parity'])
# parity can be derived from number. Yet, this should all work...
qflat = np.array([[0, 0], [1, 1], [2, 0], [-2, 0], [1, 1]])
lc = npc.LegCharge.from_qflat(chinfo, qflat)
arr = np.zeros((5, 5))
arr[0, 0] = 1.
arr[1, 1] = arr[4, 1] = arr[1, 4] = arr[4, 4] = 2.
arr[2, 2] = 3.
arr[3, 3] = 4.

qflat2 = qflat + np.array([[1, 0]])  # for checking non-zero total charge
lc2 = npc.LegCharge.from_qflat(chinfo, qflat2)


def test_npc_Array_conversion():
    # trivial
    a = npc.Array.from_ndarray_trivial(arr)
    npt.assert_equal(a.to_ndarray(), arr)
    # non-trivial charges
    a = npc.Array.from_ndarray(arr, chinfo, [lc, lc.conj()])
    npt.assert_equal(a._get_block_charge([0, 2]), [-2, 0])
    npt.assert_equal(a.to_ndarray(), arr)
    npt.assert_equal(a.qtotal, np.array([0, 0], npc.QDTYPE))
    # check non-zero total charge
    a = npc.Array.from_ndarray(arr, chinfo, [lc, lc2.conj()])
    npt.assert_equal(a.qtotal, np.array([-1, 0], npc.QDTYPE))
    npt.assert_equal(a.to_ndarray(), arr)
    a.gauge_total_charge(1)
    npt.assert_equal(a.qtotal, np.array([0, 0], npc.QDTYPE))
    # check type conversion
    a_clx = a.astype(np.complex128)
    nst.eq_(a_clx.dtype, np.complex128)
    npt.assert_equal(a_clx.to_ndarray(), arr.astype(np.complex128))


def test_npc_Array_sort():
    a = npc.Array.from_ndarray(arr, chinfo, [lc, lc.conj()])
    p_flat, a_s = a.sort_legcharge(True, False)
    arr_s = arr[np.ix_(*p_flat)]  # what a_s should be
    npt.assert_equal(a_s.to_ndarray(), arr_s)  # sort without bunch
    _, a_sb = a_s.sort_legcharge(False, True)
    npt.assert_equal(a_sb.to_ndarray(), arr_s)  # bunch after sort
    npt.assert_equal(a_sb._qdata_sorted, False)
    a_sb.sort_qdata()
    npt.assert_equal(a_sb.to_ndarray(), arr_s)  # sort_qdata


def test_npc_Array_labels():
    a = npc.Array.from_ndarray(arr, chinfo, [lc, lc.conj()])
    for t in [('x', None), (None, 'y'), ('x', 'y')]:
        a.set_leg_labels(t)
        nst.eq_(a.get_leg_labels(), t)
        axes = (0, 1, 1, 0, 1, 0)
        axes_l = list(axes) # replace with labels, where available
        for i, l in enumerate(axes[:4]):
            if t[l] is not None:
                axes_l[i] = t[l]
        nst.eq_(tuple(a.get_leg_indices(axes_l)), axes)
