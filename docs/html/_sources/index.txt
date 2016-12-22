.. datarun documentation master file, created by
   sphinx-quickstart on Mon Apr 11 11:02:37 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Welcome to datarun's documentation!
===================================

Datarun goal is to train and test machine learning models. It is a REST API written in Django.  

The basic workflow is the following (more details can be found in :ref:`workflow`):

1. Data (on which machine learning models are trained and tested) are sent to datarun.  
2. Models and train and test indices of CV fold are send to datarun, which train and test these models on these indices. 
3. The resulting predictions can then be requested. 

In this documentation, we use the following terminology (which corresponds to the database tables, cf :ref:`models`):

* ``RawData`` refers to the data on which machine learning models are trained and tested 
* ``Submission`` refers to a machine learning model   
* ``Submission on cv fold`` / ``SubmissionFold`` refers to a submission and the indices of train and test of a cv fold.  


Datarun is made of a master and datarunners, as represented below:

.. figure:: ../datarun.png
    :width: 600px
    :align: center
    :alt: oups!

Contents:  

.. toctree::
   :maxdepth: 2

   modules/workflow.rst
   modules/models.rst
   modules/views.rst
   modules/deployment.rst
   modules/tests.rst
   modules/migrations.rst
   modules/troubleshooting.rst
 

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

