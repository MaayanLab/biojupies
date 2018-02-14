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
	rawcount_dataframe <- log10(rawcount_dataframe+1)
	rawcount_dataframe <- rawcount_dataframe/colSums(rawcount_dataframe)
	quantile_dataframe <- as.data.frame(normalize.quantiles(as.matrix(rawcount_dataframe)))
	rownames(quantile_dataframe) <- rownames(rawcount_dataframe)
	colnames(quantile_dataframe) <- colnames(rawcount_dataframe)

	# Add Gene Symbol
	quantile_dataframe$gene_symbol <- rownames(quantile_dataframe)

	# Return
	return(quantile_dataframe)
}

#############################################
########## 3. Combat
#############################################

combat <- function(expression_dataframe, sample_annotation_dataframe, batchColumn, covariateFormula) {
    # Load library
    suppressMessages(require(sva))

    # Get batch
    batch <- sample_annotation_dataframe[,batchColumn]

    # Get covariate, if specified
    if (!is.nan(covariateFormula)) {
        covariateDesign <- model.matrix(as.formula(covariateFormula), data=sample_annotation_dataframe)
    } else {
        covariateDesign <- NULL
    }
    
    # Run Combat
    combatDataframe <- ComBat(dat=expression_dataframe, batch=batch, mod=covariateDesign, par.prior=TRUE, prior.plots=FALSE)

    # Return dataframe
    return(combatDataframe)
}