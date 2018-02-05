#################################################################
#################################################################
############### Normalize Dataset
#################################################################
#################################################################

#############################################
########## 1. Load libraries
#############################################
##### 1. General support #####

##### 2. Other libraries #####


#######################################################
#######################################################
########## S1. Dataset Normalization
#######################################################
#######################################################

#############################################
########## 1. VST
#############################################

vst <- function(rawcount_dataframe) {

	# Load packages
	suppressMessages(require(DESeq2))

	# Run VST
	vst_dataframe <- as.data.frame(varianceStabilizingTransformation(as.matrix(rawcount_dataframe)))

	# Return
	return(vst_dataframe)
}

#############################################
########## 2. Quantile Normalization
#############################################

quantile <- function(rawcount_dataframe) {

	# Load packages
	suppressMessages(require(preprocessCore))

	# Run Quantile Normalization
	quantile_dataframe <- as.data.frame(normalize.quantiles(as.matrix(rawcount_dataframe)))
	quantile_dataframe <- log10(quantile_dataframe+1)
	rownames(quantile_dataframe) <- rownames(rawcount_dataframe)
	colnames(quantile_dataframe) <- colnames(rawcount_dataframe)

	# Return
	return(quantile_dataframe)
}
