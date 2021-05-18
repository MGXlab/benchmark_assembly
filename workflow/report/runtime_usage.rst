Memory usage over time for sample: {{ snakemake.wildcards.sample }}.
The running assembly process was queried every {{ snakemake.config["ps_interval"] }} seconds 
to obtain the `RSS <https://en.wikipedia.org/wiki/Resident_set_size>`_ value
of the running process.

.. raw:: html

    <embed>
        <a href=runtime_stats/{{ snakemake.wildcards.sample }}_usage.html>
            Click here to open in browser.
        </a>
    </embed>
