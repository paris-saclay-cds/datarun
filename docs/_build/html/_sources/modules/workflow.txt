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

2- Split data into train and test dataset
-----------------------------------------

If your data match the standard format, you can use:

* a post request to ``<master-host>/runapp/rawdata/split/`` (cf :ref:`requestsDirect`, class runapp.views.SplitTrainTest)  
* the ``post_split`` function in the module test_files.post_api (cf :ref:`requestsModule`)  


If your data do not match the standard format, you can use:

* a post request to ``<master-host>/runapp/rawdata/customsplit/`` (cf :ref:`requestsDirect`, class runapp.views.CustomSplitTrainTest)  
* the ``custom_post_split`` function in the module test_files.post_api (cf :ref:`requestsModule`)  

3- Send submission on cv fold to be trained on datarun
------------------------------------------------------

To send a submission on cv fold, you can use: 

* a post request to ``<master-host>/runapp/submissionfold/`` (cf :ref:`requestsDirect`, class runapp.views.SubmissionFoldList)  
* the ``post_submission_fold`` function in the module test_files.post_api (cf :ref:`requestsModule`)  

4- Get back your predictions
----------------------------

