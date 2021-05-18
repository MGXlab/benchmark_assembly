`MultiQC <https://multiqc.info/>`_ is used to report stats based on 

* FastQC: Overall raw read quality statistics

.. note:: 
   This is run manually outside of the pipeline.
   No trimming is performed

* Quast: Assembly statistics
* Mapping quality 
  * Based on ``samtools stats`` and ``samtools flagstat``

.. raw:: html

    <a href=results/multiqc_report.html>
    Click here to view it
    </a

