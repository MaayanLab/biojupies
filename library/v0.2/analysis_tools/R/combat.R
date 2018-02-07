#################################################################
#################################################################
############### DE 
#################################################################
#################################################################

#############################################
########## 1. Load libraries
#############################################
##### 1. General support #####


##### 2. Other libraries #####


#######################################################
#######################################################
########## S1. Function
#######################################################
#######################################################

#############################################
########## 1. Run
#############################################

combat <- function(expression_dataframe, sample_annotation_dataframe, covariateFormula=NULL, batchColumn='batch') {
	
    # Load library
    require(sva)

    # Get batch
    batch <- sample_annotation_dataframe[,batchColumn]

    # Get covariate, if specified
    if (!is.null(covariateFormula)) {
        covariateDesign <- model.matrix(as.formula(covariateFormula), data=sample_annotation_dataframe)
    } else {
        covariateDesign <- NULL
    }
    
    # Run Combat
    combatDataframe <- ComBat(dat=expression_dataframe, batch=batch, mod=covariateDesign, par.prior=TRUE, prior.plots=FALSE)

    # Return dataframe
    return(combatDataframe)
}