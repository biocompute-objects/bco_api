
#!/usr/bin/env python3

"""Test Permissions draft BCO
Tests for Partial failure(300) and invalid token(403)

Gives 300 instead of 200 and 400

"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.test import APITestCase

class PermissionDraftBCOTestCase(TestCase):
    fixtures = ['tests/fixtures/test_data']

    def setUp(self):
        
        self.client = APIClient()
                # Checking if the user 'bco_api_user' already exists
        try:
            self.user = User.objects.get(username='bco_api_user')
        except User.DoesNotExist:
            self.user = User.objects.create_user(username='bco_api_user')

        # Checking if user already has token, if not then creating one
        if not Token.objects.filter(user=self.user).exists():
            self.token = Token.objects.create(user=self.user)
        else:
            self.token = Token.objects.get(user=self.user)

    def test_permission_bco_success(self):
        #Gives 300 instead of 200

        data = {
            "POST_api_objects_drafts_permissions": [
                {
                "object_id": "http://127.0.0.1:8000/BCO_000000/DRAFT",
                "contents": {
				"object_id": "http://127.0.0.1:8000/BCO_000000/DRAFT",
				"spec_version": "https://w3id.org/ieee/ieee-2791-schema/2791object.json",
				"etag": "0275321b6011324035289a5624c635ce5490fbdec588aa5f3bcaf63b85369b4a",
				"provenance_domain": {
					"name": "Influenza A reference gene sequences",
					"version": "1.1",
					"created": "2021-12-01T15:20:13.614Z",
					"modified": "2022-06-28T23:10:12.804Z",
					"review": [

					],
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
					"platform": [

					],
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
					"environment_variables": {
					}
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
				"parametric_domain": [

				],
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
                }
            ]
            }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/objects/drafts/permissions/', data=data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_permission_bco_partial_failure(self):
        data = {
            "POST_api_objects_drafts_permissions": [
                {
                "object_id": "http://127.0.0.1:8000/BCO_000000/DRAFT",
                "contents": {
				"object_id": "http://127.0.0.1:8000/BCO_000000/DRAFT",
				"spec_version": "https://w3id.org/ieee/ieee-2791-schema/2791object.json",
				"etag": "0275321b6011324035289a5624c635ce5490fbdec588aa5f3bcaf63b85369b4a",
				"provenance_domain": {
					"name": "Influenza A reference gene sequences",
					"version": "1.1",
					"created": "2021-12-01T15:20:13.614Z",
					"modified": "2022-06-28T23:10:12.804Z",
					"review": [

					],
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
					"platform": [

					],
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
					"environment_variables": {
					}
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
				"parametric_domain": [

				],
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
                },
                {
                "object_id": "http://127.0.0.1:8000/BCO_1234567/DRAFT",
                "contents": {
                    
                }
                }
            ]
            }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/objects/drafts/permissions/', data=data, format='json')
        self.assertEqual(response.status_code, 300)

    def test_read_bco_bad_request(self):
        ##Gives 300 instead of 400
        data = {
            "POST_api_objects_drafts_permissions": [
                {
                    # Provide invalid or missing data
                "object_id": "Invalid_objectid",
                "contents": {
                    
                }
                }
            ]
            }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/objects/drafts/permissions/', data=data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_read_bco_invalid_token(self):
        data = {
            "POST_api_objects_drafts_permissions": [
                {
                "object_id": "http://127.0.0.1:8000/BCO_000000/DRAFT",
                "contents": {
				"object_id": "http://127.0.0.1:8000/BCO_000000/DRAFT",
				"spec_version": "https://w3id.org/ieee/ieee-2791-schema/2791object.json",
				"etag": "0275321b6011324035289a5624c635ce5490fbdec588aa5f3bcaf63b85369b4a",
				"provenance_domain": {
					"name": "Influenza A reference gene sequences",
					"version": "1.1",
					"created": "2021-12-01T15:20:13.614Z",
					"modified": "2022-06-28T23:10:12.804Z",
					"review": [

					],
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
					"platform": [

					],
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
					"environment_variables": {
					}
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
				"parametric_domain": [

				],
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
                }
            ]
            }
        self.client.credentials(HTTP_AUTHORIZATION='Invalid token')
        response = self.client.post('/api/objects/drafts/permissions/', data=data, format='json')
        self.assertEqual(response.status_code, 403)
