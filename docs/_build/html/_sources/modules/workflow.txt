.. _workflow:

How to use datarun?
===================

The workflow to use datarun is the following:

1- Send data to datarun
-----------------------

The standard format of a data file excepted by datarun is a csv file whose first row contains the feature and target names, each line corresponds to a data sample.

Here is an example of a standard data file:  
::
    sepal length,sepal width,petal length,petal width,species
    5.1,3.5,1.4,0.2,setosa
    4.9,3.0,1.4,0.2,setosa
    4.7,3.2,1.3,0.2,setosa
    4.6,3.1,1.5,0.2,setosa

If your data match the standard data file, you need to send:
- the name of the data set (for instance if you use databoard, you can use the problem name)
- your data file  
- the name of the target column 
- the workflow elements of the problem related to the dataset (for instance feature_extractor, classifier, ...)


If your data do not match the standard data file, you need to send in addition to above:  

* a python file with three specific functions: ``prepare_data(raw_data_path)``, ``get_train_data(raw_data_path)``, and ``get_test_data(raw_data_path)``. An example of such file is ``test_files/variable_stars/variable_stars_datarun.py``.   
* possibly other data files (if your data are split in different files).  

In both cases, to send you data to datarun, you can use:  

* a post request to ``<master-host>/runapp/rawdata/`` (cf :ref:`requestsDirect`, class runapp.views.RawDataList)  
* the ``post_data`` function in the module test_files.post_api (cf :ref:`requestsModule`)  


**Note for databoard users:**
To send data to datarun and to split data into train and test dataset, you can user the function ``send_data_datarun`` of ``databoard/db_tools.py``, which uses the functions ``post_data`` and ``post_split`` (or ``custom_post_split``) of the module test_files.post_api of datarun.


2- Split data into train and test dataset
-----------------------------------------

If your data match the standard format, you can use:

* a post request to ``<master-host>/runapp/rawdata/split/`` (cf :ref:`requestsDirect`, class runapp.views.SplitTrainTest)  
* the ``post_split`` function in the module test_files.post_api (cf :ref:`requestsModule`)  


If your data do not match the standard format, you can use:

* a post request to ``<master-host>/runapp/rawdata/customsplit/`` (cf :ref:`requestsDirect`, class runapp.views.CustomSplitTrainTest)  
* the ``custom_post_split`` function in the module test_files.post_api (cf :ref:`requestsModule`)  


**Note for databoard users:**
To send data to datarun and to split data into train and test dataset, you can user the function ``send_data_datarun`` of ``databoard/db_tools.py``, which uses the functions ``post_data`` and ``post_split`` (or ``custom_post_split``) of the module test_files.post_api of datarun.


3- Send submission on cv fold to be trained on datarun
------------------------------------------------------

To send a submission on cv fold, you can use: 

* a post request to ``<master-host>/runapp/submissionfold/`` (cf :ref:`requestsDirect`, class runapp.views.SubmissionFoldList)  
* the ``post_submission_fold`` function in the module test_files.post_api (cf :ref:`requestsModule`)  

If the associted submission files have already been sent, you'll need to send:

* the if of the associated submission
* the id of the submission on cv fold  
* the train and test indices of the cv fold. 
  * after compression (with zlib) and base64-encoding if you use a post request  
  * the raw indices if you use the ``post_submission_fold`` function  
* the priority level (``L`` for low or ``H`` for high) of training this submission on cv fold.  
* an indication that you want to force retraining the submission on cv fold even if it already exists (``force="submission_fold"`` instead of ``force=None``).  

If the associated submission files have not been sent, you need to add:  

* the id of the associated data  
* the list of submission files  
* an indication that you want to force resending the submission even if its id already exists (``force="submission"`` instead of ``force=None``).

4- Get back your predictions
----------------------------

If you want to get all predictions that have not been requested, you can use:

* a post request to ``<master-host>/runapp/testpredictions/new/`` (cf :ref:`requestsDirect`, class runapp.views.GetTestPredictionNew)
* the ``get_prediction_new`` function in the module test_files.post_api (cf :ref:`requestsModule`)


If you want to get predictions given a list of submission on cv fold ids, you can use:

* a post request to ``<master-host>/runapp/testpredictions/list/`` (cf :ref:`requestsDirect`, class runapp.views.GetTestPredictionList)
* the ``get_prediction_list`` function in the module test_files.post_api (cf :ref:`requestsModule`)
