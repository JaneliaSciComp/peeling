from datamanagement.uniprotcommunicator import UniProtCommunicator


class CliUniProtCommunicator(UniProtCommunicator):
    
    # overriding abstract method
    def get_latest_id(self, old_ids):
        return self._retrieve_latest_id(old_ids)
    
    # overriding abstract method
    def get_annotation_surface(self):
        return self._retrieve_annotation_surface()
    
    # overriding abstract method
    def get_annotation_cyto(self):
        return self._retrieve_annotation_cyto()
