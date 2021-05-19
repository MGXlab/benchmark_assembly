`MultiQC <https://multiqc.info/>`_ is used to report stats based on:

FastQC
    Overall raw read quality statistics. This is run manually outside of 
    the pipeline. No trimming/adapter removal is performed for now.

Quast 
    Assembly statistics

Mapping quality
    Based on ``samtools stats`` and ``flagstat``

`Click here to open in browser <results/multiqc_report.html>`_

