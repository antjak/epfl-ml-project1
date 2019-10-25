# -*- coding: utf-8 -*-
"""Classifiers"""

import solver
import implementations
import dataprocessing
from dataprocessing import log_1_plus_exp_safe
import numpy as np
import math


class LeastSquares:
    """Class representing the least squares classifier"""

    def __init__(self, verbose=False, max_evaluations=100):
        """
        Constructor

        :param verbose: print out information
        :param max_evaluations: maximum number of evaluations
        """

        self.verbose = verbose
        self.max_evaluations = max_evaluations

    def fit(self, y, X):
        """
        Finds weights to fit the data to the model

        :param y: answers
        :param X: data
        """

        # dimensions
        n, d = X.shape

        # initial weight vector
        self.w = np.zeros(d)

        # find weights
        self.w = np.linalg.solve(X.T @ X, X.T @ y)


    def function_object(self, w, y, X):
        """
        Function Object.

        :param y: answers
        :param X: data
        :param w: weights
        :return: loss, gradient
        """

        # dimensions
        n, d = X.shape

        # compute error
        e = y - X @ w

        # compute loss
        f = 1/(2 * n) * np.sum(e ** 2)

        # compute gradient
        g = - 1 / n * X.T @ e

        return f, g

    def predict(self, X):
        """
        Predict

        :param X: data
        :return: answer prediction
        """

        return np.sign(X @ self.w)

class LeastSquaresL1(LeastSquares):
    """L2 Regularized Logistic Regression"""
    
    def __init__(self, lambda_, verbose=False, max_evaluations=100):
        """
        Constructor

        :param lambda: regularization strength
        :param verbose: print out information
        :param max_evaluations: maximum number of evaluations
        """
        self.lambda_ = lambda_
        super().__init__(verbose, max_evaluations)
    
    def fit(self, y, X):
        """
        Finds weights to fit the data to the model

        :param y: answers
        :param X: data
        """

        # dimensions
        n, d = X.shape

        # initial weight vector
        self.w = np.zeros(d)

        # fit weights
        self.w, f = solver.gradient_descent_L1(self.function_object, self.w, self.lambda_,
                                               self.max_evaluations, y, X, verbose=self.verbose)
    
class LeastSquaresL2(LeastSquares):
    
    def __init__(self, lambda_, verbose=False, max_evaluations=100):
        """
        Constructor

        :param lambda: regularization strength
        :param verbose: print out information
        :param max_evaluations: maximum number of evaluations
        """
        self.lambda_ = lambda_
        super().__init__(verbose, max_evaluations)
    
    def fit(self, y, X):
        """
        Finds weights to fit the data to the model

        :param y: answers
        :param X: data
        """

        # dimensions
        n, d = X.shape

        # initial weight vector
        self.w = np.zeros(d)

        # find weights
        self.w = np.linalg.solve(X.T @ X + n * self.lambda_ * np.eye(d), X.T @ y)
        
    def function_object(self, w, y, X):
        """
        Function Object.

        :param y: answers
        :param X: data
        :param w: weights
        :return: loss, gradient
        """
        
        f, g = super().function_object(w, y, X)

        # add regularization
        f += self.lambda_ / 2 * w.dot(w)
        g += self.lambda_ * w

        return f, g
    

class LogisticRegression:
    """Logistic Regression"""

    def __init__(self, verbose=False, max_evaluations=100):
        """
        Constructor

        :param verbose: print out information
        :param max_evaluations: maximum number of evaluations
        """

        self.verbose = verbose
        self.max_evaluations = max_evaluations

    def fit(self, y, X):
        """
        Finds weights to fit the data to the model

        :param y: answers
        :param X: data
        """

        # dimensions
        n, d = X.shape

        # initial weight vector
        self.w = np.zeros(d)

        # fit weights
        self.w, f = solver.gradient_descent(self.function_object, self.w, 
                                            self.max_evaluations, y, X, verbose=self.verbose)

    def sigmoid(self, t):
        """
        Sigmoid

        :param t: parameter
        :return: apply sigmoid function on t
        """
        return 1.0 / (1 + np.exp(- t))

    def function_object(self, w, y, X):
        """
        Function Object.

        :param y: answers
        :param X: data
        :param w: weights
        :return: loss, gradient
        """

        pred = y * X.dot(w)

        # function value
        f = np.sum(log_1_plus_exp_safe(-pred))

        # gradient value
        res = - y / (1. + np.exp(pred))
        g = X.T.dot(res)

        return f, g

    def predict(self, X):
        """
        Predict

        :param X: data
        :return: answer prediction
        """

        return np.sign(X @ self.w)

    
class LogisticRegressionL1(LogisticRegression):
    """L1 Regularized Logistic Regression"""

    def __init__(self, lambda_=1.0, verbose=False, max_evaluations=100):
        """
        Constructor

        :param lambda_: lambda of L1 regularization
        :param verbose: print out information
        :param max_evaluations: maximum number of evaluations
        """
        self.verbose = verbose
        self.max_evaluations = max_evaluations
        self.lambda_ = lambda_

    def funObj(self, w, y, X):
        """
        Function Object

        :param w: weight
        :param y: answers
        :param X: data
        :return: loss, gradient
        """
        # Obtain normal loss and gradient using the superclass
        f, g = super(LogisticRegressionL2, self).funObj(w, y, X)

        # Add L2 regularization
        f += self.lambda_ / 2. * w.dot(w)
        g += self.lambda_ * w

        return f, g

class LogisticRegressionL2(LogisticRegression):
    """L2 Regularized Logistic Regression"""

    def __init__(self, lambda_=1.0, verbose=False, max_evaluations=100):
        """
        Constructor

        :param lambda_: lambda of L2 regularization
        :param verbose: print out information
        :param max_evaluations: maximum number of evaluations
        """
        self.verbose = verbose
        self.max_evaluations = max_evaluations
        self.lambda_ = lambda_
       
        
    def fit(self, y, X):
        """
        Finds weights to fit the data to the model

        :param y: answers
        :param X: data
        """

        # dimensions
        n, d = X.shape

        # initial weight vector
        self.w = np.zeros(d)

        # fit weights
        self.w, f = solver.gradient_descent_L1(self.function_object, self.w, self.lambda_,
                                               self.max_evaluations, y, X, verbose=self.verbose)
    

class PCA_N:
    '''
    Solves the PCA problem min_Z,W (Z*W-X)^2 using SVD
    '''

    def __init__(self, k):
        self.k = k

    def fit(self, X):
        self.mu = np.mean(X,axis=0)
        X = X - self.mu

        U, s, Vh = np.linalg.svd(X)
        self.W = Vh[:self.k]

    def compress(self, X):
        X = X - self.mu
        Z = X@self.W.T
        return Z

    def expand(self, Z):
        X = Z@self.W + self.mu
        return X
    

class AlternativePCA(PCA_N):
    '''
    Solves the PCA problem min_Z,W (Z*W-X)^2 using gradient descent
    '''
    def fit(self, X):
        n,d = X.shape
        k = self.k
        self.mu = np.mean(X,0)
        X = X - self.mu

        # Randomly initial Z, W
        z = np.random.randn(n*k)
        w = np.random.randn(k*d)

        for i in range(10): # do 10 "outer loop" iterations
            z, f = solver.gradient_descent(self._fun_obj_z, z, 10, w, X, k)
            w, f = solver.gradient_descent(self._fun_obj_w, w, 10, z, X, k)
            print('Iteration %d, loss = %.1f' % (i, f))

        self.W = w.reshape(k,d)

    def compress(self, X):
        n,d = X.shape
        k = self.k
        X = X - self.mu
        # We didn't enforce that W was orthogonal 
        # so we need to optimize to find Z
        # (or do some matrix operations)
        z = np.zeros(n*k)
        z,f = solver.gradient_descent(self._fun_obj_z, z, 100, self.W.flatten(), X, k)
        Z = z.reshape(n,k)
        return Z

    def _fun_obj_z(self, z, w, X, k):
        n,d = X.shape
        Z = z.reshape(n,k)
        W = w.reshape(k,d)

        R = np.dot(Z,W) - X
        f = np.sum(R**2)/2
        g = np.dot(R, W.transpose())
        
        return f, g.flatten()

    def _fun_obj_w(self, w, z, X, k):
        n,d = X.shape
        Z = z.reshape(n,k)
        W = w.reshape(k,d)

        R = np.dot(Z,W) - X
        f = np.sum(R**2)/2
        g = np.dot(Z.transpose(), R)
        
        return f, g.flatten()

class RobustPCA(AlternativePCA):
    def _fun_obj_z(self, z, w, X, k):
        n,d = X.shape
        Z = z.reshape(n,k)
        W = w.reshape(k,d)
        epsilon = 0.0001
        
        R = np.dot(Z,W) - X
        f = np.sum(np.sqrt(R**2+epsilon))
        g = np.sum(np.dot((1/(2*np.sqrt(R**2+epsilon))).transpose(), 2*np.dot(R, W.transpose())))
        
        return f, g.flatten()
    
    def _fun_obj_w(self, w, z, X, k):
        n,d = X.shape
        Z = z.reshape(n,k)
        W = w.reshape(k,d)
        epsilon = 0.0001
        
        R = np.dot(Z,W) - X
        f = np.sum(np.sqrt(R**2+epsilon))
        g = np.sum(np.dot((1/(2*np.sqrt(R**2+epsilon))), (2*np.dot(Z.transpose(), R)).transpose()))

        return f, g.flatten()
        