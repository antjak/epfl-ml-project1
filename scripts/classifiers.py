# -*- coding: utf-8 -*-
"""Classifiers"""

import solver
import numpy as np
import math


def log_1_plus_exp_safe(x):
    # compute log(1+exp(x)) in a numerically safe way, avoiding overflow/underflow issues
    out = np.log(1+np.exp(x))
    out[x > 100] = x[x>100]
    out[x < -100] = np.exp(x[x < -100])
    return out

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
        self.w, f = solver.gradient_descent(self.function_object, self.w, self.max_evaluations,
                                 self.verbose, y, X)

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

class LogisticRegressionL2(LogisticRegression):
    """L2 Regularized Logistic Regression"""

    def __init__(self, lambda_=1.0, verbose=False, max_evaluations=100):
        """
        Constructor

        :param lambda_: lambda of L2 regularization
        :param verbose: print out information
        :param max_evaluations: maximum number of evaluations
        """
        super(LogisticRegressionL2, self).__init__(verbose=verbose,
                                                     max_evaluations=max_evaluations)
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
    
    
    
class Kernel:
    """Kernel method"""
    
    def __init__(self, kernel_fun, verbose=False, max_evals=100):
        self.kernel_fun = kernel_fun
        self.verbose = verbose
        self.max_evals = max_evals
        
    def fit(self, y, K):
        pass
        
    def predict(self, y, X, Xtest, *args, lambda_=0):
        K = self.kernel_fun(X, X, *args)
        Ktest = self.kernel_fun(Xtest, X, *args)
        
        self.u = self.fit(y, K, lambda_)
    
        return np.sign(Ktest @ self.u)
    
    @staticmethod
    def kernel_poly(X1, X2, p=2):
        N1, D1 = np.shape(X1)
        N2, D2 = np.shape(X2)
        return np.power(np.ones((N1, N2)) + X1@X2.T, p)
    
    @staticmethod
    def kernel_RBF(X1, X2, sigma=1):
        N1, D1 = np.shape(X1)
        N2, D2 = np.shape(X2)
        K = np.zeros((N1, N2))

        for i in range(0, N1):
            for j in range(0, N2):
                K[i, j] = np.sum((X1[i] - X2[j]) ** 2)

        return np.exp(-K / (2 * sigma**2))
    
    
class LogisticRegressionKernel(Kernel):
    
    def fit(self, y, K, lambda_=0):
        
        def loss_function(u, y, K):
            yKu = y * K.dot(u)

            # function value
            f = np.sum(log_1_plus_exp_safe(-yKu))

            # gradient value
            res = - y / (1. + np.exp(yKu))
            g = K.T.dot(res)

            # add regularization terms
            if lambda_ > 0:
                f += lambda_ / 2. * u.dot(K @ u)
                g += lambda_ / 2. * (K + K.T) @ u 

            return f, g
    
        u = np.zeros(K.shape[1])
        u, loss = solver.gradient_descent(loss_function, u, self.max_evals, 
                                          self.verbose, y, K)
        
        return u
    

class LeastSquaresKernel(Kernel):
    
    def fit(self, y, K, lambda_=0):
        # find u by solving the normal equations
        u = np.linalg.solve(K + lambda_ * np.eye(len(y)), y)
        return u
    
class LeastSquaresGDKernel(Kernel):
    
    def fit(self, y, K, lambda_=0):
        # find u by using GD
        
        def loss_function(u, y, K):
            e = y - K @ u
            f = 1/(2 * len(y)) * np.sum(e ** 2)

            g = - 1 / len(y) * K.T @ e

            # add regularization terms
            if lambda_ > 0:
                f += lambda_ / 2. * u.dot(K @ u)
                g += lambda_ / 2. * (K + K.T) @ u 

            return f, g
    
        u = np.zeros(K.shape[1])
        u, loss = solver.gradient_descent(loss_function, u, self.max_evals, 
                                          self.verbose, y, K)
        
        return u

        