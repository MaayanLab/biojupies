# Load packages
library(pheatmap)
library(RColorBrewer)

# Change directory
setwd('/Users/denis/Documents/Projects/jupyter-notebook/notebook-generator/case-study')

# Set infile
infile = 's4-correlation.dir/signature-correlation.txt'

# Read correlation file
correlation_dataframe <- read.table(infile, header=TRUE)
rownames(correlation_dataframe) <- correlation_dataframe[,1]
correlation_dataframe[,1] <- NULL
diag(correlation_dataframe) <- 0
head(correlation_dataframe)

# Pheatmap
pheatmap(correlation_dataframe,
         color = colorRampPalette(rev(brewer.pal(n = 7, name ="RdBu")))(100),
         show_rownames = FALSE,
         show_colnames = FALSE,
         border_color = NA,
         cutree_rows = 3,
         cutree_cols = 3)

