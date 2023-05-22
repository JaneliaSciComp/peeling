
# urls for cache have more fields and can be chosen as a
# cli option by the user to save retrieved data

base_url = "https://rest.uniprot.org/uniprotkb/search?compressed=true&size=500&format=tsv"
base_fields = "accession"
cached_fields = f"{base_fields},reviewed,id,gene_names,organism_name,cc_subcellular_location"

not_cached_url = f'{base_url}&fields={base_fields}'
cached_url = f'{base_url}&fields={cached_fields}'

cellular_compartments = {
    'cs': {
        "long_name": "cell surface",
        "true_positive": f"{not_cached_url}&query=(((cc_scl_term:SL-0112) OR (cc_scl_term:SL-0243) OR (keyword:KW-0732) OR (cc_scl_term:SL-9906) OR (cc_scl_term:SL-9907)) AND (reviewed:true))",
        "true_positive_cache": f"{cached_url}&query=(((cc_scl_term:SL-0112) OR (cc_scl_term:SL-0243) OR (keyword:KW-0732) OR (cc_scl_term:SL-9906) OR (cc_scl_term:SL-9907)) AND (reviewed:true))",
        "false_positive": f"{not_cached_url}&query=((((cc_scl_term:SL-0091) OR (cc_scl_term:SL-0173) OR (cc_scl_term:SL-0191)) AND (reviewed:true)) NOT (((cc_scl_term:SL-0112) OR (cc_scl_term:SL-0243) OR (keyword:KW-0732) OR (cc_scl_term:SL-9906) OR (cc_scl_term:SL-9907)) AND (reviewed:true)))",
        "false_positive_cache": f"{cached_url}&query=((((cc_scl_term:SL-0091) OR (cc_scl_term:SL-0173) OR (cc_scl_term:SL-0191)) AND (reviewed:true)) NOT (((cc_scl_term:SL-0112) OR (cc_scl_term:SL-0243) OR (keyword:KW-0732) OR (cc_scl_term:SL-9906) OR (cc_scl_term:SL-9907)) AND (reviewed:true)))"
    },
    'mt': {
        "long_name": "mitochondria",
        "true_positive": f"{not_cached_url}&query=((cc_scl_term:SL-0173) AND (reviewed:true))",
        "true_positive_cache": f"{cached_url}&query=((cc_scl_term:SL-0173) AND (reviewed:true))",
        "false_positive": f"{not_cached_url}&query=((((cc_scl_term:SL-0091) OR (cc_scl_term:SL-0191) OR (cc_scl_term:SL-0112) OR (cc_scl_term:SL-0243) OR (keyword:KW-0732) OR (cc_scl_term:SL-9906) OR (cc_scl_term:SL-9907)) AND (reviewed:true)) NOT ((cc_scl_term:SL-0173) AND (reviewed:true)))",
        "false_positive_cache": f"{cached_url}&query=((((cc_scl_term:SL-0091) OR (cc_scl_term:SL-0191) OR (cc_scl_term:SL-0112) OR (cc_scl_term:SL-0243) OR (keyword:KW-0732) OR (cc_scl_term:SL-9906) OR (cc_scl_term:SL-9907)) AND (reviewed:true)) NOT ((cc_scl_term:SL-0173) AND (reviewed:true)))"
    },
    'nu': {
        "long_name": "nucleus",
        "true_positive": f"{not_cached_url}&query=((cc_scl_term:SL-0191) AND (reviewed:true))",
        "true_positive_cache": f"{cached_url}&query=((cc_scl_term:SL-0191) AND (reviewed:true))",
        "false_positive": f"{not_cached_url}&query=((((cc_scl_term:SL-0091) OR (cc_scl_term:SL-0173) OR (cc_scl_term:SL-0112) OR (cc_scl_term:SL-0243) OR (keyword:KW-0732) OR (cc_scl_term:SL-9906) OR (cc_scl_term:SL-9907)) AND (reviewed:true)) NOT ((cc_scl_term:SL-0191) AND (reviewed:true)))",
        "false_positive_cache": f"{cached_url}&query=((((cc_scl_term:SL-0091) OR (cc_scl_term:SL-0173) OR (cc_scl_term:SL-0112) OR (cc_scl_term:SL-0243) OR (keyword:KW-0732) OR (cc_scl_term:SL-9906) OR (cc_scl_term:SL-9907)) AND (reviewed:true)) NOT ((cc_scl_term:SL-0191) AND (reviewed:true)))"
    }
}


