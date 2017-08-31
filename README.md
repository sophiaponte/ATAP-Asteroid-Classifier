# ATAP-Asteroid-Classifier

This project builds and tests several different bayesian asteroid classifiers. All inforamtion and sources used are in the public domain.
The purpose of this project is to be able to predict what meteorite taxonomic type a sample would fall in given its asteroid taxonomic type. 
The asteroid taxonomic type is determined by using the Bus-Demeo taxonomy standard, taking VISIR spectra of an asteroid and running it through 
an online implementation of the classifier found here : http://smass.mit.edu/busdemeoclass.html

The Bus Demeo online classifier returns one or multiple asteroid taxonomies for the spectra submitted, as well as the slope and PC components
for this asteroid. Using the implementation of the Naive-Bayes classifier found here, the Meteorite taxonomy can be inferred. From this meteorite
taxonomy, qualities such as density and composition can later be determined. 

This project contains 11 python files. I will describe what each one does in the list below : 

## analyze_data.py
This file contains the 'main method' that runs all of the other files to collect, scrape, classify, create training files, and runs the Naive
Bayes classifiers on the training files. All of the meteorite data (for the training and test files) is stored in
the variable 'meteorites'. It also contains some other functions to manipulate the data. 

## training_file_converter.py
This file creates training files for the Naive Bayes classifiers implemented. It uses data scraped from the Relab database, the Demeo classifier
implemented by MIT and Metbull. The following files are used to scrape, edit, and organize the data so that it can be used in training and test
files for the classifiers

##### reader_class.py
This file reads meteorite data from the relab catalogues and downloads the spectra files for all of the meteorites to the computer.
These files are saved under spectra_data_unprocessed_new and spectra_data_unprocessed_gaffey

##### run_classifier_class.py
This file runs the classifier on the files in the spectra unprocessed folders. The results are sent to an email account.

##### scraperv2.py
This file is the actual scraper that pushes data to the Bus-Demeo classifier site.

##### scraper_metbull.py
This file scrapes the metbull website to get the meteorite types associated with each name that exists in the Relab database
for the given meteorite's sample id.

##### email_getter_class.py
This file is a scraper that gets all classified data files from the email account they were sent to. It saves these files to the local computer 
in spectra_data_processed_all and spectra_data_processed_new

##### get_names.py
This file gets the names of all the meteorites associated with the sample_ids that they are stored under in Relab, and loads them to the 
meteorite data. 

##### gaffey_data.py
This file scrapes data for Gaffey Data off of the Relab site, classifies the spectra and collects the result files from Email.

## processed_data_load.py
This file creates the meteorite objects from consolodating all of the dicts containing information we have scraped from Relab, Metbull, or the MIT 
classifier site. Each meteorite object has a list of properties containing all the important data.

## naive_bayes_type_v_class.py
This file is a class for the implementation of a Naive Bayes classifier. The training data input must be in the form of 
(Asteroid tax type__Met tax type) for each line. 

## naive_bayes_pca_vs_type.py
This file is a class for an implementation of a Naive Bayes classifier running on PC space. This means that the training data contains 6
features (PC1, PC2, PC3, PC4, PC5 and slope) for each meteorite taxonomic type. The likelihood in the Naive Bayes calculation is 
calculated by a succession of Kernel density estimates for the new PC component against the ones in the training set. The training set data must be in the form of (PC1__PC2__PC3__PC4__PC5__slope__Met tax type) for each line.
