from scipy.testing import *

from scipy.sparse import csr_matrix
from scipy.io import loadmat

from numpy import array, ones, zeros, uint32

from pyamg import smoothed_aggregation_solver
from pyamg.sa import standard_aggregation, symmetric_strength_of_connection
from pyamg.gallery import load_example

from vis import coarse_grid_vis, write_mesh, shrink_elmts

def example_vis(test=0):
    """Run different visualization examples"""

    if test==0:
        """
        Basic 3x4 nodes square (12 elements)

        Plots 'points' aggregates for C/F splitting.
        """
        file_name     = 'example_%d_mesh.vtu' % test
        agg_file_name = 'example_%d_agg.vtu' % test
        Vert = array([[0.0,0.0],
                      [1.0,0.0],
                      [2.0,0.0],
                      [0.0,1.0],
                      [1.0,1.0],
                      [2.0,1.0],
                      [0.0,2.0],
                      [1.0,2.0],
                      [2.0,2.0],
                      [0.0,3.0],
                      [1.0,3.0],
                      [2.0,3.0]])
        E2V = array([[0,4,3],
                     [0,1,4],
                     [1,5,4],
                     [1,2,5],
                     [3,7,6],
                     [3,4,7],
                     [4,8,7],
                     [4,5,8],
                     [6,10,9],
                     [6,7,10],
                     [7,11,10],
                     [7,8,11]],dtype=uint32)
        row = array([0,1,2,3,4,5,6,7,8,9,10,11])
        col = array([1,0,1,1,0,1,0,1,0,1,0, 1])
        data = ones((1,12),dtype=uint32).ravel()
        Agg = csr_matrix((data,(row,col)),shape=(12,2))
        coarse_grid_vis(agg_file_name, Vert=Vert, E2V=E2V, Agg=Agg, mesh_type='tri', A=None, plot_type='points')
        write_mesh(file_name, Vert, E2V, mesh_type='tri')
        
    if test==1:
        """
        Small 21 element mesh.  _____
                                |   /
                                |__/
        Plots primal aggregates.
        """
        file_name     = 'example_%d_mesh.vtu' % test
        agg_file_name = 'example_%d_agg.vtu' % test
        Vert = array([[0.0,0.0],
                      [1.0,0.0],
                      [2.0,0.0],
                      [0.0,1.0],
                      [1.0,1.0],
                      [2.0,1.0],
                      [3.0,1.0],
                      [0.0,2.0],
                      [1.0,2.0],
                      [2.0,2.0],
                      [3.0,2.0],
                      [4.0,2.0],
                      [0.0,3.0],
                      [1.0,3.0],
                      [2.0,3.0],
                      [3.0,3.0],
                      [4.0,3.0],
                      [5.0,3.0]])
        E2V = array([[0,4,3],
                     [0,1,4],
                     [1,5,4],
                     [1,2,5],
                     [2,6,5],
                     [3,8,7],
                     [3,4,8],
                     [4,9,8],
                     [4,5,9],
                     [5,10,9],
                     [5,6,10],
                     [6,11,10],
                     [7,13,12],
                     [7,8,13],
                     [8,14,13],
                     [8,9,14],
                     [9,15,14],
                     [9,10,15],
                     [10,16,15],
                     [10,11,16],
                     [11,17,16]],dtype=uint32)
        row = array([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17])
        col = array([0,1,3,0,1,1,3,0,0,1, 3, 4, 0, 0, 0, 2, 4, 4])
        data = ones((1,18),dtype=uint32).ravel()
        Agg=csr_matrix((data,(row,col)),shape=(18,5))
        coarse_grid_vis(agg_file_name, Vert=Vert, E2V=E2V, Agg=Agg, mesh_type='tri', A=None, plot_type='primal')
        pdata = 2 * ones(18)
        pvdata = ones((18,3))
        write_mesh(file_name, Vert, E2V, mesh_type='tri', pdata=pdata, pvdata=pvdata)

    if test==2:
        """
        Airfoil example.

        Plot both points and primal aggregates
        """

        file_name      = 'example_Airfoil_mesh.vtu'
        agg_file_name1 = 'example_Airfoil_points_agg.vtu'
        agg_file_name2 = 'example_Airfoil_primal_agg.vtu'

        ex    = loadmat('Airfoil.mat')
        aggex = loadmat('Airfoil_aggs.mat')

        A    = ex['A']
        E2V  = ex['elements']
        Vert = ex['vertices']

        C   = symmetric_strength_of_connection(A.tocsr(), theta=0.25)
        Agg = standard_aggregation(C.tocsr())

        # visualize the aggregates two different ways
        coarse_grid_vis(agg_file_name1, Vert, E2V, Agg, A=A, plot_type='points', mesh_type='tri')
        coarse_grid_vis(agg_file_name2, Vert, E2V, Agg, A=A, plot_type='primal', mesh_type='tri')
        write_mesh(file_name, Vert, E2V, mesh_type='tri')

    if test==3:
        """
        PyAMG logo

        Plot both points and primal
        """

        file_name      = 'example_PyAMGLogo_mesh.vtu'
        agg_file_name1 = 'example_PyAMGLogo_points_agg.vtu'
        agg_file_name2 = 'example_PyAMGLogo_primal_agg.vtu'
        ex = loadmat('../../Docs/logo/pyamg_s30a30.mat')
        A = ex['A']
        E2V  = ex['elements']
        Vert = ex['vertices']
        Agg  = standard_aggregation(A.tocsr())

        # visualize the aggregates two different ways
        coarse_grid_vis(agg_file_name1, Vert, E2V, Agg, A=A, plot_type='points', mesh_type='tri')
        coarse_grid_vis(agg_file_name2, Vert, E2V, Agg, A=A, plot_type='primal', mesh_type='tri')

        # visualize the mesh
        fid = open(file_name,'w') #test with open file object
        write_mesh(fid, Vert, E2V, mesh_type='tri')

    if test==4:
        """
        DG p=1 case
        """

        file_name      = 'example_dg_p1_mesh.vtu'
        agg_file_name1 = 'example_dg_p1_points_agg.vtu'
        agg_file_name2 = 'example_dg_p1_primal_agg.vtu'
        ex = loadmat('./test_dg_p6.mat')
        A = ex['A']
        E2V  = ex['elements']
        Vert = ex['vertices']
        B = ex['B']
        from pyamg.sa_ode_strong_connections import sa_ode_strong_connections
        Agg  = standard_aggregation(csr_matrix(sa_ode_strong_connections(csr_matrix(A), B, theta=2.0, k=2, proj_type="l2")))

        # visualize the aggregates 
        coarse_grid_vis(agg_file_name1, Vert, E2V, Agg, A=A, plot_type='dg', mesh_type='tri')

        # visualize the mesh
        fid = open(file_name,'w') #test with open file object
        E2V, Vert = shrink_elmts(E2V, Vert)
        write_mesh(fid, Vert, E2V[:,0:3], mesh_type='tri')
    

if __name__ == '__main__':
    # small C/F splitting
    example_vis(0)

    # small 5 aggregate mesh
    example_vis(1)

    # airfoil with standard SA
    example_vis(2)
    
    # PyAMG logo with standard SA
    example_vis(3)
    
    # DG example
    #example_vis(4)