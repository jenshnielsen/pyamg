from numpy import array, zeros,  inner, conjugate
from scipy.sparse import csr_matrix, isspmatrix
from scipy.sparse.sputils import upcast
from scipy.sparse.linalg.isolve.utils import make_system
from scipy.sparse.linalg.interface import aslinearoperator
from scipy import ceil, asmatrix, rand
from warnings import warn
from pyamg.util.linalg import norm

__docformat__ = "restructuredtext en"

__all__ = ['bicgstab']


def bicgstab(A, b, x0=None, tol=1e-5, maxiter=None, xtype=None, M=None, callback=None, residuals=None):
    '''
    Biconjugate Gradient Aglorithm with Stabilization applied to A x = b
    Left preconditioning is supported

    Parameters
    ----------
    A : {array, matrix, sparse matrix, LinearOperator}
        n x n, linear system to solve
    b : {array, matrix}
        right hand side, shape is (n,) or (n,1)
    x0 : {array, matrix}
        initial guess, default is a vector of zeros
    tol : float
        relative convergence tolerance, i.e. tol is scaled by ||b||
    maxiter : int
        maximum number of allowed iterations
    xtype : type
        dtype for the solution, default is automatic type detection
    M : {array, matrix, sparse matrix, LinearOperator}
        n x n, inverted preconditioner, i.e. solve M A A.H x = b.
    callback : function
        User-supplied funtion is called after each iteration as
        callback(xk), where xk is the current solution vector
    residuals : list
        residuals has the residual norm history,
        including the initial residual, appended to it
     
    Returns
    -------    
    (xNew, info)
    xNew -- an updated guess to the solution of Ax = b
    info -- halting status of bicgstab
            0  : successful exit
            >0 : convergence to tolerance not achieved,
                 return iteration count instead.  
            <0 : numerical breakdown, or illegal input

    Notes
    -----
    The LinearOperator class is in scipy.sparse.linalg.interface.
    Use this class if you prefer to define A or M as a mat-vec routine
    as opposed to explicitly constructing the matrix.  A.psolve(..) is
    still supported as a legacy.

    Examples
    --------
    >>>from pyamg.krylov import *
    >>>from scipy import rand
    >>>import pyamg
    >>>A = pyamg.poisson((50,50))
    >>>b = rand(A.shape[0],)
    >>>(x,flag) = bicgstab(A,b,maxiter=200, tol=1e-8)
    >>>print pyamg.util.linalg.norm(b - A*x)

    References
    ----------
    Yousef Saad, "Iterative Methods for Sparse Linear Systems, 
    Second Edition", SIAM, pp. 231-234, 2003

    '''
    
    # Convert inputs to linear system, with error checking  
    A,M,x,b,postprocess = make_system(A,M,x0,b,xtype)

    # Check iteration numbers
    if maxiter == None:
        maxiter = len(x) + 5
    elif maxiter < 1:
        raise ValueError('Number of iterations must be positive')

    # Scale tol by normb
    normb = norm(b) 
    if normb != 0:
        tol = tol*normb

    # Prep for method
    r = b - A*x
    normr = norm(r)

    if residuals is not None:
        residuals[:] = [normr]

    # Is initial guess sufficient?
    if normr < tol:
        return (postprocess(x), 0)
   
    rstar = r.copy()
    p     = r.copy()

    rrstarOld = inner(conjugate(rstar), r)

    iter = 0

    # Begin BiCGStab
    while True:
        Mp  = M*p
        AMp = A*Mp
        
        # alpha = (r_j, rstar) / (A*M*p_j, rstar)
        alpha = rrstarOld/inner(conjugate(rstar), AMp)
        
        # s_j = r_j - alpha*A*M*p_j
        s   = r - alpha*AMp
        Ms  = M*s
        AMs = A*Ms

        # omega = (A*M*s_j, s_j)/(A*M*s_j, A*M*s_j)
        omega = inner(conjugate(AMs), s)/inner(conjugate(AMs), AMs)

        # x_{j+1} = x_j +  alpha*M*p_j + omega*M*s_j
        x = x + alpha*Mp + omega*Ms

        # r_{j+1} = s_j - omega*A*M*s
        r = s - omega*AMs

        # beta_j = (r_{j+1}, rstar)/(r_j, rstar) * (alpha/omega)
        rrstarNew = inner(conjugate(rstar), r)
        beta      = (rrstarNew / rrstarOld) * (alpha / omega)
        rrstarOld = rrstarNew

        # p_{j+1} = r_{j+1} + beta*(p_j - omega*A*M*p)
        p = r + beta*(p - omega*AMp)

        iter += 1
        
        normr = norm(r)

        if residuals is not None:
            residuals.append(normr)

        if callback is not None:
            callback(x)

        if normr < tol:
            return (postprocess(x), 0)

        if iter == maxiter:
            return (postprocess(x), iter)




#if __name__ == '__main__':
#    # from numpy import diag
#    # A = random((4,4))
#    # A = A*A.transpose() + diag([10,10,10,10])
#    # b = random((4,1))
#    # x0 = random((4,1))
#    # %timeit -n 15 (x,flag) = bicgstab(A,b,x0,tol=1e-8,maxiter=100)
#    from pyamg.gallery import stencil_grid
#    from numpy.random import random
#    A = stencil_grid([[0,-1,0],[-1,4,-1],[0,-1,0]],(100,100),dtype=float,format='csr')
#    b = random((A.shape[0],))
#    x0 = random((A.shape[0],))
#
#    import time
#    from scipy.sparse.linalg.isolve import bicgstab as ibicgstab
#
#    print '\n\nTesting BiCGStab with %d x %d 2D Laplace Matrix'%(A.shape[0],A.shape[0])
#    t1=time.time()
#    (x,flag) = bicgstab(A,b,x0,tol=1e-8,maxiter=100)
#    t2=time.time()
#    print '%s took %0.3f ms' % ('bicgstab', (t2-t1)*1000.0)
#    print 'norm = %g'%(norm(b - A*x))
#    print 'info flag = %d'%(flag)
#
#    t1=time.time()
#    (y,flag) = ibicgstab(A,b,x0,tol=1e-8,maxiter=100)
#    t2=time.time()
#    print '\n%s took %0.3f ms' % ('linalg bicgstab', (t2-t1)*1000.0)
#    print 'norm = %g'%(norm(b - A*y))
#    print 'info flag = %d'%(flag)

    