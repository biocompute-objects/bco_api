
# BCO API

There is one script for pulling the BCO API from github, cag.sh (Clone API from Github).  You must run the script with the --keep-db or --drop-db flag to keep or drop the existing database, respectively.

# Configuring the server

In the repository folder bco_api are two files, server.conf and tables.conf, which configure the server and the tables available on it, respectively.  The relevant settings in each of these are listed below.

### server.conf

[HOSTNAMES] - Change these to reflect the IP and domain name of your BCO API server.

[HRHOSTNAME] - Change this to reflect the human-readable name of your BCO API server.

### tables.conf

[JSON_OBJECT] - Put the models here that should be available on your server.

[META_TABLE] - Put a meta table for each of the models in [JSON_OBJECT].

# Submitting an object via API 
You need:
- an account,
- the token for your account, and
- the hostname you're sending it to
```javascript
// Create an object.
fetch('https://beta.portal.aws.biochemistry.gwu.edu/api/objects/create/', {
//fetch('http://127.0.0.1:8000/api/objects/create/', {
    method: 'POST',
    body: JSON.stringify({
        POST_create_new_object: [
            {
                contents: {"object_id":"https://w3id.org/biocompute/1.3.0/examples/glycosylation-sites-UniCarbKB","etag":"D231C92C660CD1DD818D412E10F86F07338BA730FBE6898EF8F7DF1B1ECBFD3C","spec_version":"https://w3id.org/biocompute/1.3.0/","provenance_domain":{"name":"glycosylation-sites-UniCarbKB","version":"1.0","review":[{"status":"approved","reviewer_comment":"The dataset has passed the manual and automated QC steps and the readme has also been reviewed","reviewer":{"name":"Rahi Navelkar","affiliation":"The George Washington University","email":"rsn13@gwu.edu","contribution":["curatedBy"]}}],"created":"2018-02-21T14:46:55-5:00","modified":"2018-10-10T11:34:02-5:00","contributors":[{"name":"Matthew Campbell","affiliation":"Institute for Glycomics, Griffith University, Gold Coast, Queensland, Australia","email":"m.campbell2@griffith.edu.au","contribution":["contributedBy"]},{"name":"Rahi Navelkar","affiliation":"The George Washington University","email":"rsn13@gwu.edu","contribution":["curatedBy"]},{"name":"Robel Kahsay","affiliation":"The George Washington University","email":"hadley_king@gwu.edu","contribution":["createdBy"]}],"license":"https://creativecommons.org/licenses/by/4.0/"},"usability_domain":["List of human [taxid:9606] proteins with information on glycosylation sites from UniCarbKB database [https://academic.oup.com/nar/article/42/D1/D215/1052197, https://doi.org/10.1093/nar/gkt1128]"],"extension_domain":{"license":{"data_license":"https://creativecommons.org/licenses/by/4.0/","scripts_license":"https://www.gnu.org/licenses/gpl-3.0.en.html"},"scm_extension":{"scm_repository":"https://github.com/GW-HIVE/glygen-backend-integration/","scm_type":"git","scm_commit":"d34b85553e775dd5452005d786fe6e47d6048ee0","scm_path":"/data/projects/glygen/generated/datasets/reviewed/human_proteoform_glycosylation_sites_unicarbkb_glytoucan.readme.txt"}},"description_domain":{"keywords":["protein","canonical","glycosylation","glycan"],"xref":[{"namespace":"taxonomy","name":"Taxonomy","ids":["9606"],"access_time":"2018-21-02T14:46:55-5:00"}],"platform":["centos7"],"pipeline_steps":[{"step_number":1,"name":"ac2canonical.py","description":"Python script for mapping the UniProtKB accessions in the input file to the UniProtKB canonical accessions ","version":"","input_list":[{"uri":"/human_protein_position_pmid_id_aminoacid_glytoucan_2018_09_04_07_51_27.txt"}],"output_list":[{"uri":"human_protein_position_pmid_id_aminoacid_glytoucan_2018_09_04_07_51_27.txt"}]},{"step_number":2,"name":"make-proteoform_glycosylation_sites_unicarbkb_glytoucan-csv-step2a.py","description":"Python scripts for retrieving glycosylation type or linkage type through UniCarbKB structure webpage ","input_list":[{"uri":"human_protein_position_pmid_id_aminoacid_glytoucan_2018_09_04_07_51_27.txt"}],"output_list":[{"uri":"human_proteoform_glycosylation_sites_unicarbkb_glytoucan.csv"}]},{"step_number":2,"name":"make-proteoform_glycosylation_sites_unicarbkb_glytoucan-csv-step2b.py","description":"Python scripts for retrieving glycosylation type or linkage type through UniCarbKB structure webpage ","input_list":[{"uri":"human_protein_position_pmid_id_aminoacid_glytoucan_2018_09_04_07_51_27.txt"}],"output_list":[{"uri":"human_proteoform_glycosylation_sites_unicarbkb_glytoucan.csv"}]},{"step_number":3,"name":"make-proteoform_glycosylation_sites_unicarbkb_glytoucan-csv-step3.py","description":"Python script for quality check of the processed file. Records which fall under one or more following criteria's are flagged and eliminated and can be accessed using the log file. The elimination steps include -   a. If the protein accession is not included in UniProtKB protein list - UniProtKB Nov-2017 Release   b. If the amino acid position does not match to the amino acid on the associated position on fasta sequence - UniProtKB Nov-2017 Release  c. If the id (UnicarbKB structure id) is not present in input file  d. If the glycosylation type (linkage type) is not retrieved through step 3  e. If a serine or threonine is reported for an N-linked glycan structure  f. If an asparagine is reported for an O-linked glycan structure","input_list":[{"uri":"human_proteoform_glycosylation_sites_unicarbkb_glytoucan.csv"},{"uri":"human_protein_all.fasta"}],"output_list":[{"uri":"human_proteoform_glycosylation_sites_unicarbkb_glytoucan.csv"},{"uri":"human_proteoform_glycosylation_sites_unicarbkb_glytoucan.log"}]}]},"execution_domain":{"script":[{"uri":{"uri":"https://github.com/glygener/glygen-backend-integration/blob/master/integration/ac2canonical.py"}},{"uri":{"uri":"https://github.com/glygener/glygen-backend-integration/blob/master/integration/make-proteoform_glycosylation_sites_unicarbkb_glytoucan-csv-step2a.py"}},{"uri":{"uri":"https://github.com/glygener/glygen-backend-integration/blob/master/integration/make-proteoform_glycosylation_sites_unicarbkb_glytoucan-csv-step2b.py"}},{"uri":{"uri":"https://github.com/glygener/glygen-backend-integration/blob/master/integration/make-proteoform_glycosylation_sites_unicarbkb_glytoucan-csv-step3.py"}}],"script_driver":"manual","software_prerequisites":[{"name":"Python","version":"2.7.13","uri":{"uri":"https://www.python.org/downloads/release/python-2713/","access_time":"2017-01-24T09:40:17-0500","sha1_checksum":"17add4bf0ad0ec2f08e0cae6d205c700"}}],"external_data_endpoints":[{"name":"UniCarbKB","url":"http://www.unicarbkb.org/"},{"name":"access glygen-backend-integration","url":"https://github.com/glygener/glygen-backend-integration"}],"environment_variables":{}},"io_domain":{"input_subdomain":[{"uri":{"filename":"human_protein_position_pmid_id_aminoacid_glytoucan_2018_09_04_07_51_27.txt","uri":"http://data.glygen.org/datasets/source/human_protein_position_pmid_id_aminoacid_glytoucan_2018_09_04_07_51_27.txt","access_time":"2018-10-10T11:34:02-5:00"}},{"uri":{"filename":"human_protein_all.fasta","uri":"http://data.glygen.org/GLYDS00053","access_time":"2018-10-10T11:34:02-5:00"}}],"output_subdomain":[{"mediatype":"csv/text","uri":{"filename":"human_proteoform_glycosylation_sites_unicarbkb_glytoucan.log","uri":"http://data.glygen.org/datasets/logs/human_proteoform_glycosylation_sites_unicarbkb_glytoucan.log","access_time":"2018-10-10T11:37:02-5:00"}},{"mediatype":"csv/text","uri":{"filename":"human_proteoform_glycosylation_sites_unicarbkb_glytoucan.csv","uri":"http://data.glygen.org/GLYDS00040","access_time":"2018-10-10T11:37:02-5:00"}}]},"error_domain":{"empirical_error":{"statistics":[{"comment":"Unique value statistics for the dataset"},{"key":"uniprotkb_canonical_ac","value":92,"description":"Accession assigned to the protein isoform chosen to be the canonical sequence in UniProtKB database"},{"key":"glycosylation_site","value":223,"description":"Site on the protein sequence where glycosylation is observed"},{"key":"evidence","value":163,"description":"NCBI PubMed Id (PMID) as evidence for the entry"},{"key":"unicarbkb_id","value":984,"description":"UnicarbKB data structure identifier"},{"key":"glytoucan_ac","value":824,"description":"Unique accession assigned to the registered glycan structure in GlyTouCan database"},{"key":"amino_acid","value":3,"description":"Three letter code abbreviation of the amino acid"},{"key":"glycosylation_type","value":3,"description":"Type of glycosylation [linkage type]"}]},"algorithmic_error":{}}},
                owner_group: 'bco_drafters',
                schema: 'IEEE',
                state: 'DRAFT',
                table: 'bco_draft',
            }
        ]        
    }),
    headers: {
        "Authorization": "Token 5aa391139deab4eb278d4d439e713f705c23517c",
        "Content-type": "application/json; charset=UTF-8"
    }
    }).then(response=>response.json()).then(data=>{
    console.log(data);
})
```

# Using Docker with BCO API

### Building the BCO API via Docker

A docker file is provided to allow easy building of the BCO API.  This can be done from the root directory (the directory with Dockerfile in it) by running:

`docker build -t bco_api:latest .`

This will build a container named `bco_api` with the tag `latest`.

### Running the container via Docker

The BCO Api container can be run via docker on the command line by running:

`docker run --rm --network host -it bco_api:latest`

This will expose the server at `http://127.0.0.1:8000`.

#### Overriding the port

It is possible to override the port 8000 to whatever port is desired.  This is done by running the container:

`docker run --rm --network host -it bco_api:latest 0.0.0.0:8080`

NOTE: The ip address of 0.0.0.0 is to allow the web serer to properly associate with 127.0.0.1 - if given 127.0.0.1 it will not allow communications outside of the container!

With 8080 representing the desired port.  You can also give it a specific network created with `docker network create` if you wanted to give assigned IP addresses.

