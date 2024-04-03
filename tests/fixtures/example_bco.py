
from django.conf import settings

hostname = settings.PUBLIC_HOSTNAME
BCO_000000 = {
        "object_id": f"{hostname}/BCO_000000/DRAFT",
        "spec_version": "https://w3id.org/ieee/ieee-2791-schema/2791object.json",
        "etag": "0275321b6011324035289a5624c635ce5490fbdec588aa5f3bcaf63b85369b4a",
        "provenance_domain": {
            "name": "Influenza A reference gene sequences",
            "version": "1.0",
            "created": "2021-12-01T15:20:13.614Z",
            "modified": "2022-06-28T23:10:12.804Z",
            "review": [],
            "contributors": [
                {
                    "contribution": [
                        "createdBy",
                        "authoredBy",
                        "curatedBy",
                        "importedBy",
                        "contributedBy"
                    ],
                    "name": "Stephanie Singleton",
                    "affiliation": "The George Washington University ",
                    "email": "ssingleton@gwu.edu"
                },
                {
                    "contribution": [
                        "createdBy"
                    ],
                    "name": "Jonathon Keeney",
                    "affiliation": "The George Washington University ",
                    "email": "keeneyjg@gwu.edu"
                }
            ],
            "license": "MIT"
        },
        "usability_domain": [
            "Influenza A (A/Puerto Rico/8/1934 H1N1) reference protein coding sequences.",
            "Cross reference to genes was retrieved using mappings present in proteins that were retrieved using UniProt proteome ID (UniProt ID: UP000009255; strain A/Puerto Rico/8/1934 H1N1). This set was chosen based on UniProt curation emphasis and community use. The primary use case for this data set is to visualize how protein annotations related to drug resistance mutations, selection pressure and more map to gene sequences. "
        ],
        "description_domain": {
            "keywords": [
                "Influenza A, Complete Genome, FASTA, Genes"
            ],
            "platform": [],
            "pipeline_steps": [
                {
                    "step_number": 0,
                    "name": "Download files from UniProt",
                    "description": "Download all files associated with the Influenza A reference genome (influenza A, UP000009255) into the ARGOS Dev server Downloads folder. While logged into the server, execute the following commands: wget ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/reference_proteomes/Viruses/UP000009255/*. One of the files acquired through this step and necessary for generating a new data set is 'UP000009255_211044_DNA.fasta.gz'. Then execute 'gunzip *.gz' to unzip all the files in the downloads folder. The file name is then changed to 'UP000009255_211044_DNA.fasta' in the downloads folder.",
                    "prerequisite": [
                        {
                            "name": "UniProt reference page ",
                            "uri": {
                                "uri": "ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/reference_proteomes/Viruses/UP000009255/",
                                "access_time": "2021-12-01T15:20:13.614Z"
                            }
                        }
                    ],
                    "input_list": [
                        {
                            "uri": "ftp://argosdb-vm-dev/data/shared/argosdb/downloads/uniprot/v1.0/influenza_a/UP000009255_211044_DNA.fasta.gz",
                            "filename": "UP000009255_211044_DNA.fasta.gz",
                            "access_time": "2021-12-01T15:20:13.614Z"
                        }
                    ],
                    "output_list": [
                        {
                            "uri": "ftp://argosdb-vm-dev/data/shared/argosdb/downloads/uniprot/v1.0/influenza_a/UP000009255_211044_DNA.fasta",
                            "filename": "UP000009255_211044_DNA.fasta",
                            "access_time": "2021-12-01T15:20:13.614Z"
                        }
                    ],
                    "version": "1.1"
                },
                {
                    "step_number": 0,
                    "name": "Run the recipe created to process this fasta file, review the newly generated dataset, and change the name of the file for clarity",
                    "description": "This step will use a recipe and a python script to generate a new dataset. The recipe tells the python script how and what to construct. This dataset will then be then moved in the 'unreviewed' folder in the dev argosdb server, it will be manually reviewed, and then the name of the file will be changed for clarity and tracking purposes - this is prefered. \\nMake sure you are located in the correct folder to run the script (/software/argosdb/dataset-maker). Use the following command to run the recipe and the python script: ‘python3 make-dataset.py -i recipes/influenza_UP000009255_genome_sequences.json’. Next, go to the ‘unreviewed’ folder to review the newly generated dataset ‘UP000009255_211044_DNA.fasta’. Once reviewed and approved, move the file to the ‘reviewed’ folder. Lastly, once in the ‘reviewed’ folder, change the name of the file to: ‘ influenza_UP000009255_211044_DNA.fasta’",
                    "prerequisite": [
                        {
                            "name": "Dataset-maker python script",
                            "uri": {
                                "uri": "ftp://argosdb-vm-dev/software/argosdb/make-dataset.py",
                                "filename": "make-dataset.py"
                            }
                        },
                        {
                            "name": "Influenza genome FASTA recipe",
                            "uri": {
                                "uri": "ftp://argosdb-vm-dev/data/shared/argosdb/generated/datasets/recipes/Influenza/influenza_UP000009255_genome_sequences.json",
                                "filename": "influenza_UP000009255_genome_sequences.json"
                            }
                        }
                    ],
                    "input_list": [
                        {
                            "uri": "ftp://argosdb-vm-dev/data/shared/argosdb/downloads/uniprot/v1.0/influenza_a/UP000009255_211044_DNA.fasta",
                            "filename": "UP000009255_211044_DNA.fasta",
                            "access_time": "2021-12-01T15:20:13.614Z"
                        }
                    ],
                    "output_list": [
                        {
                            "uri": "ftp://argosdb-vm-dev/data/shared/argosdb/generated/datasets/reviewed/influenza_UP000009255_211044_DNA.fasta",
                            "filename": "influenza_UP000009255_211044_DNA.fasta",
                            "access_time": "2021-12-01T15:20:13.614Z"
                        }
                    ],
                    "version": "1.1"
                }
            ]
        },
        "execution_domain": {
            "script": [
                {
                    "uri": {
                        "uri": "ftp://argosdb-vm-dev/software/argosdb/make-dataset.py",
                        "filename": "make-dataset.py"
                    }
                }
            ],
            "script_driver": "python3",
            "software_prerequisites": [
                {
                    "name": "Python",
                    "version": "3",
                    "uri": {
                        "uri": "https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe",
                        "filename": ""
                    }
                }
            ],
            "external_data_endpoints": [
                {
                    "name": "python-3.10.0",
                    "url": "https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe"
                }
            ],
            "environment_variables": {}
        },
        "io_domain": {
            "input_subdomain": [
                {
                    "uri": {
                        "uri": "http://data.argosdb.org/ln2downloads/uniprot/v1.0/UP000009255_211044_DNA.fasta",
                        "filename": "UP000009255_211044_DNA.fasta"
                    }
                }
            ],
            "output_subdomain": [
                {
                    "mediatype": "text/plain",
                    "uri": {
                        "uri": "http://data.argosdb.org/ln2data/uniprot/v1.0/UP000009255_211044_DNA.fasta",
                        "filename": "UP000009255_211044_DNA.fasta"
                    }
                }
            ]
        },
        "parametric_domain": [],
        "extension_domain": [
            {
                "extension_schema": "http://www.w3id.org/biocompute/extension_domain/1.1.0/dataset/dataset_extension.json",
                "dataset_extension": {
                    "additional_license": {
                        "data_license": "https://creativecommons.org/licenses/by/4.0/",
                        "script_license": "https://www.gnu.org/licenses/gpl-3.0.en.html"
                    },
                    "dataset_categories": [
                        {
                            "category_value": "Influenza A",
                            "category_name": "species"
                        },
                        {
                            "category_value": "nucleotide",
                            "category_name": "molecule"
                        },
                        {
                            "category_value": "Influenza A",
                            "category_name": "tag"
                        },
                        {
                            "category_value": "fasta",
                            "category_name": "file_type"
                        },
                        {
                            "category_value": "reviewed",
                            "category_name": "status"
                        },
                        {
                            "category_value": "internal",
                            "category_name": "scope"
                        }
                    ]
                }
            }
        ]
    }

BCO_000001 = {
        "object_id": f"{hostname}/BCO_000001/DRAFT",
        "spec_version": "https://w3id.org/ieee/ieee-2791-schema/2791object.json",
        "etag": "11ee4c3b8a04ad16dcca19a6f478c0870d3fe668ed6454096ab7165deb1ab8ea",
        "provenance_domain": {
            "name": "HCV1a ledipasvir resistance SNP detection",
            "version": "1.0",
            "created": "2017-01-24T09:40:17-0500",
            "modified": "2022-06-28T23:12:50.369Z",
            "review": [
                {
                    "status": "approved",
                    "reviewer_comment": "Approved by GW staff. Waiting for approval from FDA Reviewer",
                    "date": "2017-11-12T12:30:48-0400",
                    "reviewer": {
                        "name": "Charles Hadley King",
                        "affiliation": "George Washington University",
                        "email": "hadley_king@gwu.edu",
                        "contribution": [
                            "curatedBy"
                        ],
                        "orcid": "https://orcid.org/0000-0003-1409-4549"
                    }
                },
                {
                    "status": "approved",
                    "reviewer_comment": "The revised BCO looks fine",
                    "date": "2017-12-12T12:30:48-0400",
                    "reviewer": {
                        "name": "Eric Donaldson",
                        "affiliation": "FDA",
                        "email": "Eric.Donaldson@fda.hhs.gov",
                        "contribution": [
                            "curatedBy"
                        ]
                    }
                }
            ],
            "contributors": [
                {
                    "name": "Charles Hadley King",
                    "affiliation": "George Washington University",
                    "email": "hadley_king@gwu.edu",
                    "contribution": [
                        "createdBy",
                        "curatedBy"
                    ],
                    "orcid": "https://orcid.org/0000-0003-1409-4549"
                },
                {
                    "name": "Eric Donaldson",
                    "affiliation": "FDA",
                    "email": "Eric.Donaldson@fda.hhs.gov",
                    "contribution": [
                        "authoredBy"
                    ]
                }
            ],
            "license": "https://spdx.org/licenses/CC-BY-4.0.html"
        },
        "usability_domain": [
            "Identify baseline single nucleotide polymorphisms (SNPs)[SO:0000694], (insertions)[SO:0000667], and (deletions)[SO:0000045] that correlate with reduced (ledipasvir)[pubchem.compound:67505836] antiviral drug efficacy in (Hepatitis C virus subtype 1)[taxonomy:31646]",
            "Identify treatment emergent amino acid (substitutions)[SO:1000002] that correlate with antiviral drug treatment failure",
            "Determine whether the treatment emergent amino acid (substitutions)[SO:1000002] identified correlate with treatment failure involving other drugs against the same virus",
            "GitHub CWL example: https://github.com/mr-c/hive-cwl-examples/blob/master/workflow/hive-viral-mutation-detection.cwl#L20"
        ],
        "description_domain": {
            "keywords": [
                "HCV1a",
                "Ledipasvir",
                "antiviral resistance",
                "SNP",
                "amino acid substitutions"
            ],
            "platform": [
                "HIVE"
            ],
            "pipeline_steps": [
                {
                    "step_number": 1,
                    "name": "HIVE-hexagon",
                    "description": "Alignment of reads to a set of references",
                    "version": "1.3",
                    "prerequisite": [
                        {
                            "name": "Hepatitis C virus genotype 1",
                            "uri": {
                                "uri": "http://www.ncbi.nlm.nih.gov/nuccore/22129792",
                                "access_time": "2017-01-24T09:40:17-0500"
                            }
                        },
                        {
                            "name": "Hepatitis C virus type 1b complete genome",
                            "uri": {
                                "uri": "http://www.ncbi.nlm.nih.gov/nuccore/5420376",
                                "access_time": "2017-01-24T09:40:17-0500"
                            }
                        },
                        {
                            "name": "Hepatitis C virus (isolate JFH-1) genomic RNA",
                            "uri": {
                                "uri": "http://www.ncbi.nlm.nih.gov/nuccore/13122261",
                                "access_time": "2017-01-24T09:40:17-0500"
                            }
                        },
                        {
                            "name": "Hepatitis C virus clone J8CF, complete genome",
                            "uri": {
                                "uri": "http://www.ncbi.nlm.nih.gov/nuccore/386646758",
                                "access_time": "2017-01-24T09:40:17-0500"
                            }
                        },
                        {
                            "name": "Hepatitis C virus S52 polyprotein gene",
                            "uri": {
                                "uri": "http://www.ncbi.nlm.nih.gov/nuccore/295311559",
                                "access_time": "2017-01-24T09:40:17-0500"
                            }
                        }
                    ],
                    "input_list": [
                        {
                            "uri": "http://example.com/dna.cgi?cmd=objFile&ids=514683",
                            "access_time": "2017-01-24T09:40:17-0500"
                        },
                        {
                            "uri": "http://example.com/dna.cgi?cmd=objFile&ids=514682",
                            "access_time": "2017-01-24T09:40:17-0500"
                        }
                    ],
                    "output_list": [
                        {
                            "uri": "http://example.com/data/514769/allCount-aligned.csv",
                            "access_time": "2017-01-24T09:40:17-0500"
                        }
                    ]
                },
                {
                    "step_number": 2,
                    "name": "HIVE-heptagon",
                    "description": "variant calling",
                    "version": "1.3",
                    "input_list": [
                        {
                            "uri": "http://example.com/data/514769/dnaAccessionBased.csv",
                            "access_time": "2017-01-24T09:40:17-0500"
                        }
                    ],
                    "output_list": [
                        {
                            "uri": "http://example.com/data/514801/SNPProfile.csv",
                            "access_time": "2017-01-24T09:40:17-0500"
                        },
                        {
                            "uri": "http://example.com/data/14769/allCount-aligned.csv",
                            "access_time": "2017-01-24T09:40:17-0500"
                        }
                    ]
                }
            ]
        },
        "execution_domain": {
            "script": [
                {
                    "uri": {
                        "uri": "https://example.com/workflows/antiviral_resistance_detection_hive.py"
                    }
                }
            ],
            "script_driver": "shell",
            "software_prerequisites": [
                {
                    "name": "HIVE-hexagon",
                    "version": "babajanian.1",
                    "uri": {
                        "uri": "http://example.com/dna.cgi?cmd=dna-hexagon&cmdMode=-",
                        "access_time": "2017-01-24T09:40:17-0500",
                        "sha1_checksum": "d60f506cddac09e9e816531e7905ca1ca6641e3c"
                    }
                },
                {
                    "name": "HIVE-heptagon",
                    "version": "albinoni.2",
                    "uri": {
                        "uri": "http://example.com/dna.cgi?cmd=dna-heptagon&cmdMode=-",
                        "access_time": "2017-01-24T09:40:17-0500"
                    }
                }
            ],
            "external_data_endpoints": [
                {
                    "name": "HIVE",
                    "url": "http://example.com/dna.cgi?cmd=login"
                },
                {
                    "name": "access to e-utils",
                    "url": "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
                }
            ],
            "environment_variables": {
                "HOSTTYPE": "x86_64-linux",
                "EDITOR": "vim"
            }
        },
        "io_domain": {
            "input_subdomain": [
                {
                    "uri": {
                        "filename": "Hepatitis C virus genotype 1",
                        "uri": "http://www.ncbi.nlm.nih.gov/nuccore/22129792",
                        "access_time": "2017-01-24T09:40:17-0500"
                    }
                },
                {
                    "uri": {
                        "filename": "Hepatitis C virus type 1b complete genome",
                        "uri": "http://www.ncbi.nlm.nih.gov/nuccore/5420376",
                        "access_time": "2017-01-24T09:40:17-0500"
                    }
                },
                {
                    "uri": {
                        "filename": "Hepatitis C virus (isolate JFH-1) genomic RNA",
                        "uri": "http://www.ncbi.nlm.nih.gov/nuccore/13122261",
                        "access_time": "2017-01-24T09:40:17-0500"
                    }
                },
                {
                    "uri": {
                        "uri": "http://www.ncbi.nlm.nih.gov/nuccore/386646758",
                        "access_time": "2017-01-24T09:40:17-0500"
                    }
                },
                {
                    "uri": {
                        "filename": "Hepatitis C virus S52 polyprotein gene",
                        "uri": "http://www.ncbi.nlm.nih.gov/nuccore/295311559",
                        "access_time": "2017-01-24T09:40:17-0500"
                    }
                },
                {
                    "uri": {
                        "filename": "HCV1a_drug_resistant_sample0001-01",
                        "uri": "http://example.com/nuc-read/514682",
                        "access_time": "2017-01-24T09:40:17-0500"
                    }
                },
                {
                    "uri": {
                        "filename": "HCV1a_drug_resistant_sample0001-02",
                        "uri": "http://example.com/nuc-read/514683",
                        "access_time": "2017-01-24T09:40:17-0500"
                    }
                }
            ],
            "output_subdomain": [
                {
                    "mediatype": "text/csv",
                    "uri": {
                        "uri": "http://example.com/data/514769/dnaAccessionBased.csv",
                        "access_time": "2017-01-24T09:40:17-0500"
                    }
                },
                {
                    "mediatype": "text/csv",
                    "uri": {
                        "uri": "http://example.com/data/514801/SNPProfile*.csv",
                        "access_time": "2017-01-24T09:40:17-0500"
                    }
                }
            ]
        },
        "parametric_domain": [
            {
                "param": "seed",
                "value": "14",
                "step": "1"
            },
            {
                "param": "minimum_match_len",
                "value": "66",
                "step": "1"
            },
            {
                "param": "divergence_threshold_percent",
                "value": "0.30",
                "step": "1"
            },
            {
                "param": "minimum_coverage",
                "value": "15",
                "step": "2"
            },
            {
                "param": "freq_cutoff",
                "value": "0.10",
                "step": "2"
            }
        ],
        "error_domain": {
            "empirical_error": {
                "false_negative_alignment_hits": "<0.0010",
                "false_discovery": "<0.05"
            },
            "algorithmic_error": {
                "false_positive_mutation_calls_discovery": "<0.00005",
                "false_discovery": "0.005"
            }
        },
        "extension_domain": [
            {
                "extension_schema": "https://raw.githubusercontent.com/biocompute-objects/extension_domain/1.1.0/fhir/fhir_extension.json",
                "fhir_extension": [
                    {
                        "fhir_endpoint": "http://fhirtest.uhn.ca/baseDstu3",
                        "fhir_version": "3",
                        "fhir_resources": [
                            {
                                "fhir_resource": "Sequence",
                                "fhir_id": "21376"
                            },
                            {
                                "fhir_resource": "DiagnosticReport",
                                "fhir_id": "6288583"
                            },
                            {
                                "fhir_resource": "ProcedureRequest",
                                "fhir_id": "25544"
                            },
                            {
                                "fhir_resource": "Observation",
                                "fhir_id": "92440"
                            },
                            {
                                "fhir_resource": "FamilyMemberHistory",
                                "fhir_id": "4588936"
                            }
                        ]
                    }
                ]
            },
            {
                "extension_schema": "https://raw.githubusercontent.com/biocompute-objects/extension_domain/1.1.0/scm/scm_extension.json",
                "scm_extension": {
                    "scm_repository": "https://github.com/example/repo1",
                    "scm_type": "git",
                    "scm_commit": "c9ffea0b60fa3bcf8e138af7c99ca141a6b8fb21",
                    "scm_path": "workflow/hive-viral-mutation-detection.cwl",
                    "scm_preview": "https://github.com/example/repo1/blob/c9ffea0b60fa3bcf8e138af7c99ca141a6b8fb21/workflow/hive-viral-mutation-detection.cwl"
                }
            }
        ]
    }